
"""
Registro elettrico centralizzato della cucina.

Raccoglie i dati dalle istanze delle apparecchiature.
Non duplica le definizioni dei cataloghi.

Reti elettriche di riferimento:
    440 V trifase - 60 Hz
    220 V monofase - 60 Hz

ATTENZIONE:
I dati presenti nel codice non sono automaticamente
dati certificati dal produttore.

I dati mancanti rimangono None.
Non vengono inventati valori elettrici.
"""

from dataclasses import dataclass, asdict
from typing import Optional
import math
import json


# ============================================================
# CONFIGURAZIONE RETI ELETTRICHE
# ============================================================

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

NETWORK_REFERENCE = {
    "main_voltage_v": 440.0,
    "auxiliary_voltage_v": 220.0,
    "frequency_hz": 60,
    "description": "Distribuzione elettrica cucina nave",
}


# ============================================================
# ASSOCIAZIONE APPARECCHIATURE ALLE RETI
# ============================================================

EQUIPMENT_NETWORKS = {
    "fryer": "main_440v",
    "induction": "auxiliary_220v",
    "oven": "main_440v",
    "infrared_grill": "main_440v",
    "frytop": "main_440v",
    "solid_top": "main_440v",
    "bratt_pan": "main_440v",
    "boiling_kettle": "main_440v",
    "dishwasher": "main_440v",
    "refrigerator": "auxiliary_220v",
    "hood": "auxiliary_220v",
}


# ============================================================
# ASSOCIAZIONE ALLE LINEE DELLA CUCINA
# ============================================================

EQUIPMENT_LINES = {
    "fryer": "cucina_calda",
    "induction": "cucina_calda",
    "oven": None,
    "infrared_grill": "cucina_calda",
    "frytop": "cucina_calda",
    "solid_top": "cucina_calda",
    "bratt_pan": "cucina_calda",
    "boiling_kettle": "cucina_calda",
    "dishwasher": "lavaggio",
    "refrigerator": "conservazione_frigorifera",
    "hood": None,
}


# ============================================================
# MODELLO DATI ELETTRICI
# ============================================================

@dataclass
class ElectricalRecord:

    equipment_id: str
    category: str
    line: Optional[str]
    network_id: Optional[str]

    model: Optional[str]

    nominal_power_kw: Optional[float]

    voltage_v: Optional[float]
    phases: Optional[int]
    frequency_hz: Optional[float]

    power_factor: Optional[float]

    nominal_current_a: Optional[float]

    current_l1_a: Optional[float]
    current_l2_a: Optional[float]
    current_l3_a: Optional[float]

    phase_assignment: Optional[str]

    data_source: str
    confidence: str

    def to_dict(self):
        return asdict(self)


# ============================================================
# FUNZIONI DI SUPPORTO
# ============================================================

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
        result = float(value)

        if not math.isfinite(result):
            return None

        return result

    except (ValueError, TypeError):
        return None


def _to_int(value):

    if value is None:
        return None

    try:
        result = int(value)

        if result != float(value):
            return None

        return result

    except (ValueError, TypeError):
        return None


# ============================================================
# IDENTIFICAZIONE CATEGORIA
# ============================================================

def _identify_category(equipment):
    """Identifica la categoria dalla classe Python."""

    class_name = type(equipment).__name__.lower()

    categories = (
        "refrigerator",
        "dishwasher",
        "induction",
        "infrared_grill",
        "boiling_kettle",
        "bratt_pan",
        "solid_top",
        "frytop",
        "fryer",
        "oven",
        "hood",
    )

    normalized_name = class_name.replace("_", "")

    for category in categories:

        normalized_category = category.replace("_", "")

        if normalized_category in normalized_name:
            return category

    return "unknown"


# ============================================================
# CALCOLO CORRENTE NOMINALE
# ============================================================

def _calculate_current(
    power_kw,
    voltage_v,
    phases,
    power_factor,
):
    """
    Calcola la corrente nominale teorica.

    Trifase:
        I = P / (sqrt(3) * V * cos(phi))

    Monofase:
        I = P / (V * cos(phi))

    Il calcolo presuppone:
        - Potenza attiva in ingresso.
        - Fattore di potenza attendibile.
        - Alimentazione sinusoidale.
        - Carico trifase equilibrato nel caso trifase.

    Non rappresenta la corrente istantanea durante
    i cicli operativi dell'apparecchiatura.
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

        return (
            power_kw * 1000
            / (
                math.sqrt(3)
                * voltage_v
                * power_factor
            )
        )

    return (
        power_kw * 1000
        / (voltage_v * power_factor)
    )


# ============================================================
# CLASSIFICAZIONE ATTENDIBILITA'
# ============================================================

def _classify_confidence(
    power,
    voltage,
    phases,
    frequency,
    power_factor,
):
    """
    La presenza di un dato nel codice non significa
    che sia stato verificato fisicamente.
    """

    if all(
        value is not None
        for value in (
            power,
            voltage,
            phases,
            frequency,
            power_factor,
        )
    ):
        return "CODE_DEFINED_UNVERIFIED"

    return "INCOMPLETE"


# ============================================================
# CREAZIONE RECORD ELETTRICO
# ============================================================

def create_electrical_record(
    equipment,
    equipment_id=None,
):
    """Crea il record elettrico di una singola apparecchiatura."""

    equipment_id = str(
        equipment_id
        or _get_attribute(
            equipment,
            "equipment_id",
            "id",
        )
        or ""
    )

    if not equipment_id:
        raise ValueError(
            "Apparecchiatura senza identificativo"
        )

    category = _identify_category(equipment)

    # --------------------------------------------------------
    # DATI ELETTRICI DELL'APPARECCHIATURA
    # --------------------------------------------------------

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

    model = _get_attribute(
        equipment,
        "model",
    )

    # --------------------------------------------------------
    # RETE DI ALIMENTAZIONE
    # --------------------------------------------------------

    network_id = EQUIPMENT_NETWORKS.get(category)

    # --------------------------------------------------------
    # VERIFICA COERENZA RETE E APPARECCHIATURA
    # --------------------------------------------------------

    network = NETWORKS.get(network_id)

    if network is not None:

        if voltage is not None:
            if not math.isclose(
                voltage,
                network["voltage_v"],
                rel_tol=0.0,
                abs_tol=0.1,
            ):
                raise ValueError(
                    f"Incoerenza tensione per "
                    f"{equipment_id}: "
                    f"{voltage} V contro "
                    f"{network['voltage_v']} V "
                    f"previsti dalla rete {network_id}"
                )

        if phases is not None:
            if phases != network["phases"]:
                raise ValueError(
                    f"Incoerenza numero fasi per "
                    f"{equipment_id}: "
                    f"{phases} contro "
                    f"{network['phases']} previste"
                )

        if frequency is not None:
            if not math.isclose(
                frequency,
                network["frequency_hz"],
                rel_tol=0.0,
                abs_tol=0.1,
            ):
                raise ValueError(
                    f"Incoerenza frequenza per "
                    f"{equipment_id}"
                )

    # --------------------------------------------------------
    # CORRENTE NOMINALE
    # --------------------------------------------------------

    current = _calculate_current(
        power,
        voltage,
        phases,
        power_factor,
    )

    # --------------------------------------------------------
    # DISTRIBUZIONE SULLE FASI
    # --------------------------------------------------------

    # Non conosciamo la distribuzione fisica dei carichi
    # monofase sulle fasi della rete principale.
    #
    # Anche per i carichi trifase, la corrente calcolata
    # è una corrente teorica di linea, non una misura.

    current_l1 = None
    current_l2 = None
    current_l3 = None

    phase_assignment = None

    confidence = _classify_confidence(
        power,
        voltage,
        phases,
        frequency,
        power_factor,
    )

    # --------------------------------------------------------
    # RECORD
    # --------------------------------------------------------

    return ElectricalRecord(

        equipment_id=equipment_id,

        category=category,

        line=EQUIPMENT_LINES.get(category),

        network_id=network_id,

        model=(
            str(model)
            if model is not None
            else None
        ),

        nominal_power_kw=power,

        voltage_v=voltage,

        phases=phases,

        frequency_hz=frequency,

        power_factor=power_factor,

        nominal_current_a=current,

        current_l1_a=current_l1,

        current_l2_a=current_l2,

        current_l3_a=current_l3,

        phase_assignment=phase_assignment,

        data_source=type(equipment).__module__,

        confidence=confidence,
    )


# ============================================================
# COSTRUZIONE REGISTRO COMPLETO
# ============================================================

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
                _get_attribute(
                    item,
                    "equipment_id",
                    "id",
                ),
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


# ============================================================
# RIEPILOGO REGISTRO
# ============================================================

def get_registry_summary(registry):
    """Restituisce il riepilogo dell'inventario."""

    total = len(registry)

    complete = sum(
        1
        for item in registry.values()
        if item["confidence"] == "CODE_DEFINED_UNVERIFIED"
    )

    incomplete = total - complete

    known_power = sum(
        item["nominal_power_kw"]
        for item in registry.values()
        if item["nominal_power_kw"] is not None
    )

    missing_power = sum(
        1
        for item in registry.values()
        if item["nominal_power_kw"] is None
    )

    network_summary = {}

    for network_id, network in NETWORKS.items():

        network_summary[network_id] = {
            "description": network["description"],
            "voltage_v": network["voltage_v"],
            "phases": network["phases"],
            "frequency_hz": network["frequency_hz"],
            "equipment_count": 0,
            "nominal_power_kw": 0.0,
            "missing_power_count": 0,
        }

    network_summary["unassigned"] = {
        "equipment_count": 0,
        "nominal_power_kw": 0.0,
        "missing_power_count": 0,
    }

    for item in registry.values():

        network_id = item["network_id"] or "unassigned"

        if network_id not in network_summary:
            network_summary[network_id] = {
                "equipment_count": 0,
                "nominal_power_kw": 0.0,
                "missing_power_count": 0,
            }

        entry = network_summary[network_id]

        entry["equipment_count"] += 1

        if item["nominal_power_kw"] is not None:

            entry["nominal_power_kw"] += (
                item["nominal_power_kw"]
            )

        else:

            entry["missing_power_count"] += 1

    for entry in network_summary.values():

        entry["nominal_power_kw"] = round(
            entry["nominal_power_kw"],
            3,
        )

    return {

        "total_equipment": total,

        "complete_electrical_records": complete,

        "incomplete_records": incomplete,

        "missing_power_records": missing_power,

        "known_nominal_power_kw": round(
            known_power,
            3,
        ),

        "network_reference": NETWORK_REFERENCE.copy(),

        "networks": network_summary,
    }


# ============================================================
# ESPORTAZIONE JSON
# ============================================================

def export_registry(
    registry,
    filename="electrical_registry.json",
):
    """Esporta il registro in formato JSON."""

    data = {

        "network_reference": NETWORK_REFERENCE,

        "networks": NETWORKS,

        "equipment": registry,

        "summary": get_registry_summary(registry),
    }

    with open(
        filename,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )
