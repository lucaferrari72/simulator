
from equipment.base import BaseEquipment


class Hood(BaseEquipment):

    def __init__(
        self,
        equipment_id,
        model,
        hood_type,
        nominal_power_kw
    ):

        super().__init__(
            equipment_id=equipment_id,
            manufacturer="Owner Supply",
            model=model,
            nominal_power_kw=nominal_power_kw,
            voltage_v=220,
            phases=1,
            frequency_hz=60
        )

        self.hood_type = hood_type

        # COMPONENTI
        self.lighting_on = False
        self.fan_on = False

        # WATER WASH
        self.water_valve_open = False
        self.wash_active = False
        self.wash_duration = 120.0
        self.wash_elapsed = 0.0

        # SENSORE UV - TEPPANYAKI
        self.uv_sensor_active = False

        # FILTRI
        self.filter_alarm = False
        self.filter_condition = 100.0

        # ALLARMI
        self.thermal_alarm = False
        self.alarm = False
        self.alarm_code = 0

        # STATO
        self.state = "STANDBY"

    # -----------------------------------------
    # ILLUMINAZIONE
    # -----------------------------------------

    def set_lighting(self, enabled):

        self.lighting_on = bool(enabled)

    # -----------------------------------------
    # VENTILAZIONE CENTRALIZZATA
    # -----------------------------------------

    def set_fan(self, enabled):

        self.fan_on = bool(enabled)

    # -----------------------------------------
    # WATER WASH
    # -----------------------------------------

    def start_wash(self):

        if self.hood_type != "WATER_WASH":
            return False

        if self.wash_active or self.alarm:
            return False

        self.wash_active = True
        self.wash_elapsed = 0.0
        self.water_valve_open = True

        return True

    def stop_wash(self):

        self.wash_active = False
        self.water_valve_open = False
        self.wash_elapsed = 0.0

    # -----------------------------------------
    # SENSORE UV
    # -----------------------------------------

    def set_uv_sensor(self, active):

        if self.hood_type != "TEPPANYAKI":
            return False

        self.uv_sensor_active = bool(active)

        return True

    # -----------------------------------------
    # FILTRI
    # -----------------------------------------

    def set_filter_condition(self, percentage):

        percentage = float(percentage)

        if not 0 <= percentage <= 100:
            raise ValueError(
                "Condizione filtro ammessa: 0-100%"
            )

        self.filter_condition = percentage

        self.filter_alarm = percentage <= 20

        self.update_alarms()

    # -----------------------------------------
    # ALLARMI
    # -----------------------------------------

    def set_thermal_alarm(self, active):

        self.thermal_alarm = bool(active)

        self.update_alarms()

    def update_alarms(self):

        self.filter_alarm = (
            self.filter_condition <= 20
        )

        self.alarm = (
            self.filter_alarm
            or self.thermal_alarm
        )

        if self.thermal_alarm:
            self.alarm_code = 2

        elif self.filter_alarm:
            self.alarm_code = 1

        else:
            self.alarm_code = 0

        if self.alarm:
            self.stop_wash()

    def reset_alarm(self):

        if self.thermal_alarm or self.filter_condition <= 20:
            return False

        self.alarm = False
        self.alarm_code = 0

        return True

    # -----------------------------------------
    # CALCOLO POTENZA
    # -----------------------------------------

    def calculate_power(self):

        power = 0.0

        if self.hood_type == "WATER_WASH":

            # Centralina ed elettrovalvole
            if self.is_on:
                power = 0.10

        elif self.hood_type == "DRY_GREASE":

            # Illuminazione LED
            if self.lighting_on:
                power = 0.078

        elif self.hood_type == "TEPPANYAKI":

            # Illuminazione e sensori
            if self.lighting_on or self.uv_sensor_active:
                power = 0.10

        return min(power, self.nominal_power_kw)

    # -----------------------------------------
    # AGGIORNAMENTO
    # -----------------------------------------

    def update(self, dt_seconds):

        if dt_seconds <= 0:
            return

        if not self.is_on:

            self.lighting_on = False
            self.fan_on = False
            self.stop_wash()
            self.uv_sensor_active = False

        # CICLO WATER WASH
        if self.wash_active:

            if self.hood_type != "WATER_WASH" or self.alarm:

                self.stop_wash()

            else:

                self.wash_elapsed += dt_seconds

                if self.wash_elapsed >= self.wash_duration:
                    self.stop_wash()

        self.update_alarms()

        # CALCOLO ASSORBIMENTO LOCALE
        power = self.calculate_power()

        self.set_power(power)

        # STATO OPERATIVO
        if self.alarm:
            self.state = "ALARM"

        elif self.wash_active:
            self.state = "WASHING"

        elif self.fan_on:
            self.state = "VENTILATION"

        elif self.lighting_on:
            self.state = "LIGHTING"

        else:
            self.state = "STANDBY"

        self.update_electrical(dt_seconds)

    # -----------------------------------------
    # DATI PER NODE-RED
    # -----------------------------------------

    def get_process_data(self):

        return {
            "hood_type": self.hood_type,

            "state": self.state,

            "lighting_on": self.lighting_on,
            "fan_on": self.fan_on,

            "water_valve_open": self.water_valve_open,
            "wash_active": self.wash_active,
            "wash_elapsed": self.wash_elapsed,

            "uv_sensor_active": self.uv_sensor_active,

            "filter_condition": self.filter_condition,
            "filter_alarm": self.filter_alarm,

            "thermal_alarm": self.thermal_alarm,

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
