
from equipment.base import BaseEquipment


class CombiOven(BaseEquipment):

    MODES = {
        "hot_air": 10.25,
        "steam": 9.0,
        "combi": 11.0,
    }

    def __init__(
        self,
        equipment_id="44503",
        model="iCombi Pro 06-1/1 Marine"
    ):

        super().__init__(
            equipment_id=equipment_id,
            manufacturer="Rational",
            model=model,
            nominal_power_kw=11.0,
            voltage_v=440,
            phases=3,
            frequency_hz=60
        )

        # MODALITA' OPERATIVA
        self.mode = "hot_air"

        # TEMPERATURE
        self.chamber_temperature = 20.0
        self.chamber_setpoint = 180.0

        self.core_temperature = 20.0
        self.core_target_temperature = 75.0

        self.ambient_temperature = 20.0

        # STATO OPERATIVO
        self.is_heating = False
        self.door_open = False
        self.cooking_active = False

        # PARAMETRI TERMICI PROVVISORI
        self.chamber_thermal_mass = 35.0
        self.core_thermal_mass = 120.0

        self.thermal_loss_coefficient = 0.035
        self.core_transfer_coefficient = 0.12

        self.heating_efficiency = 0.90

        # CONTATORI
        self.cooking_time_seconds = 0

    def set_mode(self, mode):

        if mode not in self.MODES:
            raise ValueError(
                f"Modalità non valida: {mode}"
            )

        self.mode = mode

    def set_chamber_temperature(self, temperature):

        self.chamber_setpoint = max(
            30.0,
            min(float(temperature), 300.0)
        )

    def set_core_target(self, temperature):

        self.core_target_temperature = max(
            0.0,
            min(float(temperature), 100.0)
        )

    def set_door(self, opened):

        self.door_open = bool(opened)

    def start_cooking(self):

        if not self.is_on:
            self.turn_on()

        self.cooking_active = True

    def stop_cooking(self):

        self.cooking_active = False
        self.is_heating = False
        self.set_power(0.0)

    def turn_off(self):

        super().turn_off()

        self.is_heating = False
        self.cooking_active = False

    def update(self, dt_seconds):

        if dt_seconds <= 0:
            return

        if not self.is_on or not self.cooking_active:

            self.is_heating = False
            self.set_power(0.0)

            self.update_electrical(dt_seconds)
            return

        # CONTROLLO TEMPERATURA CAMERA
        temperature_difference = (
            self.chamber_setpoint
            - self.chamber_temperature
        )

        self.is_heating = (
            temperature_difference > 1.0
            and not self.door_open
        )

        if self.is_heating:

            selected_power = self.MODES[self.mode]

            self.set_power(selected_power)

        else:

            self.set_power(0.0)

        # POTENZA TERMICA
        thermal_power = (
            self.power_kw * self.heating_efficiency
        )

        # DISPERSIONE TERMICA
        thermal_loss = (
            self.thermal_loss_coefficient
            * (
                self.chamber_temperature
                - self.ambient_temperature
            )
        )

        if self.door_open:
            thermal_loss *= 8.0

        # AGGIORNAMENTO CAMERA
        chamber_change = (
            (thermal_power - thermal_loss)
            / self.chamber_thermal_mass
        ) * dt_seconds

        self.chamber_temperature += chamber_change

        self.chamber_temperature = max(
            self.ambient_temperature,
            min(self.chamber_temperature, 320.0)
        )

        # TRASFERIMENTO TERMICO AL PRODOTTO
        core_difference = (
            self.chamber_temperature
            - self.core_temperature
        )

        core_change = (
            self.core_transfer_coefficient
            * core_difference
            / self.core_thermal_mass
        ) * dt_seconds

        self.core_temperature += core_change

        self.core_temperature = max(
            0.0,
            min(self.core_temperature, 100.0)
        )

        # TEMPO DI COTTURA
        if self.cooking_active:
            self.cooking_time_seconds += dt_seconds

        # AGGIORNAMENTO ELETTRICO
        self.update_electrical(dt_seconds)

    def get_thermal_data(self):

        return {
            "mode": self.mode,
            "chamber_temperature": self.chamber_temperature,
            "chamber_setpoint": self.chamber_setpoint,
            "core_temperature": self.core_temperature,
            "core_target_temperature": self.core_target_temperature,
            "is_heating": self.is_heating,
            "door_open": self.door_open,
            "cooking_active": self.cooking_active,
            "cooking_time_seconds": self.cooking_time_seconds
        }

    def get_data(self):

        data = self.get_electrical_data()

        data.update(self.get_thermal_data())

        data["equipment_id"] = self.equipment_id
        data["manufacturer"] = self.manufacturer
        data["model"] = self.model

        return data
