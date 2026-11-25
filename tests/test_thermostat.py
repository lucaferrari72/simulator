
from equipment.fryer import Fryer

fryer = Fryer()
fryer.turn_on()

print("\nVERIFICA TERMOSTATO AMBACH 44422")
print("-" * 75)

previous_state = fryer.is_heating
switch_count = 0

for second in range(1801):

    fryer.update(1)

    if fryer.is_heating != previous_state:
        switch_count += 1
        previous_state = fryer.is_heating

    if second % 60 == 0:
        print(
            f"Tempo: {second // 60:02d} min | "
            f"Olio: {fryer.oil_temperature:7.2f} °C | "
            f"Setpoint: {fryer.temperature_setpoint:.1f} °C | "
            f"Resistenze: {'ON' if fryer.is_heating else 'OFF'} | "
            f"Potenza: {fryer.power_kw:5.1f} kW | "
            f"Energia: {fryer.energy_kwh:6.2f} kWh"
        )

print("-" * 75)
print(f"Commutazioni termostato: {switch_count}")
print(f"Temperatura finale: {fryer.oil_temperature:.2f} °C")
print(f"Energia totale: {fryer.energy_kwh:.2f} kWh")
print("VERIFICA COMPLETATA")
