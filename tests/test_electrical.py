

from equipment.fryer import Fryer

fryer = Fryer()

print("\nTEST ELETTRICO AMBACH 44422")
print("=" * 55)

# Accensione e primo aggiornamento
fryer.turn_on()
fryer.update(1)

data = fryer.get_electrical_data()

print(f"Tensione:       {data['voltage_v']:.1f} V")
print(f"Frequenza:      {data['frequency_hz']:.1f} Hz")
print(f"Fase L1:        {data['current_l1_a']:.2f} A")
print(f"Fase L2:        {data['current_l2_a']:.2f} A")
print(f"Fase L3:        {data['current_l3_a']:.2f} A")
print(f"Potenza:        {data['power_kw']:.2f} kW")
print(f"Energia:        {data['energy_kwh']:.5f} kWh")
print(f"Fattore potenza:{data['power_factor']:.2f}")

print("\nVERIFICA SPEGNIMENTO")

fryer.turn_off()

data = fryer.get_electrical_data()

print(f"Potenza dopo OFF: {data['power_kw']:.2f} kW")
print(f"Corrente L1 dopo OFF: {data['current_l1_a']:.2f} A")

print("\nTEST COMPLETATO")
