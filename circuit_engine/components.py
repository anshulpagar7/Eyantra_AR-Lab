# circuit_engine/components.py

from dataclasses import dataclass

@dataclass
class VoltageSource:
    """Simple DC voltage source."""
    name: str
    voltage: float  # in Volts


@dataclass
class Resistor:
    """Ideal resistor."""
    name: str
    resistance: float  # in Ohms


@dataclass
class Led:
    """
    Simple LED model with forward voltage + max safe current.
    We’ll use this later for LED experiments.
    """
    name: str
    forward_voltage: float  # in Volts
    max_current: float      # in Amps
