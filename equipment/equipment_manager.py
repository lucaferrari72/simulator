
class EquipmentManager:

    def __init__(self):

        self.equipment = {}

        # AUTO, FORCED_ON, FORCED_OFF
        self.operating_modes = {}

    # =====================================
    # REGISTRAZIONE
    # =====================================

    def add_equipment(self, equipment):

        equipment_id = str(equipment.equipment_id)

        if equipment_id in self.equipment:
            raise ValueError(
                f"ID apparecchiatura duplicato: {equipment_id}"
            )

        self.equipment[equipment_id] = equipment

        self.operating_modes[equipment_id] = "AUTO"

    def add_catalog(self, catalog):

        for equipment in catalog.values():
            self.add_equipment(equipment)

    # =====================================
    # RICERCA
    # =====================================

    def get_equipment(self, equipment_id):

        equipment_id = str(equipment_id)

        if equipment_id not in self.equipment:
            raise KeyError(
                f"Apparecchiatura non trovata: {equipment_id}"
            )

        return self.equipment[equipment_id]

    # =====================================
    # MODALITA' OPERATIVA
    # =====================================

    def get_mode(self, equipment_id):

        return self.operating_modes[str(equipment_id)]

    def set_mode(self, equipment_id, mode):

        equipment_id = str(equipment_id)

        if equipment_id not in self.equipment:
            raise KeyError(equipment_id)

        if mode not in ("AUTO", "FORCED_ON", "FORCED_OFF"):
            raise ValueError(f"Modalità non valida: {mode}")

        self.operating_modes[equipment_id] = mode

        equipment = self.get_equipment(equipment_id)

        if mode == "FORCED_ON":
            equipment.turn_on()

        elif mode == "FORCED_OFF":
            equipment.turn_off()

    def set_auto_state(self, equipment_id, state):

        equipment_id = str(equipment_id)

        if self.get_mode(equipment_id) != "AUTO":
            return False

        equipment = self.get_equipment(equipment_id)

        current = bool(
            equipment.get_data().get("is_on", False)
        )

        if state and not current:
            equipment.turn_on()

        elif not state and current:
            equipment.turn_off()

        return True

    # =====================================
    # AGGIORNAMENTO
    # =====================================

    def update_all(self, dt_seconds):

        if dt_seconds <= 0:
            raise ValueError(
                "Il tempo di aggiornamento deve essere positivo"
            )

        for equipment in self.equipment.values():
            equipment.update(dt_seconds)

    # =====================================
    # DATI APPARECCHIATURA
    # =====================================

    def get_equipment_data(self, equipment_id):

        equipment = self.get_equipment(equipment_id)

        data = equipment.get_data().copy()

        data["operating_mode"] = self.get_mode(equipment_id)

        return data

    def get_all_data(self):

        return {
            equipment_id: self.get_equipment_data(equipment_id)
            for equipment_id in self.equipment
        }

    # =====================================
    # RIEPILOGO
    # =====================================

    def get_summary(self):

        total_power = 0.0
        total_energy = 0.0

        active_equipment = 0
        alarm_equipment = 0

        for equipment_id, equipment in self.equipment.items():

            data = equipment.get_data()

            power = float(data.get("power_kw", 0.0) or 0.0)
            energy = float(data.get("energy_kwh", 0.0) or 0.0)

            total_power += power
            total_energy += energy

            if data.get("is_on", False):
                active_equipment += 1

            if data.get("alarm", False):
                alarm_equipment += 1

        return {
            "equipment_count": len(self.equipment),
            "active_equipment": active_equipment,
            "alarm_equipment": alarm_equipment,
            "total_power_kw": round(total_power, 3),
            "total_energy_kwh": round(total_energy, 4)
        }

    # =====================================
    # COMANDI MANUALI
    # =====================================

    def turn_on(self, equipment_id):

        self.set_mode(equipment_id, "FORCED_ON")

    def turn_off(self, equipment_id):

        self.set_mode(equipment_id, "FORCED_OFF")

    def restore_automatic(self, equipment_id):

        self.set_mode(equipment_id, "AUTO")

    # =====================================
    # RESET
    # =====================================

    def clear(self):

        self.equipment.clear()
        self.operating_modes.clear()

