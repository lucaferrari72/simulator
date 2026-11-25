
class BaseEquipment:

    def __init__(
        self,
        equipment_id,
        manufacturer,
        model,
        nominal_power_kw,
        voltage_v,
        phases=3,
        frequency_hz=60
    ):

        self.equipment_id = equipment_id
        self.manufacturer = manufacturer
        self.model = model

        self.nominal_power_kw = nominal_power_kw
        self.voltage_v = voltage_v
        self.phases = phases
        self.frequency_hz = frequency_hz

        self.is_on = False
        self.power_kw = 0.0
        self.energy_kwh = 0.0

        self.current_l1_a = 0.0
        self.current_l2_a = 0.0
        self.current_l3_a = 0.0

        self.alarm = False

    def turn_on(self):
        self.is_on = True

    def turn_off(self):
        self.is_on = False
        self.power_kw = 0.0
        self.current_l1_a = 0.0
        self.current_l2_a = 0.0
        self.current_l3_a = 0.0

    def set_power(self, power_kw):

        if not self.is_on:
            self.power_kw = 0.0
            return

        self.power_kw = max(
            0.0,
            min(power_kw, self.nominal_power_kw)
        )

    def update_electrical(self, dt_seconds):

        if self.phases == 3:

            current = (
                self.power_kw * 1000
                / (3 ** 0.5 * self.voltage_v)
            )

            self.current_l1_a = current
            self.current_l2_a = current
            self.current_l3_a = current

        elif self.phases == 1:

            current = (
                self.power_kw * 1000
                / self.voltage_v
            )

            self.current_l1_a = current

            self.current_l2_a = 0.0
            self.current_l3_a = 0.0

        self.energy_kwh += (
            self.power_kw * dt_seconds / 3600
        )

    def get_electrical_data(self):

        return {
            "voltage_v": self.voltage_v,
            "frequency_hz": self.frequency_hz,
            "power_kw": self.power_kw,
            "energy_kwh": self.energy_kwh,
            "current_l1_a": self.current_l1_a,
            "current_l2_a": self.current_l2_a,
            "current_l3_a": self.current_l3_a,
            "alarm": self.alarm,
            "is_on": self.is_on
        }
