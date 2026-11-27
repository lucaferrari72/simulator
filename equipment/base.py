
"""Modulo base per le apparecchiature del simulatore."""

import logging
import math

logger = logging.getLogger(__name__)


class BaseEquipment:
    """Classe base per tutte le apparecchiature di cucina.

    Gestisce:
    - Stato elettrico
    - Potenza attiva
    - Corrente per fase
    - Energia consumata
    - Comportamento termico
    - Termostato
    - Allarmi

    Convenzione temporale:
    la potenza presente all'inizio del tick viene contabilizzata
    per l'intero intervallo; il termostato determina la potenza
    del tick successivo.
    """

    OVERCURRENT_FACTOR = 1.10
    TEMP_TOLERANCE_ALARM = 20.0
    THERMOSTAT_HYSTERESIS = 2.0

    def __init__(
        self,
        equipment_id: str,
        manufacturer: str,
        model: str,
        nominal_power_kw: float,
        voltage_v: float,
        phases: int = 3,
        frequency_hz: int = 60,
        thermal_mass_kj_per_c: float = 0.0,
        heat_loss_factor_kw_per_c: float = 0.0,
        ambient_temperature_c: float = 20.0,
        heating_efficiency: float = 1.0,
        max_temperature_c: float = float("inf"),
        power_factor: float = 1.0,
    ):
        # Validazione parametri elettrici
        nominal_power_kw = float(nominal_power_kw)
        voltage_v = float(voltage_v)
        power_factor = float(power_factor)

        if not math.isfinite(nominal_power_kw) or nominal_power_kw < 0:
            raise ValueError("Potenza nominale non valida")

        if not math.isfinite(voltage_v) or voltage_v <= 0:
            raise ValueError("Tensione non valida")

        if phases not in (1, 3):
            raise ValueError("Sono supportate solo 1 o 3 fasi")

        if not math.isfinite(power_factor) or not 0 < power_factor <= 1:
            raise ValueError("Il fattore di potenza deve essere tra 0 e 1")

        if frequency_hz <= 0:
            raise ValueError("Frequenza non valida")

        # Identificazione
        self.equipment_id = equipment_id
        self.manufacturer = manufacturer
        self.model = model

        # Specifiche elettriche
        self.nominal_power_kw = nominal_power_kw
        self.voltage_v = voltage_v
        self.phases = int(phases)
        self.frequency_hz = int(frequency_hz)
        self.power_factor = power_factor

        # Stato elettrico
        self.is_on = False
        self.power_kw = 0.0
        self.energy_kwh = 0.0

        self.current_l1_a = 0.0
        self.current_l2_a = 0.0
        self.current_l3_a = 0.0

        # Stato termico
        self.thermal_mass_kj_per_c = float(thermal_mass_kj_per_c)
        self.heat_loss_factor_kw_per_c = float(
            heat_loss_factor_kw_per_c
        )
        self.ambient_temperature_c = float(ambient_temperature_c)
        self.temperature_c = self.ambient_temperature_c
        self.target_temperature_c = None

        # Allarmi e parametri termici
        self.alarm = False
        self.alarm_reason = None

        self.heating_efficiency = max(
            0.0, min(1.0, float(heating_efficiency))
        )
        self.max_temperature_c = float(max_temperature_c)

    # =========================================================
    # COMANDI BASE
    # =========================================================

    def turn_on(self):
        """Accende l'apparecchiatura."""
        self.is_on = True

    def turn_off(self):
        """Spegne l'apparecchiatura."""
        self.is_on = False
        self.power_kw = 0.0
        self._reset_currents()

    def set_power(self, power_kw: float):
        """Imposta la potenza attiva in kW.

        La potenza è limitata alla potenza nominale del singolo
        apparecchio. Non viene applicato alcun limite alla somma
        dei carichi della cucina.
        """
        power_kw = float(power_kw)

        if not math.isfinite(power_kw):
            raise ValueError("Potenza richiesta non valida")

        if not self.is_on:
            self.power_kw = 0.0
            return

        self.power_kw = max(
            0.0,
            min(power_kw, self.nominal_power_kw)
        )

    def set_target_temperature(self, temperature_c: float):
        """Imposta la temperatura target."""
        temperature_c = float(temperature_c)

        if not math.isfinite(temperature_c):
            raise ValueError("Temperatura target non valida")

        self.target_temperature_c = temperature_c

    def reset_energy(self):
        """Azzera il contatore energetico."""
        self.energy_kwh = 0.0

    def reset_alarm(self):
        """Azzera gli allarmi."""
        self.alarm = False
        self.alarm_reason = None

    # =========================================================
    # AGGIORNAMENTO TEMPORALE
    # =========================================================

    def update(self, dt_seconds: float):
        """Aggiorna l'apparecchiatura per l'intervallo indicato.

        La potenza iniziale viene utilizzata per il calcolo
        dell'energia e dell'evoluzione termica.

        La corrente viene aggiornata sulla base della nuova
        potenza determinata dal termostato.
        """
        dt_seconds = float(dt_seconds)

        if not math.isfinite(dt_seconds) or dt_seconds <= 0:
            return

        # Potenza effettiva durante l'intervallo trascorso
        interval_power_kw = self.power_kw

        # Evoluzione termica e aggiornamento termostato
        self.update_thermal(dt_seconds)

        # Energia del tick: usa la potenza applicata
        # durante l'intervallo, non quella del tick successivo.
        self.energy_kwh += (
            interval_power_kw * dt_seconds / 3600.0
        )

        # Corrente coerente con la potenza al termine del tick
        self._update_currents()

        self._check_alarms()

    def update_electrical(self, dt_seconds: float):
        """Aggiorna corrente ed energia elettrica.

        Metodo mantenuto per compatibilità con eventuali
        chiamate esterne alla classe base.
        """
        dt_seconds = float(dt_seconds)

        if not math.isfinite(dt_seconds) or dt_seconds <= 0:
            return

        self.energy_kwh += self.power_kw * dt_seconds / 3600.0
        self._update_currents()

    def _update_currents(self):
        """Calcola le correnti a partire dalla potenza attiva."""

        if not self.is_on or self.power_kw <= 0:
            self._reset_currents()
            return

        if self.phases == 3:
            # Tensione concatenata trifase
            current = (
                self.power_kw * 1000.0
                / (
                    math.sqrt(3.0)
                    * self.voltage_v
                    * self.power_factor
                )
            )

            self.current_l1_a = current
            self.current_l2_a = current
            self.current_l3_a = current

        elif self.phases == 1:
            current = (
                self.power_kw * 1000.0
                / (self.voltage_v * self.power_factor)
            )

            self.current_l1_a = current
            self.current_l2_a = 0.0
            self.current_l3_a = 0.0

    def _reset_currents(self):
        self.current_l1_a = 0.0
        self.current_l2_a = 0.0
        self.current_l3_a = 0.0

    # =========================================================
    # AGGIORNAMENTO TERMICO
    # =========================================================

    def update_thermal(self, dt_seconds: float):
        """Aggiorna temperatura, dispersioni e termostato."""

        if self.thermal_mass_kj_per_c <= 0:
            return

        heat_input_kj = (
            self.power_kw
            * self.heating_efficiency
            * dt_seconds
        )

        delta_t = (
            self.temperature_c - self.ambient_temperature_c
        )

        heat_loss_kj = (
            self.heat_loss_factor_kw_per_c
            * delta_t
            * dt_seconds
        )

        delta_temp = (
            heat_input_kj - heat_loss_kj
        ) / self.thermal_mass_kj_per_c

        self.temperature_c += delta_temp

        self.temperature_c = max(
            self.ambient_temperature_c,
            min(self.temperature_c, self.max_temperature_c)
        )

        self._apply_thermostat()

    def _apply_thermostat(self):
        """Termostato con isteresi."""

        if self.target_temperature_c is None or not self.is_on:
            return

        error = self.target_temperature_c - self.temperature_c
        h = self.THERMOSTAT_HYSTERESIS

        if error > h:
            self.set_power(self.nominal_power_kw)

        elif error < -h:
            self.set_power(0.0)

    # =========================================================
    # ALLARMI
    # =========================================================

    def _check_alarms(self):
        """Controlla sovracorrente e temperatura."""

        if self.phases == 3:
            nominal_current = (
                self.nominal_power_kw * 1000.0
                / (
                    math.sqrt(3.0)
                    * self.voltage_v
                    * self.power_factor
                )
            )
        else:
            nominal_current = (
                self.nominal_power_kw * 1000.0
                / (self.voltage_v * self.power_factor)
            )

        max_current = nominal_current * self.OVERCURRENT_FACTOR

        if max(
            self.current_l1_a,
            self.current_l2_a,
            self.current_l3_a
        ) > max_current:
            self._set_alarm("SOVRACORRENTE")
            return

        if self.target_temperature_c is not None:
            if (
                abs(
                    self.temperature_c
                    - self.target_temperature_c
                ) > self.TEMP_TOLERANCE_ALARM
            ):
                self._set_alarm("TEMPERATURA FUORI RANGE")
                return

        self.alarm = False
        self.alarm_reason = None

    def _set_alarm(self, reason: str):
        if not self.alarm:
            logger.warning(
                f"ALLARME {self.equipment_id}: {reason}"
            )

        self.alarm = True
        self.alarm_reason = reason

    # =========================================================
    # DATI
    # =========================================================

    def get_electrical_data(self) -> dict:
        """Restituisce i dati elettrici e termici."""

        return {
            "equipment_id": self.equipment_id,
            "manufacturer": self.manufacturer,
            "model": self.model,

            "voltage_v": self.voltage_v,
            "frequency_hz": self.frequency_hz,
            "phases": self.phases,
            "power_factor": self.power_factor,

            "nominal_power_kw": self.nominal_power_kw,
            "power_kw": self.power_kw,
            "energy_kwh": self.energy_kwh,

            "current_l1_a": self.current_l1_a,
            "current_l2_a": self.current_l2_a,
            "current_l3_a": self.current_l3_a,

            "is_on": self.is_on,

            "temperature_c": self.temperature_c,
            "target_temperature_c": self.target_temperature_c,
            "ambient_temperature_c": self.ambient_temperature_c,

            "alarm": self.alarm,
            "alarm_reason": self.alarm_reason,

            "heating_efficiency": self.heating_efficiency,
            "max_temperature_c": self.max_temperature_c,
        }
