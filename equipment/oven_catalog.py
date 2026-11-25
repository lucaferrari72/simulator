
from equipment.oven import CombiOven


OVEN_CATALOG = [
    "44503",
    "44529",
    "44531",
]


def create_oven(equipment_id):

    if equipment_id not in OVEN_CATALOG:
        raise ValueError(
            f"Codice forno sconosciuto: {equipment_id}"
        )

    return CombiOven(
        equipment_id=equipment_id
    )


def create_all_ovens():

    return {
        equipment_id: create_oven(equipment_id)
        for equipment_id in OVEN_CATALOG
    }
