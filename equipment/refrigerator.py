
"""Modello dinamico del frigorifero professionale."""

import math

from equipment.base import BaseEquipment


class Refrigerator(BaseEquipment):
    """Frigorifero professionale con compressore e sbrinamento."""

    def __init__(
        self,
        equipment_id,
        model,
        nominal_power_kw,
        capacity_l,
        doors,
        voltage_v=220,
        compressor_power_kw=None,
        standby_power_kw=None,
        defrost_power_kw=None,
        power_factor=0.85,
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

        self.capacity_l = float(capacity_l)
        self.doors = int(doors)

        if self.capacity_l <= 0 or self.doors < 1:
            raise ValueError("Capacità e numero porte non validi")

        # POTENZE ELETTRICHE
        # I valori di default mantengono il comportamento storico.
        # Per il modello definitivo usare dati di targa.
        self.compressor_power_kw = (
            float(compressor_power_kw)
            if compressor_power_kw is not None
            else self.nominal_power_kw * 0.45
        )

        self.standby_power_kw = (
            float(standby_power_kw)
            if standby_power_kw is not None
            else self.nominal_power_kw * 0.12
        )

        self.defrost_power_kw = (
            float(defrost_power_kw)
            if defrost_power_kw is not None
            else self.nominal_power_kw
        )

        for name, value in (
            ("compressor_power_kw", self.compressor_power_kw),
            ("standby_power_kw", self.standby_power_kw),
            ("defrost_power_kw", self.defrost_power_kw),
        ):
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} non valida")

            if value > self.nominal_power_kw:
                raise ValueError(
                    f"{name} supera la potenza nominale"
                )

        # TEMPERATURE
        self.temperature = 5.0
        self.setpoint = 4.0
        self.ambient_temperature = 25.0

        # TERMOSTATO
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

        # PARAMETRI TERMICI
        self.thermal_mass = 1200.0
        self.cooling_rate = 0.012
        self.ambient_heat_gain = 0.0008
        self.door_heat_gain = 0.025

        # Apporto termico durante lo sbrinamento
        self.defrost_heat_rate = 0.015

        # ALLARMI
        self.high_temperature_alarm = False
        self.low_temperature_alarm = False
        self.door_alarm = False
        self.alarm = False
        self.alarm_code = 0

        self.high_temperature_limit = 10.0
        self.low_temperature_limit = -2.0

        self.state = "OFF"

    # =====================================================
    # CONFIGURAZIONE
    # =====================================================

    def set_temperature(self, temperature):
        temperature = float(temperature)

        if not math.isfinite(temperature):
            raise ValueError("Temperatura non valida")

        if not -5.0 <= temperature <= 10.0:
            raise ValueError("Setpoint ammesso: -5 / +10 °C")

        self.setpoint = temperature

    def set_door(self, opened):
        opened = bool(opened)

        if opened and not self.door_open:
            self.door_open_elapsed = 0.0

        self.door_open = opened

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

    # =====================================================
    # CONTROLLO TERMICO
    # =====================================================

    def update_temperature(self, dt_seconds):
        """Evolve la temperatura anche quando il frigorifero è OFF."""

        dt = float(dt_seconds)

        if dt <= 0:
            return

        if self.defrost_active:
            self.temperature += self.defrost_heat_rate * dt
            return

        heat_gain = self.ambient_heat_gain

        if self.door_open:
            heat_gain += self.door_heat_gain

        if self.cooling_on:
            # Modello termico del raffreddamento con dispersioni.
            total_rate = self.cooling_rate + heat_gain

            equilibrium_temperature = (
                self.cooling_rate * self.setpoint
                + heat_gain * self.ambient_temperature
            ) / total_rate

            self.temperature = (
                equilibrium_temperature
                + (
                    self.temperature - equilibrium_temperature
                ) * math.exp(-total_rate * dt)
            )

        else:
            # Frigorifero fermo: temperatura verso ambiente.
            self.temperature = (
                self.ambient_temperature
                + (
                    self.temperature - self.ambient_temperature
                ) * math.exp(-heat_gain * dt)
            )

        self.temperature = max(
            -50.0,
            min(self.temperature, self.ambient_temperature)
        )

    def _update_thermostat(self):
        """Termostato con isteresi."""

        if not self.is_on or self.defrost_active:
            self.cooling_on = False
            return

        if self.temperature >= (
            self.setpoint + self.cooling_hysteresis
        ):
            self.cooling_on = True

        elif self.temperature <= self.setpoint:
            self.cooling_on = False

    # =====================================================
    # SBRINAMENTO
    # =====================================================

    def _update_defrost(self, dt_seconds):
        if self.defrost_active:
            self.defrost_elapsed += dt_seconds

            if self.defrost_elapsed >= self.defrost_duration:
                self.stop_defrost()

        else:
            self.time_since_defrost += dt_seconds

            if (
                self.time_since_defrost >= self.defrost_interval
                and not self.door_open
            ):
                self.start_defrost()

    # =====================================================
    # POTENZA ELETTRICA
    # =====================================================

    def calculate_power(self):
        """Calcola la potenza assorbita dal frigorifero."""

        if not self.is_on:
            return 0.0

        if self.defrost_active:
            return self.defrost_power_kw

        if self.cooling_on:
            return self.compressor_power_kw

        return self.standby_power_kw

    # =====================================================
    # ALLARMI
    # =====================================================

    def update_alarms(self):
        self.high_temperature_alarm = (
            self.temperature >= self.high_temperature_limit
        )

        self.low_temperature_alarm = (
            self.temperature <= self.low_temperature_limit
        )

        self.door_alarm = self.door_open_elapsed >= 60.0

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

    # =====================================================
    # AGGIORNAMENTO PRINCIPALE
    # =====================================================

    def update(self, dt_seconds):
        dt = float(dt_seconds)

        if not math.isfinite(dt) or dt <= 0:
            return

        # 1. Evoluzione del tempo di apertura porta
        if self.door_open:
            self.door_open_elapsed += dt
        else:
            self.door_open_elapsed = 0.0

        # 2. Evoluzione della temperatura.
        # Continua anche quando il frigorifero è spento.
        self.update_temperature(dt)

        # 3. Gestione dei cicli solo se alimentato
        if self.is_on:
            self._update_defrost(dt)
            self._update_thermostat()
        else:
            self.cooling_on = False
            self.defrost_active = False

        # 4. Potenza elettrica effettiva
        self.set_power(self.calculate_power())

        # 5. Contabilizzazione elettrica.
        # Un aggiornamento per ogni tick, senza duplicazioni.
        self.update_electrical(dt)

        # 6. Allarmi
        self.update_alarms()

        # 7. Stato operativo
        if self.alarm:
            self.state = "ALARM"
        elif not self.is_on:
            self.state = "OFF"
        elif self.defrost_active:
            self.state = "DEFROST"
        elif self.door_open:
            self.state = "DOOR_OPEN"
        elif self.cooling_on:
            self.state = "COOLING"
        else:
            self.state = "STANDBY"

    # =====================================================
    # DATI PER NODE-RED
    # =====================================================

    def get_process_data(self):
        return {
            "temperature": round(self.temperature, 3),
            "setpoint": self.setpoint,
            "ambient_temperature": self.ambient_temperature,

            "capacity_l": self.capacity_l,
            "doors": self.doors,

            "state": self.state,

            "cooling_on": self.cooling_on,
            "compressor_power_kw": self.compressor_power_kw,
            "standby_power_kw": self.standby_power_kw,

            "door_open": self.door_open,
            "door_open_elapsed": self.door_open_elapsed,

            "defrost_active": self.defrost_active,
            "defrost_elapsed": self.defrost_elapsed,
            "defrost_power_kw": self.defrost_power_kw,

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
