
from equipment.base import BaseEquipment

equipment = BaseEquipment(
    equipment_id="TEST001",
    manufacturer="TEST",
    model="TEST MODEL",
    nominal_power_kw=24.0,
    voltage_v=440,
    phases=3
)

equipment.turn_on()
equipment.set_power(24.0)
equipment.update_electrical(3600)

print(equipment.get_electrical_data())
