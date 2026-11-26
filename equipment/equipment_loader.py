
import logging
from equipment.equipment_manager import EquipmentManager

# IMPORT CATALOGHI
from equipment.fryer_catalog import create_all_fryers
from equipment.induction_catalog import create_all_induction
from equipment.oven_catalog import create_all_ovens
from equipment.infrared_grill_catalog import create_all_infrared_grills
from equipment.frytop_catalog import create_all_frytops
from equipment.solid_top_catalog import create_all_solid_tops
from equipment.bratt_pan_catalog import create_all_bratt_pans
from equipment.boiling_kettle_catalog import create_all_boiling_kettles
from equipment.dishwasher_catalog import create_all_dishwashers
from equipment.refrigerator_catalog import create_all_refrigerators
from equipment.hood_catalog import create_all_hoods


logger = logging.getLogger(__name__)

# REGISTRO DEI CATALOGHI
CATALOG_FACTORIES = [
    create_all_fryers,
    create_all_induction,
    create_all_ovens,
    create_all_infrared_grills,
    create_all_frytops,
    create_all_solid_tops,
    create_all_bratt_pans,
    create_all_boiling_kettles,
    create_all_dishwashers,
    create_all_refrigerators,
    create_all_hoods,
]

def create_equipment_manager():
    manager = EquipmentManager()
    total_equipment = 0

    for factory in CATALOG_FACTORIES:
        catalog = factory()
        manager.add_catalog(catalog)
        count = len(catalog)
        total_equipment += count
        logger.info(f"Catalogo caricato: {factory.__name__} ({count} apparecchiature)")

    logger.info("-" * 50)
    logger.info(f"Totale apparecchiature caricate: {total_equipment}")
    return manager


