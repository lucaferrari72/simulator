
from equipment.frytop import FryTop


FRYTOP_CATALOG = [
    "444210",
    "4442",
]


def create_frytop(equipment_id):

    if equipment_id not in FRYTOP_CATALOG:
        raise ValueError(
            f"Fry-top sconosciuto: {equipment_id}"
        )

    return FryTop(
        equipment_id=equipment_id
    )


def create_all_frytops():

    return {
        equipment_id: create_frytop(equipment_id)
        for equipment_id in FRYTOP_CATALOG
    }
