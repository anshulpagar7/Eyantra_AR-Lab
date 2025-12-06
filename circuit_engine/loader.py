# circuit_engine/loader.py

import json
from pathlib import Path
from typing import Union, Tuple, List

from .components import VoltageSource, Resistor, Led
from .circuit import SeriesCircuit


def load_series_circuit_from_json(path: Union[str, Path]) -> Tuple[SeriesCircuit, List[dict]]:
    """
    Load a SeriesCircuit and step-by-step instructions from a JSON file.
    Returns:
      (SeriesCircuit object, steps list)
    """

    # Open the JSON file
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # ---------------------------
    # Build the voltage source
    # ---------------------------
    src_data = data["source"]
    source = VoltageSource(
        name=src_data["name"],
        voltage=float(src_data["voltage"])
    )

    # ---------------------------
    # Build resistors
    # ---------------------------
    resistors = []
    for r in data.get("resistors", []):
        resistors.append(
            Resistor(
                name=r["name"],
                resistance=float(r["resistance"])
            )
        )

    # ---------------------------
    # Build LEDs
    # ---------------------------
    leds = []
    for led in data.get("leds", []):
        leds.append(
            Led(
                name=led["name"],
                forward_voltage=float(led["forward_voltage"]),
                max_current=float(led["max_current"])
            )
        )

    # ---------------------------
    # Create the circuit object
    # ---------------------------
    circuit = SeriesCircuit(
        source=source,
        resistors=resistors,
        leds=leds
    )

    # ---------------------------
    # Load step-by-step instructions
    # ---------------------------
    steps = data.get("steps", [])

    # Return BOTH circuit and steps
    return circuit, steps
