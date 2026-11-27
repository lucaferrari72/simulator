
import logging
import math

from equipment.base import BaseEquipment

logger = logging.getLogger(__name__)

# Limiti specifici per l'olio di frittura
FRYER_MIN_SETPOINT_C = 100.0
FRYER_MAX_SETPOINT_C = 190.0
FRYER_MAX_OIL_TEMP_C = 250.0
FRYER_THERMOSTAT_HYSTERESIS = 1.0


class Fryer(BaseEquipment):
    """Friggitrice con controllo termostatico dell'olio."""

    def __init__(
        self,
        equipment_id: str,
        model: str,
        nominal_power_kw: float,
        oil_capacity_l: float,
        voltage_v: float = 440,
        basket_count: int = 2,
        thermal_mass_kj_per_c: float = 180.0,
    ):
        super().__init__(
            equipment_id=equipment_id,
            manufacturer="Ambach",
            model=model,
            nominal_power_kw=nominal_power_kw,
            voltage_v=voltage_v,
            phases=3,
            frequency_hz=60,
            thermal_mass_kj_per_c=thermal_mass_kj_per_c,
            heat_loss_factor_kw_per_c=0.025,
            ambient_temperature_c=20.0,
            heating_efficiency=0.90,
            max_temperature_c=FRYER_MAX_OIL_TEMP_C,
        )

        self.oil_capacity_l = float(oil_capacity_l)
        self.basket_count = int(basket_count)

        self.is_heating = False

        self.set_target_temperature(180.0)

    # =========================================================
    # COMANDI
    # =========================================================

    def set_temperature(self, temperature_c: float):
        """Imposta la temperatura target dell'olio."""

        temperature_c = float(temperature_c)

        if not math.isfinite(temperature_c):
            raise ValueError("Temperatura non valida")

        clamped = max(
            FRYER_MIN_SETPOINT_C,
            min(temperature_c, FRYER_MAX_SETPOINT_C)
        )

        self.set_target_temperature(clamped)

        if clamped != temperature_c:
            logger.info(
                "%s: setpoint impostato a %.1f °C",
                self.equipment_id,
                clamped
            )

    def turn_on(self):
        super().turn_on()

    def turn_off(self):
        super().turn_off()
        self.is_heating = False

    # =========================================================
    # AGGIORNAMENTO
    # =========================================================

    def update(self, dt_seconds: float):
        """Aggiorna temperatura, potenza ed energia."""

        dt_seconds = float(dt_seconds)

        if not math.isfinite(dt_seconds) or dt_seconds <= 0:
            return

        # Potenza effettivamente applicata
        # durante l'intervallo appena trascorso.
        interval_power_kw = self.power_kw

        if not self.is_on:
            self.is_heating = False
            self.set_power(0.0)

            self.energy_kwh += (
                interval_power_kw * dt_seconds / 3600.0
            )

            self._update_currents()
            self._check_alarms()
            return

        # =====================================================
        # CONTROLLO TERMOSTATICO
        # =====================================================

        # L'evoluzione termica utilizza la potenza
        # presente all'inizio dell'intervallo.
        self.update_thermal(dt_seconds)

        # update_thermal aggiorna anche il termostato
        # e determina la potenza del tick successivo.
        if self.target_temperature_c is not None:
            error = (
                self.target_temperature_c - self.temperature_c
            )

            self.is_heating = (
                error > -FRYER_THERMOSTAT_HYSTERESIS
                and self.power_kw > 0
            )

        # =====================================================
        # CONTABILIZZAZIONE ELETTRICA
        # =====================================================

        # L'energia deve utilizzare la potenza
        # realmente applicata durante l'intervallo.
        self.energy_kwh += (
            interval_power_kw * dt_seconds / 3600.0
        )

        self._update_currents()
        self._check_alarms()

    # =========================================================
    # DATI
    # =========================================================

    def get_thermal_data(self) -> dict:
        return {
            "oil_temperature": self.temperature_c,
            "temperature_setpoint": self.target_temperature_c,
            "is_heating": self.is_heating,
            "is_on": self.is_on,
            "oil_capacity_l": self.oil_capacity_l,
            "basket_count": self.basket_count,
        }

    def get_data(self) -> dict:
        """Restituisce dati elettrici e termici."""

        data = self.get_electrical_data()
        data.update(self.get_thermal_data())

        data.update({
            "equipment_id": self.equipment_id,
            "manufacturer": self.manufacturer,
            "model": self.model,
        })

        return data
