
from equipment.solid_top import SolidTop


SOLID_TOP_CATALOG = [
    "44424",
]


def create_solid_top(equipment_id):

    if equipment_id not in SOLID_TOP_CATALOG:
        raise ValueError(
            f"Solid Top sconosciuto: {equipment_id}"
        )

    return SolidTop(
        equipment_id=equipment_id
    )


def create_all_solid_tops():

    return {
        equipment_id: create_solid_top(equipment_id)
        for equipment_id in SOLID_TOP_CATALOG
    }
