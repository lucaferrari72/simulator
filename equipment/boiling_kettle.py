
from equipment.base import BaseEquipment


class BoilingKettle(BaseEquipment):

    def __init__(
        self,
        equipment_id="44511",
        model="9EKK/100-P-ME+MA"
    ):

        super().__init__(
            equipment_id=equipment_id,
            manufacturer="Ambach",
            model=model,
            nominal_power_kw=18.0,
            voltage_v=440,
            phases=3,
            frequency_hz=60
        )

        # CAPACITA' E CARICO
        self.capacity_l = 100.0
        self.contents_l = 80.0

        # TEMPERATURE
        self.liquid_temperature = 20.0
        self.jacket_temperature = 20.0

        self.setpoint = 100.0
        self.ambient_temperature = 20.0

        # INTERCAPEDINE
        self.jacket_heating = False
        self.heating_enabled = True

        # STATO OPERATIVO
        self.is_tilted = False
        self.is_boiling = False

        # PARAMETRI TERMICI
        self.jacket_thermal_mass = 30.0
        self.vessel_thermal_mass = 50.0
        self.liquid_specific_heat = 4.18

        self.heat_transfer_coefficient = 0.12
        self.thermal_loss_coefficient = 0.025
        self.heating_efficiency = 0.90

        # CONTROLLO TERMOSTATICO
        self.thermostat_hysteresis = 3.0

        # INDICATORE DI PRESSIONE SIMULATO
        self.jacket_pressure_index = 0.0

    def set_temperature(self, temperature):

        temperature = float(temperature)

        if not 20.0 <= temperature <= 100.0:
            raise ValueError(
                "Temperatura ammessa: 20-100 °C"
            )

        self.setpoint = temperature

    def set_contents(self, quantity_l):

        quantity_l = float(quantity_l)

        if not 0.0 <= quantity_l <= self.capacity_l:
            raise ValueError(
                "Quantità ammessa: 0-100 litri"
            )

        self.contents_l = quantity_l

        if self.contents_l == 0:
            self.is_boiling = False
            self.jacket_heating = False

    def set_heating(self, enabled):

        self.heating_enabled = bool(enabled)

    def set_tilted(self, tilted):

        self.is_tilted = bool(tilted)

        if self.is_tilted:
            self.contents_l = 0.0
            self.jacket_heating = False
            self.is_boiling = False
            self.set_power(0.0)

    def turn_off(self):

        super().turn_off()

        self.jacket_heating = False
        self.is_boiling = False
        self.set_power(0.0)

    def update(self, dt_seconds):

        if dt_seconds <= 0:
            return

        # CONDIZIONI DI SICUREZZA SIMULATE

        if (
            not self.is_on
            or not self.heating_enabled
            or self.is_tilted
            or self.contents_l <= 0
        ):

            self.jacket_heating = False
            self.is_boiling = False

            self.set_power(0.0)

            # Raffreddamento intercapedine
            self.jacket_temperature = max(
                self.ambient_temperature,
                self.jacket_temperature
                - 0.002 * dt_seconds
            )

            self.update_electrical(dt_seconds)
            return

        # CONTROLLO TERMOSTATICO

        if self.liquid_temperature <= (
            self.setpoint - self.thermostat_hysteresis
        ):
            self.jacket_heating = True

        elif self.liquid_temperature >= self.setpoint:
            self.jacket_heating = False

        # POTENZA ELETTRICA
        power = (
            18.0 if self.jacket_heating else 0.0
        )

        self.set_power(power)

        # POTENZA TERMICA DISPONIBILE

        thermal_power = (
            power * self.heating_efficiency
        )

        # TRASFERIMENTO CALORE INTERCAPEDINE-LIQUIDO

        temperature_difference = (
            self.jacket_temperature
            - self.liquid_temperature
        )

        heat_transfer = (
            self.heat_transfer_coefficient
            * temperature_difference
        )

        # temperature_difference = max(
        #    0.0,
        #    self.jacket_temperature
        #    - self.liquid_temperature
        #)

        # heat_transfer = (
        #    self.heat_transfer_coefficient
        #    * temperature_difference
        #)

        #heat_transfer = min(
        #    heat_transfer,
        #    thermal_power
        #)

        # DISPERSIONI TERMICHE

        jacket_loss = (
            self.thermal_loss_coefficient
            * (
                self.jacket_temperature
                - self.ambient_temperature
            )
        )

        # AGGIORNAMENTO TEMPERATURA INTERCAPEDINE

        jacket_energy = (
            thermal_power
            - heat_transfer
            - jacket_loss
        )

        self.jacket_temperature += (
            jacket_energy
            / self.jacket_thermal_mass
        ) * dt_seconds

        self.jacket_temperature = max(
            self.ambient_temperature,
            min(self.jacket_temperature, 150.0)
        )

        # AGGIORNAMENTO TEMPERATURA LIQUIDO

        liquid_thermal_mass = (
            self.vessel_thermal_mass
            + self.contents_l * self.liquid_specific_heat
        )

        if self.liquid_temperature < 100.0:

            self.liquid_temperature += (
                heat_transfer
                / liquid_thermal_mass
            ) * dt_seconds

            self.liquid_temperature = min(
                self.liquid_temperature,
                100.0
            )

        # STATO EBOLLIZIONE

        self.is_boiling = (
            self.liquid_temperature >= 99.5
        )

        # INDICE DI PRESSIONE PURAMENTE DIMOSTRATIVO
        # Non rappresenta una pressione fisica in bar.

        self.jacket_pressure_index = min(
            100.0,
            max(
                0.0,
                (self.jacket_temperature - 20.0) / 1.3
            )
        )

        self.update_electrical(dt_seconds)

    def get_thermal_data(self):

        return {
            "capacity_l": self.capacity_l,
            "contents_l": self.contents_l,

            "liquid_temperature": self.liquid_temperature,
            "jacket_temperature": self.jacket_temperature,

            "setpoint": self.setpoint,

            "heating_enabled": self.heating_enabled,
            "jacket_heating": self.jacket_heating,

            "is_boiling": self.is_boiling,
            "is_tilted": self.is_tilted,

            "jacket_pressure_index": self.jacket_pressure_index
        }

    def get_data(self):

        data = self.get_electrical_data()

        data.update(self.get_thermal_data())

        data["equipment_id"] = self.equipment_id
        data["manufacturer"] = self.manufacturer
        data["model"] = self.model

        return data
