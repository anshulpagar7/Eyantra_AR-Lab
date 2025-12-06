# test_steps.py

from circuit_engine.loader import load_series_circuit_from_json
from pathlib import Path

def main():
    circuit, steps = load_series_circuit_from_json("experiments/exp1_ohm.json")

    print("=== Circuit Loaded ===")
    print(circuit)

    print("\n=== Steps ===")
    for step in steps:
        print(step)

if __name__ == "__main__":
    main()
