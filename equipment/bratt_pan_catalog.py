
from equipment.bratt_pan import BrattPan


BRATT_PAN_CATALOG = [
    "44504",
]


def create_bratt_pan(equipment_id):

    if equipment_id not in BRATT_PAN_CATALOG:
        raise ValueError(
            f"Brasiera sconosciuta: {equipment_id}"
        )

    return BrattPan(
        equipment_id=equipment_id
    )


def create_all_bratt_pans():

    return {
        equipment_id: create_bratt_pan(equipment_id)
        for equipment_id in BRATT_PAN_CATALOG
    }
