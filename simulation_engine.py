
import time


class SimulationEngine:

    def __init__(
        self,
        equipment_manager,
        scheduler=None,
        time_scale=1.0,
        start_seconds=19800
    ):

        self.manager = equipment_manager
        self.scheduler = scheduler

        self.running = False

        self.initial_time = float(start_seconds)
        self.simulation_time = float(start_seconds)

        self.time_scale = float(time_scale)

        if self.time_scale <= 0:
            raise ValueError("time_scale deve essere positivo")

        self.total_cycles = 0
        self.last_update = None

    # =====================================
    # AVVIO
    # =====================================

    def start(self):

        if self.running:
            return False

        self.running = True

        self.last_update = time.monotonic()

        if self.scheduler:
            self.scheduler.update(self.simulation_time)

        return True

    # =====================================
    # PAUSA
    # =====================================

    def stop(self):

        if not self.running:
            return False

        self.running = False
        self.last_update = None

        return True

    # =====================================
    # STEP
    # =====================================

    def step(self, dt_seconds=1.0):

        if dt_seconds <= 0:
            raise ValueError(
                "Il passo temporale deve essere positivo"
            )

        simulated_dt = dt_seconds * self.time_scale

        next_time = self.simulation_time + simulated_dt

        if self.scheduler:
            self.scheduler.update(next_time)

        self.manager.update_all(simulated_dt)

        self.simulation_time = next_time

        self.total_cycles += 1

        return self.get_status()

    # =====================================
    # TICK
    # =====================================

    def tick(self):

        if not self.running:
            return None

        now = time.monotonic()

        if self.last_update is None:
            self.last_update = now
            return None

        dt = now - self.last_update

        self.last_update = now

        return self.step(dt)

    # =====================================
    # RESET
    # =====================================

    def reset(self):

        if self.running:
            raise RuntimeError(
                "Arrestare la simulazione prima del reset"
            )

        self.simulation_time = self.initial_time
        self.total_cycles = 0
        self.last_update = None

        if self.scheduler:
            self.scheduler.previous_states.clear()
            self.scheduler.transition_log.clear()

    # =====================================
    # STATO
    # =====================================

    def get_status(self):

        daily_seconds = self.simulation_time % 86400

        hours = int(daily_seconds // 3600)
        minutes = int((daily_seconds % 3600) // 60)
        seconds = int(daily_seconds % 60)

        status = {
            "running": self.running,
            "simulation_time_seconds": round(
                self.simulation_time, 2
            ),
            "simulation_hour": hours,
            "simulation_minute": minutes,
            "simulation_second": seconds,
            "time_scale": self.time_scale,
            "total_cycles": self.total_cycles,
            "equipment": self.manager.get_summary()
        }

        if self.scheduler:
            status["scheduler"] = self.scheduler.get_status()

        return status

