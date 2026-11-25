
from equipment.base import BaseEquipment


class BrattPan(BaseEquipment):

    def __init__(
        self,
        equipment_id="44504",
        model="9EKB/125-ME+MA"
    ):

        super().__init__(
            equipment_id=equipment_id,
            manufacturer="Ambach",
            model=model,
            nominal_power_kw=13.5,
            voltage_v=440,
            phases=3,
            frequency_hz=60
        )

        # CAPACITA' VASCA
        self.capacity_l = 106.0
        self.contents_l = 80.0

        # TEMPERATURE
        self.temperature = 20.0
        self.setpoint = 120.0
        self.ambient_temperature = 20.0

        # STATO OPERATIVO
        self.heating_enabled = True
        self.is_heating = False
        self.is_tilted = False

        # PARAMETRI TERMICI
        # Capacità termica equivalente in kJ/°C
        self.vessel_thermal_mass = 45.0
        self.content_specific_heat = 4.18

        self.thermal_loss_coefficient = 0.025
        self.heating_efficiency = 0.90

        # CONTROLLO TERMOSTATICO
        self.thermostat_hysteresis = 3.0

    def set_temperature(self, temperature):

        temperature = float(temperature)

        if not 20.0 <= temperature <= 200.0:
            raise ValueError(
                "Temperatura ammessa: 20-200 °C"
            )

        self.setpoint = temperature

    def set_contents(self, quantity_l):

        quantity_l = float(quantity_l)

        if not 0.0 <= quantity_l <= self.capacity_l:
            raise ValueError(
                "Quantità ammessa: 0-106 litri"
            )

        self.contents_l = quantity_l

    def set_heating(self, enabled):

        self.heating_enabled = bool(enabled)

    def set_tilted(self, tilted):

        tilted = bool(tilted)

        if tilted:
            self.is_tilted = True
            self.contents_l = 0.0
            self.is_heating = False
            self.set_power(0.0)

        else:
            self.is_tilted = False

    def turn_off(self):

        super().turn_off()

        self.is_heating = False
        self.set_power(0.0)

    def update(self, dt_seconds):

        if dt_seconds <= 0:
            return

        # SICUREZZA E CONDIZIONI OPERATIVE

        if (
            not self.is_on
            or not self.heating_enabled
            or self.is_tilted
            or self.contents_l <= 0
        ):

            self.is_heating = False
            self.set_power(0.0)

            self.update_electrical(dt_seconds)
            return

        # CONTROLLO TERMOSTATO CON ISTERESI

        if self.temperature <= (
            self.setpoint - self.thermostat_hysteresis
        ):
            self.is_heating = True

        elif self.temperature >= self.setpoint:
            self.is_heating = False

        # POTENZA ELETTRICA

        selected_power = (
            13.5 if self.is_heating else 0.0
        )

        self.set_power(selected_power)

        # MASSA TERMICA EQUIVALENTE
        # kJ/°C: vasca + contenuto

        thermal_mass = (
            self.vessel_thermal_mass
            + self.contents_l * self.content_specific_heat
        )

        # POTENZA TERMICA UTILE

        thermal_power = (
            self.power_kw * self.heating_efficiency
        )

        # DISPERSIONE TERMICA

        thermal_loss = (
            self.thermal_loss_coefficient
            * (
                self.temperature
                - self.ambient_temperature
            )
        )

        # BILANCIO ENERGETICO

        temperature_change = (
            (thermal_power - thermal_loss)
            / thermal_mass
        ) * dt_seconds

        self.temperature += temperature_change

        self.temperature = max(
            self.ambient_temperature,
            min(self.temperature, 200.0)
        )

        # AGGIORNAMENTO ENERGETICO

        self.update_electrical(dt_seconds)

    def get_thermal_data(self):

        return {
            "capacity_l": self.capacity_l,
            "contents_l": self.contents_l,
            "temperature": self.temperature,
            "setpoint": self.setpoint,
            "heating_enabled": self.heating_enabled,
            "is_heating": self.is_heating,
            "is_tilted": self.is_tilted
        }

    def get_data(self):

        data = self.get_electrical_data()

        data.update(self.get_thermal_data())

        data["equipment_id"] = self.equipment_id
        data["manufacturer"] = self.manufacturer
        data["model"] = self.model

        return data
