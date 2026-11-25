
from equipment.infrared_grill_catalog import (
    create_all_infrared_grills
)


grills = create_all_infrared_grills()

print("\nTEST AMBACH INFRARED GRILL")
print("=" * 55)

grill = grills["044519A"]

grill.turn_on()

# TEST ZONA 1
print("\nTEST ZONA 1")

grill.set_zone(1, True)
grill.set_zone(2, False)

for _ in range(60):
    grill.update(1.0)

data = grill.get_data()

print(f"Potenza: {data['power_kw']:.2f} kW")
print(f"Corrente L1: {data['current_l1_a']:.2f} A")
print(f"Temperatura zona 1: {data['zone_1_temperature']:.2f} °C")
print(f"Temperatura zona 2: {data['zone_2_temperature']:.2f} °C")

# TEST DUE ZONE
print("\nTEST DUE ZONE")

grill.set_zone(2, True)

for _ in range(60):
    grill.update(1.0)

data = grill.get_data()

print(f"Potenza: {data['power_kw']:.2f} kW")
print(f"Corrente L1: {data['current_l1_a']:.2f} A")
print(f"Temperatura zona 1: {data['zone_1_temperature']:.2f} °C")
print(f"Temperatura zona 2: {data['zone_2_temperature']:.2f} °C")
print(f"Energia: {data['energy_kwh']:.4f} kWh")

# TEST VASCA ACQUA
print("\nTEST VASCA ACQUA")

grill.water_level_l = 5.0
grill.set_water_valve(True)
grill.update(10.0)

print(f"Livello acqua: {grill.water_level_l:.2f} L")
print(f"Valvola acqua: {grill.water_valve_open}")

print("\nTEST COMPLETATO")
