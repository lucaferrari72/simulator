
from equipment.dishwasher import Dishwasher


DISHWASHER_CATALOG = [
    "44909",
    "44919",
]


def create_dishwasher(equipment_id):

    if equipment_id not in DISHWASHER_CATALOG:
        raise ValueError(
            f"Lavastoviglie sconosciuta: {equipment_id}"
        )

    return Dishwasher(
        equipment_id=equipment_id
    )


def create_all_dishwashers():

    return {
        equipment_id: create_dishwasher(equipment_id)
        for equipment_id in DISHWASHER_CATALOG
    }
