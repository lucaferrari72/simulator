
from equipment.fryer import Fryer


FRYER_CATALOG = {

    "44422": {
        "model": "A-9EF1/60-24-MA",
        "power": 24.0,
        "capacity": 32.0,
        "baskets": 2,
    },

    "44515": {
        "model": "A-8EF1/60-24-MA",
        "power": 24.0,
        "capacity": 32.0,
        "baskets": 2,
    },

    "44516": {
        "model": "A-8EF1/40-10-MA",
        "power": 10.0,
        "capacity": 16.0,
        "baskets": 1,
    },
}


def create_fryer(equipment_id):

    config = FRYER_CATALOG[equipment_id]

    return Fryer(
        equipment_id=equipment_id,
        model=config["model"],
        nominal_power_kw=config["power"],
        oil_capacity_l=config["capacity"],
        basket_count=config["baskets"]
    )


def create_all_fryers():

    return {
        equipment_id: create_fryer(equipment_id)
        for equipment_id in FRYER_CATALOG
    }
