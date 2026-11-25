
from equipment.boiling_kettle_catalog import (
    create_all_boiling_kettles
)


kettles = create_all_boiling_kettles()

print("\nTEST AMBACH BOILING KETTLE")
print("=" * 55)

kettle = kettles["44511"]

kettle.turn_on()

kettle.set_contents(80)
kettle.set_temperature(100)

# TEST RISCALDAMENTO
print("\nTEST RISCALDAMENTO")

for _ in range(3600):
    kettle.update(1.0)

data = kettle.get_data()

print(f"Potenza: {data['power_kw']:.2f} kW")
print(f"Corrente L1: {data['current_l1_a']:.2f} A")

print(
    f"Temperatura liquido: "
    f"{data['liquid_temperature']:.2f} °C"
)

print(
    f"Temperatura intercapedine: "
    f"{data['jacket_temperature']:.2f} °C"
)

print(f"Setpoint: {data['setpoint']:.2f} °C")
print(f"Ebollizione: {data['is_boiling']}")

print(f"Energia: {data['energy_kwh']:.4f} kWh")

# TEST TERMOSTATO
print("\nTEST TERMOSTATO")

kettle.set_temperature(30)

for _ in range(600):
    kettle.update(1.0)

data = kettle.get_data()

print(f"Riscaldamento: {data['jacket_heating']}")
print(f"Temperatura liquido: {data['liquid_temperature']:.2f} °C")
print(f"Potenza: {data['power_kw']:.2f} kW")

# TEST INTERCAPEDINE
print("\nTEST INTERCAPEDINE")

print(
    f"Indice pressione simulato: "
    f"{data['jacket_pressure_index']:.2f}"
)

# TEST RIBALTAMENTO
print("\nTEST RIBALTAMENTO")

kettle.set_tilted(True)

data = kettle.get_data()

print(f"Ribaltato: {data['is_tilted']}")
print(f"Contenuto: {data['contents_l']:.2f} L")
print(f"Potenza: {data['power_kw']:.2f} kW")

# TEST RIPRISTINO
print("\nTEST RIPRISTINO")

kettle.set_tilted(False)
kettle.set_contents(50)

data = kettle.get_data()

print(f"Ribaltato: {data['is_tilted']}")
print(f"Contenuto: {data['contents_l']:.2f} L")

print("\nTEST COMPLETATO")
