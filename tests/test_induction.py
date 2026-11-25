
from equipment.induction_catalog import create_all_induction


cooktops = create_all_induction()

print("\nTEST PIASTRE A INDUZIONE GARLAND")
print("=" * 55)

for equipment_id, cooktop in cooktops.items():

    cooktop.turn_on()
    cooktop.set_level(12)

    for _ in range(10):
        cooktop.update(1.0)

    data = cooktop.get_data()

    print(f"\nCodice: {equipment_id}")
    print(f"Modello: {data['model']}")
    print(f"Livello: {data['power_level']}")
    print(f"Potenza: {data['power_kw']:.3f} kW")
    print(f"Corrente L1: {data['current_l1_a']:.2f} A")
    print(f"Temperatura pentola: {data['pan_temperature']:.2f} °C")
    print(f"Energia: {data['energy_kwh']:.5f} kWh")

print("\nTEST COMPLETATO")
