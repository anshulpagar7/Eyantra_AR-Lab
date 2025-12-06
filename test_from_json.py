# test_from_json.py

from circuit_engine.loader import load_series_circuit_from_json
from circuit_engine.solver import solve_series_circuit
from pathlib import Path


def main():
    json_path = Path("experiments/exp1_ohm.json")
    circuit = load_series_circuit_from_json(json_path)
    result = solve_series_circuit(circuit)

    print("=== Loaded from JSON: Ohm's Law Experiment ===")
    print(result)


if __name__ == "__main__":
    main()
