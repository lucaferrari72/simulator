import json
import math
from pathlib import Path


class DailySchedule:

    def __init__(self, config_path="profiles/daily_operation.json"):

        self.config_path = Path(config_path)

        if not self.config_path.is_absolute():
            project_root = Path(__file__).resolve().parent.parent
            self.config_path = project_root / self.config_path

        self.config = self.load()

    def load(self):

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configurazione non trovata: {self.config_path}"
            )

        with self.config_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def time_to_minutes(value):

        hours, minutes = map(int, value.split(":"))

        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError(f"Orario non valido: {value}")

        return hours * 60 + minutes

    def get_start_time(self):

        return self.config.get(
            "simulation", {}
        ).get("start_time", "03:30")

    def get_start_seconds(self):

        return self.time_to_minutes(
            self.get_start_time()
        ) * 60

    # =====================================
    # PASSEGGERI / AFFLUSO GIORNALIERO
    # =====================================

    def get_passengers(self):

        passengers = self.config.get("passengers", 3000)

        # Formato legacy: numero intero
        if isinstance(passengers, (int, float)):
            return int(passengers)

        # Formato nuovo: oggetto con total e flow
        return int(passengers.get("total", 3000))

    def get_passenger_flow(self):

        passengers = self.config.get("passengers", {})

        if isinstance(passengers, (int, float)):
            return []

        flow = []

        for service in passengers.get("flow", []):

            start = self.time_to_minutes(service["start"])
            end = self.time_to_minutes(service["end"])
            count = int(service.get("count", 0))

            flow.append({
                "name": service.get("name", "servizio"),
                "start_minute": start,
                "end_minute": end,
                "count": count
            })

        return sorted(flow, key=lambda s: s["start_minute"])

    def get_ramp_minutes(self):

        value = int(
            self.config.get("simulation", {}).get("ramp_minutes", 30)
        )

        if value < 0:
            raise ValueError("ramp_minutes non puo' essere negativo")

        return value

    @staticmethod
    def _service_load(service, minute):

        """Carico istantaneo [0..1] di un servizio a un minuto dato."""

        start = service["start_minute"]
        end = service["end_minute"]
        duration = end - start

        if duration <= 0:
            return 0.0

        if not (start <= minute < end):
            return 0.0

        progress = (minute - start) / duration

        # Sinusoide mezza-onda: 0 all'inizio, 1 a meta', ~0 alla fine
        return math.sin(math.pi * progress)

    def get_active_passengers(self, simulation_seconds):

        """
        Passeggeri presenti in cucina in un dato istante.

        Afflusso NON costante: ogni servizio (colazione/pranzo/cena)
        segue una curva a campana (sinusoide mezza-onda) sulla propria
        finestra oraria, con rampa minima garantita da ramp_minutes.

        I servizi sono sommati perche' le finestre sono disgiunte;
        se due finestre si sovrappongono i carichi si accumulano
        (es. buffet pomeridiano durante il pranzo).
        """

        minute = int(simulation_seconds // 60) % 1440
        ramp = self.get_ramp_minutes()

        present = 0

        for service in self.get_passenger_flow():

            load = self._service_load(service, minute)

            if load <= 0:
                continue

            # Nelle prime/ultime ramp_minutes la presenza e' limitata
            # dalla salita/discesa lineare (afflusso graduale)
            if ramp > 0:
                elapsed = minute - service["start_minute"]
                remaining = service["end_minute"] - minute
                linear_cap = min(elapsed, remaining) / ramp
                load = min(load, linear_cap)

            present += int(round(service["count"] * load))

        return present

    def get_service_at(self, simulation_seconds):

        minute = int(simulation_seconds // 60) % 1440

        for service in self.get_passenger_flow():
            if service["start_minute"] <= minute < service["end_minute"]:
                return service["name"]

        return "fuori servizio"

    # =====================================
    # SIMULAZIONE
    # =====================================

    def get_time_scale(self):

        value = float(
            self.config.get("simulation", {}).get(
                "time_scale", 1.0
            )
        )

        if value <= 0:
            raise ValueError("time_scale deve essere positivo")

        return value

    def get_windows(self, category):

        return self.config.get(
            "equipment_profiles", {}
        ).get(category, [])

    def is_time_active(self, windows, minute):

        minute %= 1440

        for window in windows:

            start = self.time_to_minutes(window["start"])
            end = self.time_to_minutes(window["end"])

            # Fascia di 24 ore
            if start == end:
                return True

            # Fascia normale
            if start < end:

                if start <= minute < end:
                    return True

            # Fascia che attraversa mezzanotte
            else:

                if minute >= start or minute < end:
                    return True

        return False
