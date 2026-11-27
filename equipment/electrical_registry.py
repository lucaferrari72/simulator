
"""
Registro elettrico centralizzato della cucina.

Raccoglie i dati dalle istanze delle apparecchiature.
Non duplica le definizioni dei cataloghi.

Rete generale:
    440 V trifase
    60 Hz

I dati mancanti rimangono None.
Non vengono inventati valori elettrici.
"""

from dataclasses import dataclass, asdict
from typing import Optional


NETWORK_REFERENCE = {
    "voltage_v": 440.0,
    "phases": 3,
    "frequency_hz": 60,
    "description": "Rete generale nave",
}

NETWORKS = {
    "main_440v": {
        "voltage_v": 440.0,
        "phases": 3,
        "frequency_hz": 60,
        "description": "Rete principale trifase",
    },

    "auxiliary_220v": {
        "voltage_v": 220.0,
        "phases": 1,
        "frequency_hz": 60,
        "description": "Rete autonoma monofase",
    },
}

EQUIPMENT_LINES = {
    "fryer": "cucina_calda",
    "induction": "cucina_calda",
    "oven": "cucina_calda",
    "infrared_grill": "cucina_calda",
    "frytop": "cucina_calda",
    "solid_top": "cucina_calda",
    "bratt_pan": "cucina_calda",
    "boiling_kettle": "cucina_calda",
    "dishwasher": "lavaggio",
    "refrigerator": "conservazione_frigorifera",
    "hood": None,
}


@dataclass
class ElectricalRecord:

    equipment_id: str
    category: str
    line: Optional[str]

    model: Optional[str]

    nominal_power_kw: Optional[float]
    voltage_v: Optional[float]
    phases: Optional[int]
    frequency_hz: Optional[float]
    power_factor: Optional[float]

    current_l1_a: Optional[float]
    current_l2_a: Optional[float]
    current_l3_a: Optional[float]

    data_source: str
    confidence: str

    def to_dict(self):
        return asdict(self)


def _get_attribute(obj, *names):
    """Legge il primo attributo disponibile."""

    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)

            if value is not None:
                return value

    return None


def _to_float(value):
    if value is None:
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _to_int(value):
    if value is None:
        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _identify_category(equipment):
    """Identifica la categoria dalla classe Python."""

    class_name = type(equipment).__name__.lower()

    categories = (
        "refrigerator",
        "dishwasher",
        "induction",
        "fryer",
        "oven",
        "infrared_grill",
        "frytop",
        "solid_top",
        "bratt_pan",
        "boiling_kettle",
        "hood",
    )

    for category in categories:
        if category.replace("_", "") in class_name.replace("_", ""):
            return category

    return "unknown"


def _calculate_current(power_kw, voltage_v, phases, power_factor):
    """
    Calcola la corrente nominale teorica.

    Per trifase assume carico equilibrato.
    Per monofase assume tensione di alimentazione disponibile.
    """

    if (
        power_kw is None
        or voltage_v is None
        or phases not in (1, 3)
        or power_factor is None
    ):
        return None

    if power_kw < 0 or voltage_v <= 0:
        return None

    if not 0 < power_factor <= 1:
        return None

    if phases == 3:
        import math

        return (
            power_kw * 1000
            / (math.sqrt(3) * voltage_v * power_factor)
        )

    return power_kw * 1000 / (voltage_v * power_factor)


def create_electrical_record(equipment, equipment_id=None):
    """Crea il record elettrico di una singola apparecchiatura."""

    equipment_id = str(
        equipment_id
        or _get_attribute(equipment, "equipment_id", "id")
        or ""
    )

    if not equipment_id:
        raise ValueError("Apparecchiatura senza identificativo")

    category = _identify_category(equipment)

    power = _to_float(
        _get_attribute(
            equipment,
            "nominal_power_kw",
            "rated_power_kw",
        )
    )

    voltage = _to_float(
        _get_attribute(
            equipment,
            "voltage_v",
            "rated_voltage_v",
        )
    )

    phases = _to_int(
        _get_attribute(
            equipment,
            "phases",
            "number_of_phases",
        )
    )

    frequency = _to_float(
        _get_attribute(
            equipment,
            "frequency_hz",
        )
    )

    power_factor = _to_float(
        _get_attribute(
            equipment,
            "power_factor",
            "cos_phi",
        )
    )

    model = _get_attribute(equipment, "model")

    current = _calculate_current(
        power,
        voltage,
        phases,
        power_factor,
    )

    currents = (
        _to_float(_get_attribute(equipment, "current_l1_a")),
        _to_float(_get_attribute(equipment, "current_l2_a")),
        _to_float(_get_attribute(equipment, "current_l3_a")),
    )

    if all(value is None for value in currents):
        currents = (
            (current, current, current)
            if phases == 3 and current is not None
            else (current, 0.0, 0.0)
            if current is not None
            else (None, None, None)
        )

    known = all(
        value is not None
        for value in (
            power,
            voltage,
            phases,
            frequency,
            power_factor,
        )
    )

    confidence = "CODE_DEFINED" if known else "INCOMPLETE"

    return ElectricalRecord(
        equipment_id=equipment_id,
        category=category,
        line=EQUIPMENT_LINES.get(category),
        model=str(model) if model is not None else None,
        nominal_power_kw=power,
        voltage_v=voltage,
        phases=phases,
        frequency_hz=frequency,
        power_factor=power_factor,
        current_l1_a=currents[0],
        current_l2_a=currents[1],
        current_l3_a=currents[2],
        data_source=type(equipment).__module__,
        confidence=confidence,
    )


def build_electrical_registry(equipment_instances):
    """
    Costruisce il registro a partire dalle istanze esistenti.

    equipment_instances:
        Dizionario {equipment_id: equipment}
        oppure iterabile di apparecchiature.
    """

    if isinstance(equipment_instances, dict):
        items = equipment_instances.items()
    else:
        items = (
            (
                _get_attribute(item, "equipment_id", "id"),
                item,
            )
            for item in equipment_instances
        )

    registry = {}

    for equipment_id, equipment in items:

        record = create_electrical_record(
            equipment,
            equipment_id,
        )

        if record.equipment_id in registry:
            raise ValueError(
                f"ID duplicato: {record.equipment_id}"
            )

        registry[record.equipment_id] = record.to_dict()

    return registry


def get_registry_summary(registry):
    """Restituisce il riepilogo dell'inventario."""

    total = len(registry)

    complete = sum(
        1 for item in registry.values()
        if item["confidence"] == "CODE_DEFINED"
    )

    incomplete = total - complete

    known_power = sum(
        item["nominal_power_kw"]
        for item in registry.values()
        if item["nominal_power_kw"] is not None
    )

    missing_power = sum(
        1 for item in registry.values()
        if item["nominal_power_kw"] is None
    )

    return {
        "total_equipment": total,
        "complete_electrical_records": complete,
        "incomplete_records": incomplete,
        "missing_power_records": missing_power,
        "known_nominal_power_kw": round(known_power, 3),
        "network_reference": NETWORK_REFERENCE.copy(),
    }


def export_registry(registry, filename="electrical_registry.json"):
    """Esporta il registro in formato JSON."""

    import json

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            {
                "network": NETWORK_REFERENCE,
                "equipment": registry,
                "summary": get_registry_summary(registry),
            },
            file,
            indent=4,
            ensure_ascii=False,
        )
