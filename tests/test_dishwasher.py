
from equipment.dishwasher_catalog import create_all_dishwashers


dishwashers = create_all_dishwashers()

print("\nTEST MEIKO FV 40.2 MARINE")
print("=" * 55)

machine = dishwashers["44909"]

machine.turn_on()

# TEST AVVIO CICLO
print("\nTEST AVVIO CICLO")

machine.set_cycle_duration(90)

result = machine.start_cycle()

print(f"Avvio accettato: {result}")
print(f"Stato: {machine.state}")

# TEST RIEMPIMENTO E RISCALDAMENTO
print("\nTEST RIEMPIMENTO E RISCALDAMENTO")

for _ in range(6000):

    machine.update(1.0)

    if machine.state == "WASHING":
        break

data = machine.get_data()

print(f"Stato: {data['state']}")
print(f"Acqua vasca: {data['tank_water_l']:.2f} L")
print(f"Temperatura vasca: {data['tank_temperature']:.2f} °C")
print(f"Temperatura boiler: {data['boiler_temperature']:.2f} °C")
print(f"Potenza: {data['power_kw']:.2f} kW")

# TEST CICLO COMPLETO
print("\nTEST CICLO LAVAGGIO")

for _ in range(100):

    machine.update(1.0)

    if machine.state == "COMPLETE":
        break

data = machine.get_data()

print(f"Stato finale: {data['state']}")
print(f"Cicli completati: {data['cycles_completed']}")
print(f"Pompa attiva: {data['wash_pump_on']}")
print(f"Energia: {data['energy_kwh']:.4f} kWh")

# TEST ALLARME
print("\nTEST ALLARME")

machine.set_fault(101)

data = machine.get_data()

print(f"Allarme: {data['alarm']}")
print(f"Codice: {data['alarm_code']}")
print(f"Potenza: {data['power_kw']:.2f} kW")

# TEST RESET ALLARME
print("\nTEST RESET ALLARME")

machine.reset_alarm()

data = machine.get_data()

print(f"Allarme: {data['alarm']}")
print(f"Codice: {data['alarm_code']}")

# TEST SECONDA MACCHINA
print("\nTEST SECONDA LAVASTOVIGLIE")

machine_2 = dishwashers["44919"]

machine_2.turn_on()
machine_2.start_cycle()

print(f"ID: {machine_2.equipment_id}")
print(f"Stato: {machine_2.state}")

print("\nTEST COMPLETATO")
