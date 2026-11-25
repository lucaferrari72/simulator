
class EquipmentScheduler:

    def __init__(self, equipment_manager, daily_schedule):

        self.manager = equipment_manager
        self.schedule = daily_schedule

        self.enabled = True

        self.equipment_categories = {}
        self.transition_log = []

        self._classify_equipment()

    # =====================================
    # CLASSIFICAZIONE
    # =====================================

    def classify(self, equipment_id, equipment):

        searchable = " ".join([
            str(equipment_id),
            type(equipment).__name__,
            str(getattr(equipment, "manufacturer", "")),
            str(getattr(equipment, "model", ""))
        ]).lower().replace("-", "_").replace(" ", "_")

        categories = [
            ("refrigeration", [
                "refrigerator", "refrigeration",
                "refriger", "freezer", "fridge"
            ]),
            ("dishwashing", [
                "dishwasher", "dishwashing"
            ]),
            ("ventilation", [
                "hood", "ventilation", "extractor",
                "exhaust", "cappa"
            ]),
            ("boiling_kettles", [
                "boiling_kettle", "boilingkettle",
                "kettle", "boiler"
            ]),
            ("bratt_pans", [
                "bratt_pan", "brattpan", "bratt"
            ]),
            ("infrared_grills", [
                "infrared_grill", "infraredgrill",
                "infrared"
            ]),
            ("frytops", [
                "frytop", "fry_top"
            ]),
            ("solid_tops", [
                "solid_top", "solidtop"
            ]),
            ("induction", [
                "induction"
            ]),
            ("fryers", [
                "fryer", "fryers", "deep_fry"
            ]),
            ("ovens", [
                "oven", "ovens", "combi_oven",
                "convection"
            ])
        ]

        for category, keywords in categories:

            if any(keyword in searchable for keyword in keywords):
                return category

        return "unknown"

    def _classify_equipment(self):

        print("\n========== EQUIPMENT CLASSIFICATION ==========")

        totals = {}

        for equipment_id, equipment in self.manager.equipment.items():

            category = self.classify(
                equipment_id,
                equipment
            )

            self.equipment_categories[equipment_id] = category

            totals[category] = totals.get(category, 0) + 1

            print(f"{equipment_id:25} -> {category}")

        print("\n========== CATEGORY TOTALS ==========")

        for category, count in sorted(totals.items()):
            print(f"{category:20} : {count}")

        print("=====================================\n")

    # =====================================
    # STATO APPARECCHIATURA
    # =====================================

    def is_equipment_on(self, equipment_id):

        equipment = self.manager.get_equipment(equipment_id)

        return bool(
            equipment.get_data().get("is_on", False)
        )

    # =====================================
    # PROGRAMMAZIONE
    # =====================================

    def should_be_on(self, equipment_id, minute):

        category = self.equipment_categories[equipment_id]

        windows = self.schedule.get_windows(category)

        return self.schedule.is_time_active(
            windows,
            minute
        )

    # =====================================
    # AGGIORNAMENTO AUTOMATICO
    # =====================================

    def update(self, simulation_seconds):

        if not self.enabled:
            return

        minute = int(simulation_seconds // 60) % 1440

        for equipment_id in self.manager.equipment:

            # Rispetta i comandi manuali
            mode = self.manager.get_mode(equipment_id)

            if mode != "AUTO":
                continue

            desired_state = self.should_be_on(
                equipment_id,
                minute
            )

            current_state = self.is_equipment_on(
                equipment_id
            )

            if desired_state == current_state:
                continue

            self.manager.set_auto_state(
                equipment_id,
                desired_state
            )

            action = "ON" if desired_state else "OFF"

            self.transition_log.append({
                "time": simulation_seconds,
                "equipment_id": equipment_id,
                "category": self.equipment_categories[equipment_id],
                "action": action
            })

            print(
                f"[{minute // 60:02d}:{minute % 60:02d}] "
                f"{equipment_id} -> {action} AUTO"
            )

    # =====================================
    # CONTROLLO AUTOMAZIONE
    # =====================================

    def enable(self):

        self.enabled = True

    def disable(self):

        self.enabled = False

    # =====================================
    # REPORT
    # =====================================

    def get_status(self):

        active = sum(
            1 for equipment_id in self.manager.equipment
            if self.is_equipment_on(equipment_id)
        )

        return {
            "enabled": self.enabled,
            "equipment_count": len(self.equipment_categories),
            "active_equipment": active,
            "transitions": len(self.transition_log),
            "categories": self.equipment_categories.copy()
        }
