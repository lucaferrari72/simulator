"""Modulo base per le apparecchiature del simulatore."""
import logging

logger = logging.getLogger(__name__)


class BaseEquipment:
    """Classe base per tutte le apparecchiature di cucina.

    Gestisce stato elettrico (corrente, potenza, energia) e termico
    (temperatura, inerzia, dispersioni, termostato).
    """

    # Soglie di allarme (valori di default)
    OVERCURRENT_FACTOR = 1.10       # 110% della corrente nominale
    TEMP_TOLERANCE_ALARM = 20.0     # °C di scostamento prima dell'allarme
    THERMOSTAT_HYSTERESIS = 2.0     # °C di banda morta del termostato

    def __init__(
        self,
        equipment_id: str,
        manufacturer: str,
        model: str,
        nominal_power_kw: float,
        voltage_v: float,
        phases: int = 3,
        frequency_hz: int = 60,
        # Parametri termici (opzionali)
        thermal_mass_kj_per_c: float = 0.0,
        heat_loss_factor_kw_per_c: float = 0.0,
        ambient_temperature_c: float = 20.0,
        heating_efficiency: float = 1.0,
        max_temperature_c: float = float("inf"),
    ):
        # Identificazione
        self.equipment_id = equipment_id
        self.manufacturer = manufacturer
        self.model = model

        # Specifiche elettriche
        self.nominal_power_kw = float(nominal_power_kw)
        self.voltage_v = float(voltage_v)
        self.phases = int(phases)
        self.frequency_hz = int(frequency_hz)

        # Stato elettrico
        self.is_on = False
        self.power_kw = 0.0
        self.energy_kwh = 0.0
        self.current_l1_a = 0.0
        self.current_l2_a = 0.0
        self.current_l3_a = 0.0

        # Stato termico
        self.thermal_mass_kj_per_c = float(thermal_mass_kj_per_c)
        self.heat_loss_factor_kw_per_c = float(heat_loss_factor_kw_per_c)
        self.ambient_temperature_c = float(ambient_temperature_c)
        self.temperature_c = float(ambient_temperature_c)
        self.target_temperature_c = None  # None = termostato disabilitato

        # Allarmi
        self.alarm = False
        self.alarm_reason = None

        self.heating_efficiency = max(0.0, min(1.0, float(heating_efficiency)))
        self.max_temperature_c = float(max_temperature_c)

    # =========================================================
    # COMANDI BASE
    # =========================================================
    def turn_on(self):
        """Accende l'apparecchiatura."""
        self.is_on = True

    def turn_off(self):
        """Spegne l'apparecchiatura e azzera potenza/corrente."""
        self.is_on = False
        self.power_kw = 0.0
        self.current_l1_a = 0.0
        self.current_l2_a = 0.0
        self.current_l3_a = 0.0

    def set_power(self, power_kw: float):
        """Imposta la potenza attiva (clamped tra 0 e nominale)."""
        if not self.is_on:
            self.power_kw = 0.0
            return
        self.power_kw = max(0.0, min(power_kw, self.nominal_power_kw))

    def set_target_temperature(self, temperature_c: float):
        """Imposta la temperatura target per il termostato."""
        self.target_temperature_c = float(temperature_c)

    def reset_energy(self):
        """Resetta il contatore di energia consumata."""
        self.energy_kwh = 0.0

    def reset_alarm(self):
        """Resetta manualmente lo stato di allarme."""
        self.alarm = False
        self.alarm_reason = None

    # =========================================================
    # AGGIORNAMENTO (chiamato dal manager ad ogni tick)
    # =========================================================
    def update(self, dt_seconds: float):
        """Aggiorna lo stato completo dell'apparecchiatura.

        Questo è il metodo principale chiamato da EquipmentManager.update_all().
        """
        if dt_seconds <= 0:
            return

        self.update_electrical(dt_seconds)
        self.update_thermal(dt_seconds)
        self._check_alarms()

    def update_electrical(self, dt_seconds: float):
        """Aggiorna corrente e accumulo energia."""
        # Calcolo corrente in base alle fasi
        if self.phases == 3:
            current = (self.power_kw * 1000) / (3 ** 0.5 * self.voltage_v)
            self.current_l1_a = current
            self.current_l2_a = current
            self.current_l3_a = current
        elif self.phases == 1:
            current = (self.power_kw * 1000) / self.voltage_v
            self.current_l1_a = current
            self.current_l2_a = 0.0
            self.current_l3_a = 0.0
        else:
            logger.warning(
                f"{self.equipment_id}: fasi non supportate ({self.phases})"
            )

        # Accumulo energia (kWh)
        self.energy_kwh += self.power_kw * dt_seconds / 3600


    def update_thermal(self, dt_seconds: float):
        """Aggiorna temperatura basata su potenza, inerzia e dispersioni."""
        if self.thermal_mass_kj_per_c <= 0:
            return

        # Apporto termico dalla potenza attiva (kJ) - con efficienza
        heat_input_kj = self.power_kw * self.heating_efficiency * dt_seconds

        # Dispersioni termiche verso l'ambiente (kJ)
        delta_t = self.temperature_c - self.ambient_temperature_c
        heat_loss_kj = self.heat_loss_factor_kw_per_c * delta_t * dt_seconds

        # Variazione di temperatura
        delta_temp = (heat_input_kj - heat_loss_kj) / self.thermal_mass_kj_per_c
        self.temperature_c += delta_temp

        # Limiti fisici
        self.temperature_c = max(
            self.ambient_temperature_c,
            min(self.temperature_c, self.max_temperature_c)
        )

        # Termostato con isteresi
        self._apply_thermostat()

    
    def _apply_thermostat(self):
        """Applica la logica del termostato con banda morta."""
        if self.target_temperature_c is None or not self.is_on:
            return
        
        error = self.target_temperature_c - self.temperature_c
        h = self.THERMOSTAT_HYSTERESIS
        
        if error > h:
            self.power_kw = self.nominal_power_kw
        elif error < -h:
            self.power_kw = 0.0

    # =========================================================
    # ALLARMI
    # =========================================================
    def _check_alarms(self):
        """Rileva condizioni di allarme e aggiorna self.alarm."""
        # Sovracorrente su qualsiasi fase
        max_current = (
            self.nominal_power_kw * 1000 / (3 ** 0.5 * self.voltage_v)
            * self.OVERCURRENT_FACTOR
        )
        if max(self.current_l1_a, self.current_l2_a, self.current_l3_a) > max_current:
            self._set_alarm("SOVRACORRENTE")
            return

        # Temperatura fuori range (solo se c'è un target configurato)
        if self.target_temperature_c is not None:
            if abs(self.temperature_c - self.target_temperature_c) > self.TEMP_TOLERANCE_ALARM:
                self._set_alarm("TEMPERATURA FUORI RANGE")
                return

        # Nessun allarme attivo
        self.alarm = False
        self.alarm_reason = None

    def _set_alarm(self, reason: str):
        if not self.alarm:
            logger.warning(f"ALLARME {self.equipment_id}: {reason}")
        self.alarm = True
        self.alarm_reason = reason

    # =========================================================
    # DATI
    # =========================================================
    def get_electrical_data(self) -> dict:
        """Restituisce tutti i dati dell'apparecchiatura."""
        return {
            # Elettrico
            "voltage_v": self.voltage_v,
            "frequency_hz": self.frequency_hz,
            "power_kw": self.power_kw,
            "energy_kwh": self.energy_kwh,
            "current_l1_a": self.current_l1_a,
            "current_l2_a": self.current_l2_a,
            "current_l3_a": self.current_l3_a,
            "is_on": self.is_on,
            # Termico
            "temperature_c": self.temperature_c,
            "target_temperature_c": self.target_temperature_c,
            "ambient_temperature_c": self.ambient_temperature_c,
            # Allarmi
            "alarm": self.alarm,
            "alarm_reason": self.alarm_reason,
            "heating_efficiency": self.heating_efficiency,
            "max_temperature_c": self.max_temperature_c,
        }