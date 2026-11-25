
from equipment.hood_catalog import create_all_hoods


hoods = create_all_hoods()

print("\nTEST CAPPE MARINE")
print("=" * 60)

# TEST CATALOGO
print("\nTEST CATALOGO")

for equipment_id, hood in hoods.items():

    print(
        equipment_id,
        hood.model,
        hood.hood_type,
        hood.nominal_power_kw,
        "kW"
    )

# =========================================
# TEST WATER WASH
# =========================================

print("\nTEST WATER WASH")

water_hood = hoods["44567"]

water_hood.turn_on()
water_hood.set_fan(True)

result = water_hood.start_wash()

print(f"Avvio lavaggio: {result}")

for _ in range(30):
    water_hood.update(1.0)

data = water_hood.get_data()

print(f"Stato: {data['state']}")
print(f"Ventilazione: {data['fan_on']}")
print(f"Elettrovalvola: {data['water_valve_open']}")
print(f"Lavaggio attivo: {data['wash_active']}")
print(f"Potenza: {data['power_kw']:.3f} kW")

# TEST FINE LAVAGGIO
print("\nTEST FINE LAVAGGIO")

for _ in range(100):
    water_hood.update(1.0)

data = water_hood.get_data()

print(f"Lavaggio attivo: {data['wash_active']}")
print(f"Elettrovalvola: {data['water_valve_open']}")

# =========================================
# TEST DRY GREASE
# =========================================

print("\nTEST DRY GREASE")

dry_hood = hoods["44569"]

dry_hood.turn_on()
dry_hood.set_lighting(True)
dry_hood.set_fan(True)

dry_hood.update(1.0)

data = dry_hood.get_data()

print(f"Illuminazione: {data['lighting_on']}")
print(f"Ventilazione: {data['fan_on']}")
print(f"Potenza: {data['power_kw']:.3f} kW")

# =========================================
# TEST FILTRI
# =========================================

print("\nTEST ALLARME FILTRI")

dry_hood.set_filter_condition(15)

dry_hood.update(1.0)

data = dry_hood.get_data()

print(f"Condizione filtro: {data['filter_condition']}%")
print(f"Allarme filtro: {data['filter_alarm']}")
print(f"Allarme generale: {data['alarm']}")
print(f"Codice: {data['alarm_code']}")

# TEST RIPRISTINO FILTRI
print("\nTEST RIPRISTINO FILTRI")

dry_hood.set_filter_condition(100)

result = dry_hood.reset_alarm()

dry_hood.update(1.0)

print(f"Reset eseguito: {result}")
print(f"Allarme: {dry_hood.alarm}")

# =========================================
# TEST TEPANYAKI
# =========================================

print("\nTEST TEPANYAKI")

teppanyaki = hoods["44954"]

teppanyaki.turn_on()
teppanyaki.set_lighting(True)

result = teppanyaki.set_uv_sensor(True)

teppanyaki.update(1.0)

data = teppanyaki.get_data()

print(f"Sensore UV: {data['uv_sensor_active']}")
print(f"Illuminazione: {data['lighting_on']}")
print(f"Potenza: {data['power_kw']:.3f} kW")
print(f"Stato: {data['state']}")

# =========================================
# TEST INDIPENDENZA
# =========================================

print("\nTEST INDIPENDENZA")

hood_2 = hoods["44958"]

hood_2.turn_on()
hood_2.set_lighting(False)
hood_2.set_uv_sensor(False)
hood_2.update(1.0)

print(f"ID: {hood_2.equipment_id}")
print(f"Illuminazione: {hood_2.lighting_on}")
print(f"Sensore UV: {hood_2.uv_sensor_active}")
print(f"Potenza: {hood_2.power_kw:.3f} kW")

print("\nTEST COMPLETATO")
