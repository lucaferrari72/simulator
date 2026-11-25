
from equipment.base import BaseEquipment


class InfraredGrill(BaseEquipment):

    def __init__(
        self,
        equipment_id="044519A",
        model="A-8ELG/80-450-MA"
    ):

        super().__init__(
            equipment_id=equipment_id,
            manufacturer="Ambach",
            model=model,
            nominal_power_kw=12.0,
            voltage_v=440,
            phases=3,
            frequency_hz=60
        )

        # DUE ZONE DI COTTURA
        self.zone_count = 2

        self.zone_power_kw = 6.0

        self.zone_1_on = False
        self.zone_2_on = False

        self.zone_1_temperature = 20.0
        self.zone_2_temperature = 20.0

        self.zone_1_setpoint = 250.0
        self.zone_2_setpoint = 250.0

        self.zone_1_heating = False
        self.zone_2_heating = False

        # PARAMETRI TERMICI PROVVISORI
        self.thermal_mass = 45.0
        self.thermal_loss_coefficient = 0.025
        self.heating_efficiency = 0.90

        self.ambient_temperature = 20.0

        # VASCA ACQUA
        self.water_capacity_l = 7.0
        self.water_level_l = 7.0

        self.water_valve_open = False
        self.water_fill_rate_l_s = 0.10

    def set_zone(self, zone, enabled):

        if zone == 1:
            self.zone_1_on = bool(enabled)

        elif zone == 2:
            self.zone_2_on = bool(enabled)

        else:
            raise ValueError("La zona deve essere 1 oppure 2")

    def set_zone_temperature(self, zone, temperature):

        temperature = max(
            20.0,
            min(float(temperature), 500.0)
        )

        if zone == 1:
            self.zone_1_setpoint = temperature

        elif zone == 2:
            self.zone_2_setpoint = temperature

        else:
            raise ValueError("La zona deve essere 1 oppure 2")

    def set_water_valve(self, opened):

        self.water_valve_open = bool(opened)

    def turn_off(self):

        super().turn_off()

        self.zone_1_on = False
        self.zone_2_on = False

        self.zone_1_heating = False
        self.zone_2_heating = False

    def update_zone(
        self,
        temperature,
        setpoint,
        enabled,
        dt_seconds
    ):

        heating = (
            enabled
            and temperature < setpoint - 1.0
        )

        power = self.zone_power_kw if heating else 0.0

        thermal_power = power * self.heating_efficiency

        thermal_loss = (
            self.thermal_loss_coefficient
            * (temperature - self.ambient_temperature)
        )

        temperature_change = (
            (thermal_power - thermal_loss)
            / self.thermal_mass
        ) * dt_seconds

        temperature += temperature_change

        temperature = max(
            self.ambient_temperature,
            min(temperature, 520.0)
        )

        return temperature, heating, power

    def update(self, dt_seconds):

        if dt_seconds <= 0:
            return

        if not self.is_on:

            self.zone_1_heating = False
            self.zone_2_heating = False

            self.set_power(0.0)

            self.update_electrical(dt_seconds)
            return

        # AGGIORNAMENTO ZONA 1
        (
            self.zone_1_temperature,
            self.zone_1_heating,
            power_1
        ) = self.update_zone(
            self.zone_1_temperature,
            self.zone_1_setpoint,
            self.zone_1_on,
            dt_seconds
        )

        # AGGIORNAMENTO ZONA 2
        (
            self.zone_2_temperature,
            self.zone_2_heating,
            power_2
        ) = self.update_zone(
            self.zone_2_temperature,
            self.zone_2_setpoint,
            self.zone_2_on,
            dt_seconds
        )

        # POTENZA COMPLESSIVA
        self.set_power(power_1 + power_2)

        # GESTIONE VASCA ACQUA
        if self.water_valve_open:

            self.water_level_l += (
                self.water_fill_rate_l_s * dt_seconds
            )

            self.water_level_l = min(
                self.water_level_l,
                self.water_capacity_l
            )

        self.update_electrical(dt_seconds)

    def get_thermal_data(self):

        return {
            "zone_1_on": self.zone_1_on,
            "zone_2_on": self.zone_2_on,

            "zone_1_temperature": self.zone_1_temperature,
            "zone_2_temperature": self.zone_2_temperature,

            "zone_1_setpoint": self.zone_1_setpoint,
            "zone_2_setpoint": self.zone_2_setpoint,

            "zone_1_heating": self.zone_1_heating,
            "zone_2_heating": self.zone_2_heating,

            "water_level_l": self.water_level_l,
            "water_valve_open": self.water_valve_open
        }

    def get_data(self):

        data = self.get_electrical_data()

        data.update(self.get_thermal_data())

        data["equipment_id"] = self.equipment_id
        data["manufacturer"] = self.manufacturer
        data["model"] = self.model

        return data
