
from equipment.hood import Hood


HOOD_CATALOG = {

    "44567": {
        "model": "Water Wash Hood",
        "hood_type": "WATER_WASH",
        "nominal_power_kw": 0.10
    },

    "44569": {
        "model": "Dry Grease Hood",
        "hood_type": "DRY_GREASE",
        "nominal_power_kw": 0.078
    },

    "44954": {
        "model": "KFM Teppanyaki Hood",
        "hood_type": "TEPPANYAKI",
        "nominal_power_kw": 0.10
    },

    "44958": {
        "model": "KFM Teppanyaki Hood",
        "hood_type": "TEPPANYAKI",
        "nominal_power_kw": 0.10
    }
}


def create_hood(equipment_id):

    equipment_id = str(equipment_id)

    if equipment_id not in HOOD_CATALOG:
        raise ValueError(
            f"Cappa sconosciuta: {equipment_id}"
        )

    config = HOOD_CATALOG[equipment_id]

    return Hood(
        equipment_id=equipment_id,
        model=config["model"],
        hood_type=config["hood_type"],
        nominal_power_kw=config["nominal_power_kw"]
    )


def create_all_hoods():

    return {
        equipment_id: create_hood(equipment_id)
        for equipment_id in HOOD_CATALOG
    }
