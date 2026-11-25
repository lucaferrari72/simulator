
from equipment.base import BaseEquipment


class Fryer(BaseEquipment):

    def __init__(
        self,
        equipment_id="44422",
        model="A-9EF1/60-24-MA",
        nominal_power_kw=24.0,
        oil_capacity_l=32.0,
        voltage_v=440,
        basket_count=2,
        thermal_mass=180.0
    ):

        super().__init__(
            equipment_id=equipment_id,
            manufacturer="Ambach",
            model=model,
            nominal_power_kw=nominal_power_kw,
            voltage_v=voltage_v,
            phases=3,
            frequency_hz=60
        )

        self.oil_capacity_l = oil_capacity_l
        self.basket_count = basket_count

        self.oil_temperature = 20.0
        self.temperature_setpoint = 180.0
        self.ambient_temperature = 20.0

        self.is_heating = False

        self.thermal_mass = thermal_mass
        self.thermal_loss_coefficient = 0.025
        self.heating_efficiency = 0.90

    def set_temperature(self, temperature):

        self.temperature_setpoint = max(
            100.0,
            min(temperature, 190.0)
        )

    def turn_on(self):

        super().turn_on()

    def turn_off(self):

        super().turn_off()

        self.is_heating = False

    def update(self, dt_seconds):

        if dt_seconds <= 0:
            return

        if not self.is_on:

            self.is_heating = False

            self.set_power(0.0)

            self.update_electrical(dt_seconds)

            return

        # DIFFERENZA TERMICA
        temperature_difference = (
            self.temperature_setpoint
            - self.oil_temperature
        )

        # CONTROLLO TERMOSTATO
        self.is_heating = (
            temperature_difference > 1.0
        )

        if self.is_heating:

            self.set_power(
                self.nominal_power_kw
            )

        else:

            self.set_power(0.0)

        # POTENZA TERMICA UTILE
        thermal_power = (
            self.power_kw
            * self.heating_efficiency
        )

        # PERDITA TERMICA
        thermal_loss = (
            self.thermal_loss_coefficient
            * (
                self.oil_temperature
                - self.ambient_temperature
            )
        )

        # AGGIORNAMENTO TEMPERATURA
        temperature_change = (
            (thermal_power - thermal_loss)
            / self.thermal_mass
        ) * dt_seconds

        self.oil_temperature += temperature_change

        # LIMITI FISICI DEL MODELLO
        self.oil_temperature = max(
            self.ambient_temperature,
            min(self.oil_temperature, 250.0)
        )

        # AGGIORNAMENTO ELETTRICO
        self.update_electrical(dt_seconds)

    def get_thermal_data(self):

        return {
            "oil_temperature": self.oil_temperature,
            "temperature_setpoint": self.temperature_setpoint,
            "is_heating": self.is_heating,
            "is_on": self.is_on
        }

    def get_data(self):

        data = self.get_electrical_data()

        data.update(self.get_thermal_data())

        data["equipment_id"] = self.equipment_id
        data["manufacturer"] = self.manufacturer
        data["model"] = self.model

        return data
