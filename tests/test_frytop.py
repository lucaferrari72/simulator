
from equipment.frytop_catalog import create_all_frytops


frytops = create_all_frytops()

print("\nTEST AMBACH FRY-TOP")
print("=" * 55)

frytop = frytops["444210"]

frytop.turn_on()

# CONFIGURAZIONE TEMPERATURE
frytop.set_zone_temperature(1, 200)
frytop.set_zone_temperature(2, 180)

# TEST ZONA 1
print("\nTEST ZONA 1")

frytop.set_zone(1, True)
frytop.set_zone(2, False)

for _ in range(60):
    frytop.update(1.0)

data = frytop.get_data()

print(f"Potenza: {data['power_kw']:.2f} kW")
print(f"Corrente L1: {data['current_l1_a']:.2f} A")
print(f"Temperatura zona 1: {data['zone_1_temperature']:.2f} °C")
print(f"Temperatura zona 2: {data['zone_2_temperature']:.2f} °C")

# TEST DUE ZONE
print("\nTEST DUE ZONE")

frytop.set_zone(2, True)

for _ in range(60):
    frytop.update(1.0)

data = frytop.get_data()

print(f"Potenza: {data['power_kw']:.2f} kW")
print(f"Corrente L1: {data['current_l1_a']:.2f} A")
print(f"Temperatura zona 1: {data['zone_1_temperature']:.2f} °C")
print(f"Temperatura zona 2: {data['zone_2_temperature']:.2f} °C")
print(f"Energia: {data['energy_kwh']:.4f} kWh")

# TEST SPEGNIMENTO
print("\nTEST SPEGNIMENTO")

frytop.turn_off()

data = frytop.get_data()

print(f"Acceso: {data['is_on']}")
print(f"Potenza: {data['power_kw']:.2f} kW")

print("\nTEST COMPLETATO")
