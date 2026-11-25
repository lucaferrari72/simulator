
from equipment.fryer_catalog import create_all_fryers


fryers = create_all_fryers()

print("\nCATALOGO FRIGGITRICI AMBACH")
print("=" * 65)

for equipment_id, fryer in fryers.items():

    fryer.turn_on()
    fryer.update(1.0)

    data = fryer.get_data()

    print(f"\nCodice: {equipment_id}")
    print(f"Modello: {fryer.model}")
    print(f"Capacità: {fryer.oil_capacity_l} L")
    print(f"Cestelli: {fryer.basket_count}")
    print(f"Potenza nominale: {fryer.nominal_power_kw} kW")
    print(f"Potenza attuale: {data['power_kw']:.2f} kW")
    print(f"Corrente L1: {data['current_l1_a']:.2f} A")
    print(f"Temperatura: {data['oil_temperature']:.2f} °C")

print("\nTUTTE LE FRIGGITRICI CREATE CORRETTAMENTE")
