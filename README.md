# Epidemic Simulation Model

This project implements a Python-based SEIR epidemic simulation to model the spread of disease under various public health interventions. It supports quarantine, masking, vaccination, and social distancing, with flexible trigger mechanisms and customizable parameters. The simulation results can be saved to CSV or an SQLite database, and visualized using matplotlib.

---

## Features

- **SEIR Compartments**: Models individuals transitioning through:
  - Susceptible (S)
  - Exposed (E)
  - Infectious (I)
  - Recovered (R)
- **Public Health Interventions**:
  - Quarantine (based on time or infection count)
  - Masking (reduces transmission rate)
  - Vaccination (rollout after delay at a specified rate)
  - Social Distancing (reduces contact rate)
- **Simulation Outputs**:
  - CSV export for statistical analysis
  - SQLite integration using `DatabaseManager.py`
  - Plotting of SEIR trends and intervention effects

---

## Simulation Parameters

| Parameter         | Description                              |
|------------------|------------------------------------------|
| `N`              | Total population size                    |
| `init_infected`  | Initial number of infectious individuals |
| `init_exposed`   | Initial number of exposed individuals    |
| `days`           | Number of days to simulate               |
| `beta`           | Transmission probability per contact     |
| `sigma`          | Incubation rate (E → I transition)       |
| `gamma`          | Recovery rate (I → R transition)         |
| `act_rate`       | Daily contact rate per individual        |

---

## Interventions

Each intervention has parameters for activation (by day or infection threshold):

- **Quarantine**: Probabilistically isolates infectious individuals.
- **Masking**: Reduces the effective transmission probability.
- **Vaccination**: Immunizes a portion of the population each day.
- **Social Distancing**: Lowers the number of daily contacts per person.

---

## Installation

Make sure you have Python 3.7+ installed.

Install dependencies using pip:

```bash
pip install numpy pandas matplotlib
```

---

## Usage

Run the simulation:

```bash
python epidemic_model.py
```

This performs 90 simulations:
- 15 baseline (no interventions)
- 15 with masking
- 15 with quarantine (moderate)
- 15 with quarantine (strong)
- 15 with masking + moderate quarantine
- 15 with masking + strong quarantine

Each run appends its summary results to `epidemic_data.csv`.

---

## Example Code

```python
from epidemic_model import EpidemicModel

model = EpidemicModel(
    N=10000,
    init_infected=10,
    init_exposed=5,
    days=100,
    beta=0.2,
    sigma=0.1,
    gamma=0.1,
    act_rate=7
)

model.apply_masking(mask_effectiveness=0.5, mask_day=10)
model.apply_quarantine(q_prob=0.75, quarantine_day=10)

history_df, totals_df = model.sim()
model.save_to_csv("epidemic_data.csv")
model.plot_results()
```

---

## Output Files

- `epidemic_data.csv`: Summary of all simulation runs
- `epidemic_data.db` (optional): SQLite database with full history
- Line plots showing dynamics of each compartment over time

---

## Project Structure

```
.
├── epidemic_model.py       # Main simulation class
├── DatabaseManager.py      # SQLite handling (must be implemented)
├── epidemic_data.csv       # Aggregated simulation output
├── README.md               # Project documentation
```

---

## Key Metrics Tracked

- Total and peak values of:
  - Infected (E + I)
  - Quarantined
  - Vaccinated
- Daily compartment counts: S, E, I, R, Q, V

---

## Simulation Scenarios

The script includes multiple runs under different interventions. You can modify or extend the simulation loop to test additional combinations of policy scenarios.

---

## License

This project is licensed under the MIT License. See `LICENSE` for more information.

---

## Contact

For questions or contributions, feel free to open an issue or submit a pull request.

