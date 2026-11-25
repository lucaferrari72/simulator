
from equipment.bratt_pan_catalog import create_all_bratt_pans


bratt_pans = create_all_bratt_pans()

print("\nTEST AMBACH BRATT PAN")
print("=" * 55)

pan = bratt_pans["44504"]

pan.turn_on()

pan.set_temperature(120)
pan.set_contents(80)

# TEST RISCALDAMENTO
print("\nTEST RISCALDAMENTO")

for _ in range(120):
    pan.update(1.0)

data = pan.get_data()

print(f"Potenza: {data['power_kw']:.2f} kW")
print(f"Corrente L1: {data['current_l1_a']:.2f} A")
print(f"Temperatura: {data['temperature']:.2f} °C")
print(f"Setpoint: {data['setpoint']:.2f} °C")
print(f"Contenuto: {data['contents_l']:.2f} L")
print(f"Energia: {data['energy_kwh']:.4f} kWh")

# TEST TERMOSTATO
print("\nTEST TERMOSTATO")

pan.set_temperature(25)

for _ in range(120):
    pan.update(1.0)

data = pan.get_data()

print(f"Riscaldamento attivo: {data['is_heating']}")
print(f"Potenza: {data['power_kw']:.2f} kW")

# TEST RIBALTAMENTO
print("\nTEST RIBALTAMENTO")

pan.set_tilted(True)

data = pan.get_data()

print(f"Brasiera ribaltata: {data['is_tilted']}")
print(f"Contenuto residuo: {data['contents_l']:.2f} L")
print(f"Potenza: {data['power_kw']:.2f} kW")

# TEST RIPRISTINO
print("\nTEST RIPRISTINO")

pan.set_tilted(False)
pan.set_contents(50)

data = pan.get_data()

print(f"Brasiera ribaltata: {data['is_tilted']}")
print(f"Nuovo contenuto: {data['contents_l']:.2f} L")

print("\nTEST COMPLETATO")
