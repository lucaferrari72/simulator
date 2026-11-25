
from equipment.induction import InductionCooktop


INDUCTION_CATALOG = [
    "44458",
    "44557",
    "44558",
    "44710",
    "44810",
]


def create_induction(equipment_id):

    if equipment_id not in INDUCTION_CATALOG:
        raise ValueError(
            f"Codice induzione sconosciuto: {equipment_id}"
        )

    return InductionCooktop(
        equipment_id=equipment_id
    )


def create_all_induction():

    return {
        equipment_id: create_induction(equipment_id)
        for equipment_id in INDUCTION_CATALOG
    }
