
from equipment.fryer import Fryer


fryer = Fryer()

print("\nTEST FRIGGITRICE AMBACH")
print("=" * 45)

print("Identificazione:")
print(fryer.equipment_id)
print(fryer.manufacturer)
print(fryer.model)

print("\nAccensione friggitrice")

fryer.turn_on()

for second in range(1, 11):

    fryer.update(1.0)

    data = fryer.get_data()

    print(
        f"Secondo {second:02d} | "
        f"Temperatura: {data['oil_temperature']:.2f} °C | "
        f"Potenza: {data['power_kw']:.2f} kW | "
        f"Corrente L1: {data['current_l1_a']:.2f} A | "
        f"Riscaldamento: {data['is_heating']}"
    )

print("\nTEST COMPLETATO")
