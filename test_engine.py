# test_engine.py

from circuit_engine.components import VoltageSource, Resistor, Led
from circuit_engine.circuit import SeriesCircuit
from circuit_engine.solver import solve_series_circuit


def test_ohms_law():
    """
    Simple test:
      - 5V supply
      - 1 kΩ resistor
    Expect: I = 5V / 1000Ω = 0.005 A (5 mA)
    """
    V = VoltageSource(name="V1", voltage=5.0)
    R1 = Resistor(name="R1", resistance=1000.0)

    circuit = SeriesCircuit(source=V, resistors=[R1])

    result = solve_series_circuit(circuit)
    print("=== Ohm's Law Test ===")
    print(result)


def test_led_with_resistor():
    """
    5V supply, red LED (2V drop, 20mA max), 220Ω resistor.
    Expected current approx = (5 - 2) / 220 ≈ 13.6 mA
    """
    V = VoltageSource(name="V1", voltage=5.0)
    R1 = Resistor(name="R1", resistance=220.0)
    led = Led(name="LED1", forward_voltage=2.0, max_current=0.02)  # 20 mA max

    circuit = SeriesCircuit(source=V, resistors=[R1], leds=[led])

    result = solve_series_circuit(circuit)
    print("=== LED + Resistor Test ===")
    print(result)


if __name__ == "__main__":
    test_ohms_law()
    print()
    test_led_with_resistor()
