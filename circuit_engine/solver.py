# circuit_engine/solver.py

from typing import Dict, Any
from .circuit import SeriesCircuit
from .components import Led


def solve_series_circuit(circuit: SeriesCircuit) -> Dict[str, Any]:
    """
    Solve a very simple DC series circuit:
    - 1 voltage source
    - N resistors in series
    - Optional LEDs (treated as fixed voltage drops)

    Returns a dict with:
      - total_resistance
      - total_led_drop
      - available_resistor_voltage
      - current
      - voltage_drops (per component)
    """
    V_supply = circuit.source.voltage

    # Total LED forward voltage (sum of all LEDs in series)
    total_led_drop = sum(led.forward_voltage for led in circuit.leds)

    # Total resistance of resistors
    total_R = circuit.total_series_resistance()

    result: Dict[str, Any] = {
        "supply_voltage": V_supply,
        "total_resistance": total_R,
        "total_led_drop": total_led_drop,
        "available_resistor_voltage": None,
        "current": 0.0,
        "voltage_drops": {},
        "led_status": {},
    }

    # If LED drops already exceed supply, no current flows
    if total_led_drop >= V_supply or total_R <= 0:
        # All LEDs are off in this case
        for led in circuit.leds:
            result["led_status"][led.name] = "OFF (insufficient voltage)"
        result["available_resistor_voltage"] = max(V_supply - total_led_drop, 0)
        return result

    # Voltage available for resistors
    V_resistors = V_supply - total_led_drop
    result["available_resistor_voltage"] = V_resistors

    # Ohm's law: I = V / R
    I = V_resistors / total_R
    result["current"] = I

    # Voltage drop per resistor
    for r in circuit.resistors:
        Vr = I * r.resistance
        result["voltage_drops"][r.name] = Vr

    # LED status (safe or overcurrent)
    for led in circuit.leds:
        if I <= led.max_current:
            result["led_status"][led.name] = f"ON (I = {I:.3f} A, safe)"
        else:
            result["led_status"][led.name] = f"ON but OVERCURRENT (I = {I:.3f} A)"

    return result
