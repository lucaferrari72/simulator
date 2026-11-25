
from equipment.equipment_loader import create_equipment_manager

manager = create_equipment_manager()

print("\nVERIFICA INTERFACCE APPARECCHIATURE")
print("=" * 70)

for equipment_id, equipment in manager.equipment.items():

    data = equipment.get_data()

    print(f"\nID: {equipment_id}")
    print(f"Tipo: {type(equipment).__name__}")
    print(f"Produttore: {equipment.manufacturer}")
    print(f"Modello: {equipment.model}")
    print(f"Variabili: {list(data.keys())}")

print("\nVERIFICA COMPLETATA")
