
import math

from equipment.base import BaseEquipment


class SolidTop(BaseEquipment):

    def __init__(
        self,
        equipment_id="44424",
        model="A-9EP/90+MA"
    ):

        super().__init__(
            equipment_id=equipment_id,
            manufacturer="Ambach",
            model=model,
            nominal_power_kw=16.0,
            voltage_v=440,
            phases=3,
            frequency_hz=60
        )

        # QUATTRO ZONE DI COTTURA
        self.zone_count = 4
        self.zone_power_kw = 4.0

        self.zone_on = [False] * 4
        self.zone_temperature = [20.0] * 4
        self.zone_setpoint = [200.0] * 4
        self.zone_heating = [False] * 4

        # PARAMETRI TERMICI
        self.ambient_temperature = 20.0
        self.thermal_mass = 55.0
        self.thermal_loss_coefficient = 0.035
        self.heating_efficiency = 0.90

        # CONTROLLO TERMOSTATICO
        self.thermostat_hysteresis = 5.0

    def _validate_zone(self, zone):

        if not isinstance(zone, int) or isinstance(zone, bool):
            raise ValueError("La zona deve essere un intero")

        if zone not in range(1, 5):
            raise ValueError(
                "La zona deve essere compresa tra 1 e 4"
            )

        return zone - 1

    def set_zone(self, zone, enabled):

        index = self._validate_zone(zone)
        self.zone_on[index] = bool(enabled)

    def set_zone_temperature(self, zone, temperature):

        index = self._validate_zone(zone)
        temperature = float(temperature)

        if not math.isfinite(temperature):
            raise ValueError("Temperatura non valida")

        if not 20.0 <= temperature <= 440.0:
            raise ValueError(
                "La temperatura deve essere tra 20 e 440 °C"
            )

        self.zone_setpoint[index] = temperature

    def update_zone(self, index, dt_seconds):

        temperature = self.zone_temperature[index]
        setpoint = self.zone_setpoint[index]
        enabled = self.zone_on[index]
        heating = self.zone_heating[index]

        # CONTROLLO TERMOSTATO CON ISTERESI

        if not enabled:
            heating = False

        elif temperature <= setpoint - self.thermostat_hysteresis:
            heating = True

        elif temperature >= setpoint:
            heating = False

        power = self.zone_power_kw if heating else 0.0

        # BILANCIO TERMICO

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
            min(temperature, 460.0)
        )

        self.zone_temperature[index] = temperature
        self.zone_heating[index] = heating

        return power

    def turn_off(self):

        super().turn_off()

        self.zone_on = [False] * 4
        self.zone_heating = [False] * 4

    def update(self, dt_seconds):

        try:
            dt_seconds = float(dt_seconds)
        except (TypeError, ValueError):
            raise ValueError("Intervallo temporale non valido")

        if not math.isfinite(dt_seconds) or dt_seconds <= 0:
            return

        # POTENZA APPLICATA DURANTE IL TICK PRECEDENTE
        interval_power_kw = self.power_kw

        if not self.is_on:

            self.zone_heating = [False] * 4
            self.set_power(0.0)

        else:

            total_power = 0.0

            # AGGIORNAMENTO DELLE QUATTRO ZONE

            for index in range(self.zone_count):

                zone_power = self.update_zone(
                    index,
                    dt_seconds
                )

                total_power += zone_power

            # POTENZA ISTANTANEA DEL NUOVO TICK

            self.set_power(total_power)

        # ENERGIA: POTENZA DEL TICK APPENA TRASCORSO

        self.energy_kwh += (
            interval_power_kw * dt_seconds / 3600.0
        )

        # CORRENTI E ALLARMI

        self._update_currents()
        self._check_alarms()

    def get_thermal_data(self):

        return {
            "zone_count": self.zone_count,
            "zone_on": self.zone_on.copy(),
            "zone_temperature": self.zone_temperature.copy(),
            "zone_setpoint": self.zone_setpoint.copy(),
            "zone_heating": self.zone_heating.copy()
        }

    def get_data(self):

        data = self.get_electrical_data()
        data.update(self.get_thermal_data())

        data["equipment_id"] = self.equipment_id
        data["manufacturer"] = self.manufacturer
        data["model"] = self.model

        return data
