Epidemic Simulation Model
This repository contains a Python-based SEIR epidemic simulation with optional intervention strategies including quarantine, masking, vaccination, and social distancing. The simulation tracks the population through different health states and allows for analysis of intervention effectiveness.

📦 Features
SEIR Model: Susceptible → Exposed → Infectious → Recovered dynamics

Intervention Capabilities:

Quarantine (by day or infection threshold)

Masking (adjustable effectiveness)

Vaccination (with rollout delay and rate)

Social Distancing (reduced contact rate)

Data Output:

Exports results to CSV

Optionally saves to SQLite using DatabaseManager

Visualization: Time-series plots of all health states

🧪 Simulation Parameters
Parameter	Description
N	Total population size
init_infected	Initial number of infectious individuals
init_exposed	Initial number of exposed individuals
days	Number of days to simulate
beta	Probability of transmission per contact
sigma	Incubation rate (E → I transition)
gamma	Recovery rate (I → R transition)
act_rate	Average contacts per individual per day

🚀 Running the Simulation
Install dependencies:

bash
Copy
Edit
pip install numpy pandas matplotlib
Run the main script:

bash
Copy
Edit
python epidemic_model.py
This will perform 90 simulations:

15 baseline (no interventions)

15 with masking

15 with quarantine (moderate)

15 with quarantine (strong)

15 with both masking + moderate quarantine

15 with both masking + strong quarantine

Each run appends summary results to epidemic_data.csv.

📊 Output
CSV Output: Summary metrics from each simulation run (e.g., max infections, quarantine rates).

Plot: Line chart visualizing population state transitions over time.

Database Output (optional): Results saved to epidemic_data.db if save_to_db() is called.

🛠️ Project Structure
bash
Copy
Edit
.
├── epidemic_model.py         # Main simulation script
├── DatabaseManager.py        # SQLite interface (assumed present)
├── epidemic_data.csv         # Output of simulation runs
├── README.md                 # This file
🧩 Example Use
python
Copy
Edit
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

model.apply_masking(0.5, mask_day=10)
model.apply_quarantine(0.75, quarantine_day=10)
history, totals = model.sim()
model.save_to_csv()
model.plot_results()
📈 Key Metrics Collected
max_infected: Peak number of individuals exposed or infectious

max_quarantined: Maximum number quarantined

max_vaccinated: Maximum number vaccinated

Daily counts of all SEIR and intervention states

📌 Notes
All interventions can be triggered by day or by infection threshold, but not both simultaneously.

Contact reduction (social distancing) must reduce act_rate but remain > 0.

📜 License
This project is open-source and available under the MIT License.

