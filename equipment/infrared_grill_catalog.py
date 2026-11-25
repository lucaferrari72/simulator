
from equipment.infrared_grill import InfraredGrill


INFRARED_GRILL_CATALOG = [
    "044519A",
]


def create_infrared_grill(equipment_id):

    if equipment_id not in INFRARED_GRILL_CATALOG:
        raise ValueError(
            f"Griglia sconosciuta: {equipment_id}"
        )

    return InfraredGrill(
        equipment_id=equipment_id
    )


def create_all_infrared_grills():

    return {
        equipment_id: create_infrared_grill(equipment_id)
        for equipment_id in INFRARED_GRILL_CATALOG
    }
