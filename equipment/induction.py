
import math

from equipment.base import BaseEquipment


class InductionCooktop(BaseEquipment):

    def __init__(
        self,
        equipment_id="44458",
        model="INSTINCT HOB 3.5",
        nominal_power_kw=3.5,
        voltage_v=220
    ):
        super().__init__(
            equipment_id=equipment_id,
            manufacturer="Garland",
            model=model,
            nominal_power_kw=nominal_power_kw,
            voltage_v=voltage_v,
            phases=1,
            frequency_hz=60
        )

        # CONTROLLO POTENZA
        self.power_level = 0
        self.min_power_kw = 0.875
        self.max_power_kw = 3.5

        # PENTOLA
        self.pan_present = True
        self.pan_temperature = 20.0
        self.pan_mass_kg = 10.0

        # MODELLO TERMICO
        self.thermal_mass = 45.0
        self.ambient_temperature = 20.0
        self.thermal_loss_coefficient = 0.015
        self.heating_efficiency = 0.90

        self.is_heating = False

    def set_level(self, level):
        if not isinstance(level, int) or isinstance(level, bool):
            raise ValueError("Il livello deve essere un numero intero")

        if not 0 <= level <= 12:
            raise ValueError("Il livello deve essere compreso tra 0 e 12")

        self.power_level = level

        if level == 0:
            self.set_power(0.0)

    def set_pan_present(self, present):
        self.pan_present = bool(present)

    def turn_on(self):
        super().turn_on()

    def turn_off(self):
        super().turn_off()
        self.power_level = 0
        self.is_heating = False

    def get_selected_power(self):
        if self.power_level == 0:
            return 0.0

        step = (
            self.max_power_kw - self.min_power_kw
        ) / 11

        return (
            self.min_power_kw
            + (self.power_level - 1) * step
        )

    def update(self, dt_seconds):
        try:
            dt_seconds = float(dt_seconds)
        except (TypeError, ValueError):
            raise ValueError("Intervallo temporale non valido")

        if not math.isfinite(dt_seconds) or dt_seconds <= 0:
            raise ValueError("Intervallo temporale non valido")

        if not self.is_on or not self.pan_present:
            self.is_heating = False
            self.set_power(0.0)
            self.update_electrical(dt_seconds)
            return

        selected_power = self.get_selected_power()

        self.set_power(selected_power)

        self.is_heating = self.power_kw > 0

        thermal_power = (
            self.power_kw * self.heating_efficiency
        )

        thermal_loss = (
            self.thermal_loss_coefficient
            * (
                self.pan_temperature
                - self.ambient_temperature
            )
        )

        temperature_change = (
            (thermal_power - thermal_loss)
            / self.thermal_mass
        ) * dt_seconds

        self.pan_temperature += temperature_change

        self.pan_temperature = max(
            self.ambient_temperature,
            min(self.pan_temperature, 300.0)
        )

        self.update_electrical(dt_seconds)

    def get_thermal_data(self):
        return {
            "power_level": self.power_level,
            "pan_present": self.pan_present,
            "pan_temperature": self.pan_temperature,
            "is_heating": self.is_heating
        }

    def get_data(self):
        data = self.get_electrical_data()
        data.update(self.get_thermal_data())

        data["equipment_id"] = self.equipment_id
        data["manufacturer"] = self.manufacturer
        data["model"] = self.model

        return data
