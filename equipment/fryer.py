import logging
from equipment.base import BaseEquipment

logger = logging.getLogger(__name__)

# Limiti specifici per l'olio di frittura
FRYER_MIN_SETPOINT_C = 100.0
FRYER_MAX_SETPOINT_C = 190.0
FRYER_MAX_OIL_TEMP_C = 250.0
FRYER_THERMOSTAT_HYSTERESIS = 1.0  # Più stretta per l'olio


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
            # Parametri termici specifici
            thermal_mass_kj_per_c=thermal_mass_kj_per_c,
            heat_loss_factor_kw_per_c=0.025,  # dispersione olio
            ambient_temperature_c=20.0,
            heating_efficiency=0.90,
            max_temperature_c=FRYER_MAX_OIL_TEMP_C,
        )

        # Specifiche friggitrice
        self.oil_capacity_l = float(oil_capacity_l)
        self.basket_count = int(basket_count)

        # Stato specifico
        self.is_heating = False

        # Setpoint di default per la friggitrice
        self.set_target_temperature(180.0)

    # =========================================================
    # COMANDI SPECIFICI
    # =========================================================
    def set_temperature(self, temperature_c: float):
        """Imposta la temperatura target dell'olio (100-190°C)."""
        clamped = max(FRYER_MIN_SETPOINT_C, min(temperature_c, FRYER_MAX_SETPOINT_C))
        self.set_target_temperature(clamped)
        if clamped != temperature_c:
            logger.info(
                f"{self.equipment_id}: setpoint clamped a {clamped}°C"
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
        """Aggiorna stato friggitrice."""
        if dt_seconds <= 0:
            return

        if not self.is_on:
            self.is_heating = False
            self.set_power(0.0)
            self.update_electrical(dt_seconds)
            return

        # Logica termostato specifica per friggitrice (isteresi 1°C)
        if self.target_temperature_c is not None:
            error = self.target_temperature_c - self.temperature_c
            if error > FRYER_THERMOSTAT_HYSTERESIS:
                self.is_heating = True
                self.set_power(self.nominal_power_kw)
            elif error < -FRYER_THERMOSTAT_HYSTERESIS:
                self.is_heating = False
                self.set_power(0.0)

        # Aggiorna termico + elettrico (delegato alla base)
        self.update_thermal(dt_seconds)
        self.update_electrical(dt_seconds)

    # =========================================================
    # DATI
    # =========================================================
    def get_thermal_data(self) -> dict:
        """Dati termici specifici della friggitrice."""
        return {
            "oil_temperature": self.temperature_c,
            "temperature_setpoint": self.target_temperature_c,
            "is_heating": self.is_heating,
            "is_on": self.is_on,
            "oil_capacity_l": self.oil_capacity_l,
            "basket_count": self.basket_count,
        }

    def get_data(self) -> dict:
        """Dati completi (retrocompatibile con il vecchio codice)."""
        data = self.get_electrical_data()
        data.update(self.get_thermal_data())
        data.update({
            "equipment_id": self.equipment_id,
            "manufacturer": self.manufacturer,
            "model": self.model,
        })
        return data