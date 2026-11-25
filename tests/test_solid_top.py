
from equipment.solid_top_catalog import create_all_solid_tops


solid_tops = create_all_solid_tops()

print("\nTEST AMBACH SOLID TOP")
print("=" * 55)

solid_top = solid_tops["44424"]

solid_top.turn_on()

# IMPOSTAZIONE TEMPERATURE
solid_top.set_zone_temperature(1, 200)
solid_top.set_zone_temperature(2, 250)
solid_top.set_zone_temperature(3, 180)
solid_top.set_zone_temperature(4, 300)

# TEST ZONA 1
print("\nTEST ZONA 1")

solid_top.set_zone(1, True)

for _ in range(60):
    solid_top.update(1.0)

data = solid_top.get_data()

print(f"Potenza totale: {data['power_kw']:.2f} kW")
print(f"Corrente L1: {data['current_l1_a']:.2f} A")

for i in range(4):
    print(
        f"Zona {i+1}: "
        f"{data['zone_temperature'][i]:.2f} °C"
    )

# TEST QUATTRO ZONE
print("\nTEST QUATTRO ZONE")

for zone in range(1, 5):
    solid_top.set_zone(zone, True)

for _ in range(60):
    solid_top.update(1.0)

data = solid_top.get_data()

print(f"Potenza totale: {data['power_kw']:.2f} kW")
print(f"Corrente L1: {data['current_l1_a']:.2f} A")

for i in range(4):
    print(
        f"Zona {i+1}: "
        f"{data['zone_temperature'][i]:.2f} °C "
        f"(Setpoint: {data['zone_setpoint'][i]} °C)"
    )

print(f"Energia: {data['energy_kwh']:.4f} kWh")

# TEST SPEGNIMENTO
print("\nTEST SPEGNIMENTO")

solid_top.turn_off()

data = solid_top.get_data()

print(f"Acceso: {data['is_on']}")
print(f"Potenza: {data['power_kw']:.2f} kW")

print("\nTEST COMPLETATO")
