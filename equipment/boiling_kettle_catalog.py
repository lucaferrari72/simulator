
from equipment.boiling_kettle import BoilingKettle


BOILING_KETTLE_CATALOG = [
    "44511",
]


def create_boiling_kettle(equipment_id):

    if equipment_id not in BOILING_KETTLE_CATALOG:
        raise ValueError(
            f"Bollitore sconosciuto: {equipment_id}"
        )

    return BoilingKettle(
        equipment_id=equipment_id
    )


def create_all_boiling_kettles():

    return {
        equipment_id: create_boiling_kettle(equipment_id)
        for equipment_id in BOILING_KETTLE_CATALOG
    }
