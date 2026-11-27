
import math

from equipment.base import BaseEquipment


class FryTop(BaseEquipment):

    def __init__(
        self,
        equipment_id="444210",
        model="A-9EBPR/60 III-CL-MA"
    ):

        super().__init__(
            equipment_id=equipment_id,
            manufacturer="Ambach",
            model=model,
            nominal_power_kw=9.0,
            voltage_v=440,
            phases=3,
            frequency_hz=60
        )

        # DUE ZONE DI COTTURA
        self.zone_power_kw = 4.5
        self.zone_1_on = False
        self.zone_2_on = False

        # TEMPERATURE PIASTRA
        self.zone_1_temperature = 20.0
        self.zone_2_temperature = 20.0

        self.zone_1_setpoint = 200.0
        self.zone_2_setpoint = 200.0

        self.zone_1_heating = False
        self.zone_2_heating = False

        # PARAMETRI TERMICI
        self.ambient_temperature = 20.0
        self.thermal_mass = 65.0
        self.thermal_loss_coefficient = 0.035
        self.heating_efficiency = 0.90

        # ISTERESI TERMOSTATO
        self.thermostat_hysteresis = 5.0

    def set_zone(self, zone, enabled):

        if zone == 1:
            self.zone_1_on = bool(enabled)

        elif zone == 2:
            self.zone_2_on = bool(enabled)

        else:
            raise ValueError(
                "La zona deve essere 1 oppure 2"
            )

    def set_zone_temperature(self, zone, temperature):

        temperature = float(temperature)

        if not math.isfinite(temperature):
            raise ValueError("Temperatura non valida")

        temperature = max(
            20.0,
            min(temperature, 300.0)
        )

        if zone == 1:
            self.zone_1_setpoint = temperature

        elif zone == 2:
            self.zone_2_setpoint = temperature

        else:
            raise ValueError(
                "La zona deve essere 1 oppure 2"
            )

    def update_zone(
        self,
        temperature,
        setpoint,
        enabled,
        heating,
        dt_seconds
    ):

        # CONTROLLO TERMOSTATO CON ISTERESI

        if not enabled:
            heating = False

        elif temperature <= setpoint - self.thermostat_hysteresis:
            heating = True

        elif temperature >= setpoint:
            heating = False

        power = (
            self.zone_power_kw
            if heating
            else 0.0
        )

        # BILANCIO TERMICO

        thermal_power = (
            power * self.heating_efficiency
        )

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
            min(temperature, 320.0)
        )

        return temperature, heating, power

    def turn_off(self):

        super().turn_off()

        self.zone_1_on = False
        self.zone_2_on = False

        self.zone_1_heating = False
        self.zone_2_heating = False

    def update(self, dt_seconds):

        try:
            dt_seconds = float(dt_seconds)
        except (TypeError, ValueError):
            return

        if not math.isfinite(dt_seconds) or dt_seconds <= 0:
            return

        # POTENZA APPLICATA DURANTE IL TICK PRECEDENTE
        interval_power_kw = self.power_kw

        if not self.is_on:

            self.zone_1_heating = False
            self.zone_2_heating = False

            self.set_power(0.0)

            self.energy_kwh += (
                interval_power_kw * dt_seconds / 3600.0
            )

            self._update_currents()
            self._check_alarms()
            return

        # ZONA 1

        (
            self.zone_1_temperature,
            self.zone_1_heating,
            power_1
        ) = self.update_zone(
            self.zone_1_temperature,
            self.zone_1_setpoint,
            self.zone_1_on,
            self.zone_1_heating,
            dt_seconds
        )

        # ZONA 2

        (
            self.zone_2_temperature,
            self.zone_2_heating,
            power_2
        ) = self.update_zone(
            self.zone_2_temperature,
            self.zone_2_setpoint,
            self.zone_2_on,
            self.zone_2_heating,
            dt_seconds
        )

        # POTENZA ISTANTANEA DELLE DUE ZONE

        self.set_power(power_1 + power_2)

        # ENERGIA DEL TICK PRECEDENTE

        self.energy_kwh += (
            interval_power_kw * dt_seconds / 3600.0
        )

        # CORRENTI E ALLARMI

        self._update_currents()
        self._check_alarms()

    def get_thermal_data(self):
        return {
            "zone_1_on": self.zone_1_on,
            "zone_2_on": self.zone_2_on,

            "zone_1_temperature": self.zone_1_temperature,
            "zone_2_temperature": self.zone_2_temperature,

            "zone_1_setpoint": self.zone_1_setpoint,
            "zone_2_setpoint": self.zone_2_setpoint,

            "zone_1_heating": self.zone_1_heating,
            "zone_2_heating": self.zone_2_heating
        }

    def get_data(self):

        data = self.get_electrical_data()
        data.update(self.get_thermal_data())

        data["equipment_id"] = self.equipment_id
        data["manufacturer"] = self.manufacturer
        data["model"] = self.model

        return data
