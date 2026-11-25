
from equipment.equipment_loader import create_equipment_manager
from simulation_engine import SimulationEngine


print("\nMARINE KITCHEN SIMULATOR")
print("TEST SIMULATION ENGINE")
print("=" * 55)


# 1. CREAZIONE SISTEMA
manager = create_equipment_manager()

engine = SimulationEngine(manager)


# 2. STATO INIZIALE
print("\nSTATO INIZIALE")

print(engine.get_status())


# 3. ACCENSIONE FRIGGITRICE
print("\nACCENSIONE FRIGGITRICE")

manager.turn_on("44422")


# 4. AGGIORNAMENTO SIMULAZIONE
print("\nAVANZAMENTO SIMULAZIONE")

for second in range(60):

    engine.step(1.0)


# 5. LETTURA DATI FRIGGITRICE
print("\nDATI FRIGGITRICE")

data = manager.get_equipment_data("44422")

for key, value in data.items():

    print(f"{key}: {value}")


# 6. STATO GENERALE
print("\nSTATO GENERALE")

status = engine.get_status()

for key, value in status.items():

    print(f"{key}: {value}")


# 7. TEST AVVIO E ARRESTO
print("\nTEST START / STOP")

print("Avvio:", engine.start())

print("In esecuzione:", engine.running)

print("Arresto:", engine.stop())

print("In esecuzione:", engine.running)


# 8. TEST AGGIORNAMENTO DOPO STOP
print("\nTEST AGGIORNAMENTO MANUALE")

engine.step(1.0)

print(engine.get_status())


print("\nTEST COMPLETATO")
