
from equipment.oven_catalog import create_all_ovens


ovens = create_all_ovens()

print("\nTEST FORNI RATIONAL")
print("=" * 55)

for equipment_id, oven in ovens.items():

    oven.set_mode("hot_air")
    oven.set_chamber_temperature(180)

    oven.start_cooking()

    for _ in range(60):
        oven.update(1.0)

    data = oven.get_data()

    print(f"\nCodice: {equipment_id}")
    print(f"Modello: {data['model']}")
    print(f"Modalità: {data['mode']}")
    print(f"Potenza: {data['power_kw']:.2f} kW")
    print(f"Corrente L1: {data['current_l1_a']:.2f} A")
    print(
        f"Temperatura camera: "
        f"{data['chamber_temperature']:.2f} °C"
    )
    print(
        f"Temperatura cuore: "
        f"{data['core_temperature']:.2f} °C"
    )
    print(f"Energia: {data['energy_kwh']:.4f} kWh")

print("\nTEST COMPLETATO")
