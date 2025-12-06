# circuit_engine/circuit.py

from dataclasses import dataclass, field
from typing import List
from .components import VoltageSource, Resistor, Led


@dataclass
class SeriesCircuit:
    """
    Very simple series circuit:
    - exactly one DC voltage source
    - one or more series components (resistors, LEDs, etc.)
    
    This is enough for:
      - Ohm's law
      - Series resistors
      - LED + resistor
    We’ll create more complex circuit types later.
    """
    source: VoltageSource
    resistors: List[Resistor] = field(default_factory=list)
    leds: List[Led] = field(default_factory=list)

    def total_series_resistance(self) -> float:
        """
        For now, treat LEDs separately and handle them in solver.
        Here we just sum resistor values. 
        """
        return sum(r.resistance for r in self.resistors)
