
from equipment.refrigerator_catalog import (
    create_all_refrigerators
)


refrigerators = create_all_refrigerators()

print("\nTEST FRIGORIFERI DE WAVE")
print("=" * 60)

# TEST CATALOGO
print("\nTEST CATALOGO")

for equipment_id, refrigerator in refrigerators.items():

    print(
        equipment_id,
        refrigerator.model,
        refrigerator.capacity_l,
        "L",
        refrigerator.nominal_power_kw,
        "kW"
    )

# TEST FRIGORIFERO
print("\nTEST RAFFREDDAMENTO")

fridge = refrigerators["44716"]

fridge.turn_on()
fridge.set_temperature(4)

# Simuliamo temperatura iniziale elevata
fridge.temperature = 15.0

for _ in range(600):
    fridge.update(1.0)

data = fridge.get_data()

print(f"Temperatura: {data['temperature']} °C")
print(f"Setpoint: {data['setpoint']} °C")
print(f"Raffreddamento: {data['cooling_on']}")
print(f"Stato: {data['state']}")
print(f"Potenza: {data['power_kw']:.2f} kW")

# TEST APERTURA PORTA
print("\nTEST PORTA APERTA")

fridge.set_door(True)

for _ in range(90):
    fridge.update(1.0)

data = fridge.get_data()

print(f"Porta aperta: {data['door_open']}")
print(f"Allarme porta: {data['door_alarm']}")
print(f"Temperatura: {data['temperature']} °C")
print(f"Stato: {data['state']}")

# TEST CHIUSURA PORTA
print("\nTEST CHIUSURA PORTA")

fridge.set_door(False)

for _ in range(10):
    fridge.update(1.0)

data = fridge.get_data()

print(f"Porta aperta: {data['door_open']}")
print(f"Stato: {data['state']}")

# TEST SBRINAMENTO MANUALE
print("\nTEST SBRINAMENTO")

result = fridge.start_defrost()

print(f"Avvio sbrinamento: {result}")

for _ in range(30):
    fridge.update(1.0)

data = fridge.get_data()

print(f"Sbrinamento attivo: {data['defrost_active']}")
print(f"Temperatura: {data['temperature']} °C")
print(f"Potenza: {data['power_kw']:.2f} kW")
print(f"Stato: {data['state']}")

# TEST ALLARME TEMPERATURA
print("\nTEST ALLARME TEMPERATURA")

fridge.stop_defrost()
fridge.temperature = 12.0

fridge.update(1.0)

data = fridge.get_data()

print(f"Allarme: {data['alarm']}")
print(f"Codice: {data['alarm_code']}")
print(f"Stato: {data['state']}")

# TEST INDIPENDENZA
print("\nTEST INDIPENDENZA FRIGORIFERI")

fridge_2 = refrigerators["44801"]

fridge_2.turn_on()

print(f"ID: {fridge_2.equipment_id}")
print(f"Temperatura: {fridge_2.temperature} °C")
print(f"Capacità: {fridge_2.capacity_l} L")

print("\nTEST COMPLETATO")
