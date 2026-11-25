
from equipment.base import BaseEquipment


class Dishwasher(BaseEquipment):

    def __init__(
        self,
        equipment_id="44909",
        model="FV 40.2 Marine"
    ):

        super().__init__(
            equipment_id=equipment_id,
            manufacturer="Meiko",
            model=model,
            nominal_power_kw=9.2,
            voltage_v=440,
            phases=3,
            frequency_hz=60
        )

        # POTENZE ELETTRICHE
        self.boiler_power_kw = 6.5
        self.tank_heater_power_kw = 2.0
        self.pump_power_kw = 0.7

        # CAPACITA'
        self.tank_capacity_l = 11.0
        self.tank_water_l = 0.0
        self.boiler_water_l = 8.0

        # TEMPERATURE
        self.tank_temperature = 20.0
        self.boiler_temperature = 20.0

        self.tank_setpoint = 60.0
        self.boiler_setpoint = 85.0

        self.ambient_temperature = 20.0

        # PARAMETRI TERMICI PROVVISORI
        self.tank_thermal_mass = 20.0
        self.boiler_thermal_mass = 15.0
        self.water_specific_heat = 4.18

        self.thermal_loss_coefficient = 0.015
        self.heating_efficiency = 0.90

        # STATI DELLA MACCHINA
        self.state = "STANDBY"

        self.cycle_duration = 90
        self.cycle_elapsed = 0.0
        self.phase_elapsed = 0.0

        self.fill_duration = 20.0
        self.fill_elapsed = 0.0

        self.cycles_completed = 0

        # COMPONENTI
        self.tank_heating = False
        self.boiler_heating = False
        self.wash_pump_on = False

        # ALLARMI
        self.alarm = False
        self.alarm_code = 0
        self.door_open = False

    # --------------------------------------------------
    # CONFIGURAZIONE
    # --------------------------------------------------

    def set_cycle_duration(self, seconds):

        if seconds not in (90, 120, 180):
            raise ValueError(
                "Ciclo ammesso: 90, 120 oppure 180 secondi"
            )

        self.cycle_duration = seconds

    def set_door(self, opened):

        self.door_open = bool(opened)

    def set_fault(self, code):

        self.alarm = True
        self.alarm_code = int(code)

        self.wash_pump_on = False
        self.tank_heating = False
        self.boiler_heating = False

        self.set_power(0.0)

    def reset_alarm(self):

        if self.door_open:
            return False

        self.alarm = False
        self.alarm_code = 0

        return True

    # --------------------------------------------------
    # AVVIO CICLO
    # --------------------------------------------------

    def start_cycle(self):

        if not self.is_on:
            return False

        if self.alarm or self.door_open:
            return False

        if self.state not in ("STANDBY", "COMPLETE"):
            return False

        self.state = "FILLING"

        self.fill_elapsed = 0.0
        self.phase_elapsed = 0.0
        self.cycle_elapsed = 0.0

        self.tank_water_l = 0.0

        self.tank_heating = False
        self.boiler_heating = False
        self.wash_pump_on = False

        return True

    # --------------------------------------------------
    # RISCALDAMENTO
    # --------------------------------------------------

    #def update_heating(self, dt_seconds):
    def update_heating(
        self,
        dt_seconds,
        allow_tank=True,
        allow_boiler=True
        ):

        # TERMOSTATO VASCA
        if not allow_tank:
            self.tank_heating = False

        elif self.tank_temperature <= self.tank_setpoint - 2:
            self.tank_heating = True

        elif self.tank_temperature >= self.tank_setpoint:
            self.tank_heating = False

        # TERMOSTATO BOILER
        if not allow_boiler:
            self.boiler_heating = False

        elif self.boiler_temperature <= self.boiler_setpoint - 2:
            self.boiler_heating = True

        elif self.boiler_temperature >= self.boiler_setpoint:
            self.boiler_heating = False

        # POTENZA TERMICA VASCA
        tank_power = (
            self.tank_heater_power_kw
            if self.tank_heating
            else 0.0
        )

        # POTENZA TERMICA BOILER
        boiler_power = (
            self.boiler_power_kw
            if self.boiler_heating
            else 0.0
        )

        # MASSA TERMICA VASCA
        tank_mass = (
            self.tank_thermal_mass
            + self.tank_water_l * self.water_specific_heat
        )

        # MASSA TERMICA BOILER
        boiler_mass = (
            self.boiler_thermal_mass
            + self.boiler_water_l * self.water_specific_heat
        )

        # DISPERSIONE TERMICA
        tank_loss = (
            self.thermal_loss_coefficient
            * (self.tank_temperature - self.ambient_temperature)
        )

        boiler_loss = (
            self.thermal_loss_coefficient
            * (self.boiler_temperature - self.ambient_temperature)
        )

        # BILANCIO TERMICO VASCA
        tank_energy = (
            tank_power * self.heating_efficiency
            - tank_loss
        )

        self.tank_temperature += (
            tank_energy / tank_mass
        ) * dt_seconds

        # BILANCIO TERMICO BOILER
        boiler_energy = (
            boiler_power * self.heating_efficiency
            - boiler_loss
        )

        self.boiler_temperature += (
            boiler_energy / boiler_mass
        ) * dt_seconds

        self.tank_temperature = max(
            self.ambient_temperature,
            min(self.tank_temperature, 95.0)
        )

        self.boiler_temperature = max(
            self.ambient_temperature,
            min(self.boiler_temperature, 95.0)
        )

        return tank_power, boiler_power

    # --------------------------------------------------
    # AGGIORNAMENTO MACCHINA
    # --------------------------------------------------

    def update(self, dt_seconds):

        if dt_seconds <= 0:
            return

        if not self.is_on or self.alarm or self.door_open:

            self.tank_heating = False
            self.boiler_heating = False
            self.wash_pump_on = False

            self.set_power(0.0)
            self.update_electrical(dt_seconds)

            return

        total_power = 0.0

        # FASE 1: RIEMPIMENTO
        if self.state == "FILLING":

            self.fill_elapsed += dt_seconds

            fill_rate = (
                self.tank_capacity_l / self.fill_duration
            )

            self.tank_water_l = min(
                self.tank_capacity_l,
                self.tank_water_l + fill_rate * dt_seconds
            )

            if self.fill_elapsed >= self.fill_duration:
                self.tank_water_l = self.tank_capacity_l
                self.state = "HEATING"

        # FASE 2: RISCALDAMENTO
        if self.state == "HEATING":

            tank_power, boiler_power = self.update_heating(dt_seconds, True, True)

            total_power = tank_power + boiler_power

            if (
                self.tank_temperature >= self.tank_setpoint
                and self.boiler_temperature >= self.boiler_setpoint
            ):

                self.state = "WASHING"
                self.phase_elapsed = 0.0
                self.cycle_elapsed = 0.0

        # FASE 3: LAVAGGIO
        elif self.state == "WASHING":

            tank_power, boiler_power = self.update_heating(dt_seconds, True, False)

            self.wash_pump_on = True

            total_power = (
                tank_power + self.pump_power_kw
            )

            self.phase_elapsed += dt_seconds
            self.cycle_elapsed += dt_seconds

            wash_duration = self.cycle_duration * 0.70

            if self.phase_elapsed >= wash_duration:

                self.state = "RINSING"
                self.phase_elapsed = 0.0

        # FASE 4: RISCIACQUO
        elif self.state == "RINSING":

            tank_power, boiler_power = self.update_heating(dt_seconds, False, True)

            self.wash_pump_on = True

            total_power = (
                boiler_power + self.pump_power_kw
            )

            self.phase_elapsed += dt_seconds
            self.cycle_elapsed += dt_seconds

            rinse_duration = self.cycle_duration * 0.30

            if self.phase_elapsed >= rinse_duration:

                self.state = "COMPLETE"

                self.cycles_completed += 1

                self.wash_pump_on = False
                self.tank_heating = False
                self.boiler_heating = False

                total_power = 0.0

        # FINE CICLO
        if self.state in ("STANDBY", "COMPLETE"):
            self.wash_pump_on = False

        self.set_power(total_power)

        self.update_electrical(dt_seconds)

    # --------------------------------------------------
    # DATI ESPOSTI
    # --------------------------------------------------

    def get_process_data(self):

        return {
            "state": self.state,

            "tank_water_l": self.tank_water_l,
            "tank_temperature": self.tank_temperature,
            "tank_setpoint": self.tank_setpoint,

            "boiler_temperature": self.boiler_temperature,
            "boiler_setpoint": self.boiler_setpoint,

            "tank_heating": self.tank_heating,
            "boiler_heating": self.boiler_heating,

            "wash_pump_on": self.wash_pump_on,

            "cycle_duration": self.cycle_duration,
            "cycle_elapsed": self.cycle_elapsed,

            "cycles_completed": self.cycles_completed,

            "door_open": self.door_open,
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
