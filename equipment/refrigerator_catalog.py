
"""Catalogo dei frigoriferi della cucina centrale."""

from equipment.refrigerator import Refrigerator


REFRIGERATOR_CATALOG = {

    "44716": {
        "model": "Custom Marine - 1 porta",
        "nominal_power_kw": 0.90,
        "capacity_l": 650,
        "doors": 1,
        "voltage_v": 220,

        # Da valorizzare con dati di targa
        "compressor_power_kw": None,
        "standby_power_kw": None,
        "defrost_power_kw": None,
    },

    "44812": {
        "model": "Custom Marine - 1 porta",
        "nominal_power_kw": 0.90,
        "capacity_l": 650,
        "doors": 1,
        "voltage_v": 220,

        "compressor_power_kw": None,
        "standby_power_kw": None,
        "defrost_power_kw": None,
    },

    "44801": {
        "model": "Custom Marine - Tavolo 3 porte",
        "nominal_power_kw": 0.70,
        "capacity_l": 475,
        "doors": 3,
        "voltage_v": 220,

        "compressor_power_kw": None,
        "standby_power_kw": None,
        "defrost_power_kw": None,
    },

    "44807": {
        "model": "Custom Marine - 2 porte",
        "nominal_power_kw": 1.20,
        "capacity_l": 1350,
        "doors": 2,
        "voltage_v": 220,

        "compressor_power_kw": None,
        "standby_power_kw": None,
        "defrost_power_kw": None,
    },

    "44808": {
        "model": "Custom Marine - 2 porte",
        "nominal_power_kw": 1.20,
        "capacity_l": 1350,
        "doors": 2,
        "voltage_v": 220,

        "compressor_power_kw": None,
        "standby_power_kw": None,
        "defrost_power_kw": None,
    },
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
        doors=config["doors"],
        voltage_v=config["voltage_v"],
        compressor_power_kw=config["compressor_power_kw"],
        standby_power_kw=config["standby_power_kw"],
        defrost_power_kw=config["defrost_power_kw"],
    )


def create_all_refrigerators():

    return {
        equipment_id: create_refrigerator(equipment_id)
        for equipment_id in REFRIGERATOR_CATALOG
    }
