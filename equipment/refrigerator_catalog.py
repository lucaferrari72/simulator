
from equipment.refrigerator import Refrigerator


REFRIGERATOR_CATALOG = {

    "44716": {
        "model": "Custom Marine - 1 porta",
        "nominal_power_kw": 0.90,
        "capacity_l": 650,
        "doors": 1
    },

    "44812": {
        "model": "Custom Marine - 1 porta",
        "nominal_power_kw": 0.90,
        "capacity_l": 650,
        "doors": 1
    },

    "44801": {
        "model": "Custom Marine - Tavolo 3 porte",
        "nominal_power_kw": 0.70,
        "capacity_l": 475,
        "doors": 3
    },

    "44807": {
        "model": "Custom Marine - 2 porte",
        "nominal_power_kw": 1.20,
        "capacity_l": 1350,
        "doors": 2
    },

    "44808": {
        "model": "Custom Marine - 2 porte",
        "nominal_power_kw": 1.20,
        "capacity_l": 1350,
        "doors": 2
    }
}


def create_refrigerator(equipment_id):

    equipment_id = str(equipment_id)

    if equipment_id not in REFRIGERATOR_CATALOG:
        raise ValueError(
            f"Frigorifero sconosciuto: {equipment_id}"
        )

    config = REFRIGERATOR_CATALOG[equipment_id]

    return Refrigerator(
        equipment_id=equipment_id,
        model=config["model"],
        nominal_power_kw=config["nominal_power_kw"],
        capacity_l=config["capacity_l"],
        doors=config["doors"]
    )


def create_all_refrigerators():

    return {
        equipment_id: create_refrigerator(equipment_id)
        for equipment_id in REFRIGERATOR_CATALOG
    }
