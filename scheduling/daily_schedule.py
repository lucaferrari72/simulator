import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


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
    def time_to_minutes(value: str) -> int:
        if not isinstance(value, str):
            raise ValueError(f"Orario deve essere una stringa, ricevuto: {type(value)}")
        
        match = re.match(r"^(\d{1,2}):(\d{2})$", value)
        if not match:
            raise ValueError(f"Formato orario non valido (richiesto HH:MM): {value}")
        
        hours, minutes = int(match.group(1)), int(match.group(2))
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError(f"Valori orario fuori range (0-23h, 0-59m): {value}")
            
        return hours * 60 + minutes

    def get_start_time(self):

        return self.config.get(
            "simulation", {}
        ).get("start_time", "05:30")

    def get_start_seconds(self):

        return self.time_to_minutes(
            self.get_start_time()
        ) * 60

    def get_passengers(self):

        return int(self.config.get("passengers", 3000))

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

