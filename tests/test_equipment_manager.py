
from equipment.equipment_loader import create_equipment_manager


print("\nMARINE KITCHEN SIMULATOR")
print("TEST REGISTRO CENTRALE")
print("=" * 55)


# 1. CREAZIONE MANAGER
manager = create_equipment_manager()


# 2. ELENCO COMPLETO
print("\nELENCO APPARECCHIATURE")

for equipment_id, equipment in manager.equipment.items():

    print(
        f"{equipment_id:10} "
        f"{equipment.manufacturer:15} "
        f"{equipment.model}"
    )


# 3. RIEPILOGO
print("\nRIEPILOGO GENERALE")

summary = manager.get_summary()

for key, value in summary.items():

    print(f"{key}: {value}")


# 4. AGGIORNAMENTO SIMULAZIONE
print("\nAGGIORNAMENTO SIMULAZIONE")

for _ in range(60):

    manager.update_all(1.0)


# 5. VERIFICA POTENZE
print("\nPOTENZE APPARECCHIATURE")

total_power = 0.0

for equipment_id, equipment in manager.equipment.items():

    data = equipment.get_data()

    power = data.get("power_kw", 0.0)

    total_power += power

    print(
        f"{equipment_id}: "
        f"{power:.3f} kW"
    )


# 6. RIEPILOGO FINALE
print("\nRIEPILOGO FINALE")

print(
    f"Apparecchiature: {len(manager.equipment)}"
)

print(
    f"Potenza totale: {total_power:.3f} kW"
)

print(
    f"Energia totale: "
    f"{manager.get_summary()['total_energy_kwh']:.4f} kWh"
)


print("\nTEST COMPLETATO")
