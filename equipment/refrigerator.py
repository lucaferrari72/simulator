
from equipment.base import BaseEquipment


class Refrigerator(BaseEquipment):

    def __init__(
        self,
        equipment_id,
        model,
        nominal_power_kw,
        capacity_l,
        doors,
        voltage_v=220
    ):

        super().__init__(
            equipment_id=equipment_id,
            manufacturer="De Wave",
            model=model,
            nominal_power_kw=nominal_power_kw,
            voltage_v=voltage_v,
            phases=1,
            frequency_hz=60
        )

        # CARATTERISTICHE
        self.capacity_l = float(capacity_l)
        self.doors = int(doors)

        # TEMPERATURE
        self.temperature = 5.0
        self.setpoint = 4.0
        self.ambient_temperature = 25.0

        # CONTROLLO TERMICO
        self.cooling_on = False
        self.cooling_hysteresis = 2.0

        # PORTE
        self.door_open = False
        self.door_open_elapsed = 0.0

        # SBRINAMENTO
        self.defrost_active = False
        self.defrost_elapsed = 0.0
        self.defrost_duration = 600.0
        self.defrost_interval = 21600.0
        self.time_since_defrost = 0.0

        self.defrost_power_kw = nominal_power_kw

        # PARAMETRI TERMICI SIMULATI
        self.thermal_mass = 1200.0
        self.cooling_rate = 0.012
        self.ambient_heat_gain = 0.0008
        self.door_heat_gain = 0.025

        # ALLARMI
        self.high_temperature_alarm = False
        self.low_temperature_alarm = False
        self.door_alarm = False
        self.alarm = False
        self.alarm_code = 0

        # SOGLIE
        self.high_temperature_limit = 10.0
        self.low_temperature_limit = -2.0

        self.state = "COOLING"

    # -----------------------------------------
    # CONFIGURAZIONE
    # -----------------------------------------

    def set_temperature(self, temperature):

        temperature = float(temperature)

        if not -5.0 <= temperature <= 10.0:
            raise ValueError(
                "Setpoint ammesso: -5 / +10 °C"
            )

        self.setpoint = temperature

    def set_door(self, opened):

        self.door_open = bool(opened)

        if opened:
            self.door_open_elapsed = 0.0

    def start_defrost(self):

        if self.defrost_active:
            return False

        if not self.is_on or self.door_open:
            return False

        self.defrost_active = True
        self.defrost_elapsed = 0.0
        self.cooling_on = False

        return True

    def stop_defrost(self):

        self.defrost_active = False
        self.defrost_elapsed = 0.0
        self.time_since_defrost = 0.0

    # -----------------------------------------
    # CONTROLLO TERMICO
    # -----------------------------------------

    def update_temperature(self, dt_seconds):

        if self.defrost_active:

            # Apporto termico durante lo sbrinamento
            self.temperature += (
                0.015 * dt_seconds
            )

        elif self.cooling_on and not self.door_open:

            # Raffreddamento simulato
            self.temperature -= (
                self.cooling_rate
                * (self.temperature - self.setpoint)
                * dt_seconds
            )

            # Guadagno termico ambientale
            self.temperature += (
                self.ambient_heat_gain
                * (self.ambient_temperature - self.temperature)
                * dt_seconds
            )

        else:

            # Risalita naturale della temperatura
            gain = self.ambient_heat_gain

            if self.door_open:
                gain += self.door_heat_gain

            self.temperature += (
                gain
                * (self.ambient_temperature - self.temperature)
                * dt_seconds
            )

    # -----------------------------------------
    # ALLARMI
    # -----------------------------------------

    def update_alarms(self):

        self.high_temperature_alarm = (
            self.temperature >= self.high_temperature_limit
        )

        self.low_temperature_alarm = (
            self.temperature <= self.low_temperature_limit
        )

        self.door_alarm = (
            self.door_open_elapsed >= 60.0
        )

        self.alarm = (
            self.high_temperature_alarm
            or self.low_temperature_alarm
            or self.door_alarm
        )

        if self.high_temperature_alarm:
            self.alarm_code = 1

        elif self.low_temperature_alarm:
            self.alarm_code = 2

        elif self.door_alarm:
            self.alarm_code = 3

        else:
            self.alarm_code = 0

    # -----------------------------------------
    # AGGIORNAMENTO PRINCIPALE
    # -----------------------------------------

    def update(self, dt_seconds):

        if dt_seconds <= 0:
            return

        if not self.is_on:

            self.cooling_on = False
            self.set_power(0.0)

            self.update_electrical(dt_seconds)
            return

        # TEMPO PORTA APERTA
        if self.door_open:
            self.door_open_elapsed += dt_seconds
        else:
            self.door_open_elapsed = 0.0

        # SBRINAMENTO
        if self.defrost_active:

            self.defrost_elapsed += dt_seconds

            if self.defrost_elapsed >= self.defrost_duration:
                self.stop_defrost()

        else:

            self.time_since_defrost += dt_seconds

            # AVVIO SBRINAMENTO AUTOMATICO
            if (
                self.time_since_defrost >= self.defrost_interval
                and not self.door_open
            ):
                self.start_defrost()

        # CONTROLLO TERMOSTATO
        if not self.defrost_active and not self.door_open:

            if self.temperature >= (
                self.setpoint + self.cooling_hysteresis
            ):
                self.cooling_on = True

            elif self.temperature <= self.setpoint:
                self.cooling_on = False

        else:
            self.cooling_on = False

        # POTENZA ELETTRICA
        if self.defrost_active:
            power = self.defrost_power_kw

        elif self.cooling_on:
            power = self.nominal_power_kw * 0.45

        else:
            power = self.nominal_power_kw * 0.12

        self.set_power(power)

        # AGGIORNAMENTO TEMPERATURA
        self.update_temperature(dt_seconds)

        # ALLARMI
        self.update_alarms()

        # STATO
        if self.alarm:
            self.state = "ALARM"

        elif self.defrost_active:
            self.state = "DEFROST"

        elif self.door_open:
            self.state = "DOOR_OPEN"

        elif self.cooling_on:
            self.state = "COOLING"

        else:
            self.state = "STANDBY"

        self.update_electrical(dt_seconds)

    # -----------------------------------------
    # DATI PER NODE-RED
    # -----------------------------------------

    def get_process_data(self):

        return {
            "temperature": round(self.temperature, 2),
            "setpoint": self.setpoint,

            "capacity_l": self.capacity_l,
            "doors": self.doors,

            "state": self.state,

            "cooling_on": self.cooling_on,

            "door_open": self.door_open,
            "door_open_elapsed": self.door_open_elapsed,

            "defrost_active": self.defrost_active,
            "defrost_elapsed": self.defrost_elapsed,

            "high_temperature_alarm": self.high_temperature_alarm,
            "low_temperature_alarm": self.low_temperature_alarm,
            "door_alarm": self.door_alarm,

            "alarm": self.alarm,
            "alarm_code": self.alarm_code
        }

    def get_data(self):

        data = self.get_electrical_data()

        data.update(self.get_process_data())

        data["equipment_id"] = self.equipment_id
        data["manufacturer"] = self.manufacturer
        data["model"] = self.model

        return data
