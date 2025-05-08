### IMPORTS ###
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

from DatabaseManager import DatabaseManager


### STATES ###
SUSCEPTIBLE = 0
EXPOSED = 1
INFECTIOUS = 2
RECOVERED = 3

### INTERVENTION STATES ###
QUARANTINED = 1
VACCINATED = 1


class EpidemicModel:
    def __init__(
        self, N, init_infected, init_exposed, days, beta, sigma, gamma, act_rate
    ):
        """
        INITIALIZE EPIDEMIC MODEL PARAMETERS

        Args:
            N (int): Total population size.
            init_infected (int): Initial number of infected individuals.
            init_exposed (int): Initial number of exposed individuals.
            days (int): Number of days to simulate.
            beta (float): Infection probability per contact.
            sigma (float): Incubation rate.
            gamma (float): Recovery rate.
            act_rate (int): Number of contacts per day.

        """
        self.N = N
        self.init_infected = init_infected
        self.init_exposed = init_exposed
        self.days = days
        self.beta = beta
        self.sigma = sigma
        self.gamma = gamma
        self.act_rate = act_rate

        ### INITIALIZE INTERVENTION PARAMETERS ###
        self.quarantine_enabled = False
        self.quarantine_enabled_day = False
        self.quarantine_enabled_threshold = False
        self.quarantine_prob = 0.0
        self.quarantine_start = None
        self.quarantine_threshold = None

        self.vaccination_enabled = False
        self.vaccine_start = None
        self.vaccine_rate = 0.0
        self.vaccine_enabled_day = False
        self.vaccine_enabled_threshold = False

        self.distancing_enabled = False
        self.distancing_start = None
        self.distancing_threshold = None
        self.reduced_contacts = None
        self.distancing_enabled_day = False
        self.distancing_enabled_threshold = False

        self.masking_enabled = False
        self.mask_start = None
        self.mask_threshold = None
        self.mask_effectiveness = 0.0
        self.mask_enabled_day = False
        self.mask_enabled_threshold = False

        ### INITIALIZE POPULATION ###
        self.states = np.full(N, SUSCEPTIBLE)
        self.states[:init_exposed] = EXPOSED
        self.states[init_exposed : init_exposed + init_infected] = INFECTIOUS
        np.random.shuffle(self.states)

        self.vaccinated = np.zeros(N, dtype=int)
        self.quarantined = np.zeros(N, dtype=int)

        ### DATA STRUCTURE FOR RESULTS ###
        self.history = {"S": [], "E": [], "I": [], "R": [], "Q": [], "V": [], "infected": []}
        self.totals = {"S": 0, "E": 0, "I": [], "R": [], "Q": [], "V": [], "infected": []}

    def apply_quarantine(self, q_prob, quarantine_day=None, quarantine_threshold=None):
        """
        APPLY QUARANTINE INTERVENTION AT A SPECIFIC DAY OR THRESHOLD

        Args:
            q_prob (float): Quarantine probability (0 to 1).
            quarantine_day (int): Day to start quarantine.
            quarantine_threshold (int): Threshold of infectious individuals to start quarantine.

        """

        if not (0 <= q_prob <= 1):
            raise ValueError("Quarantine probability must be between 0 and 1.")

        if quarantine_day and quarantine_threshold:
            raise ValueError(
                "Both trigger_day and trigger_infectious cannot be set at the same time."
            )

        elif quarantine_day:
            self.quarantine_start = quarantine_day
            self.quarantine_prob = q_prob
            self.quarantine_enabled_day = True

        elif quarantine_threshold:
            self.quarantine_threshold = quarantine_threshold
            self.quarantine_prob = q_prob
            self.quarantine_enabled_threshold = True

        self.quarantine_enabled = True

    def apply_vaccination(
        self, v_rate, vaccination_day=None, begin_vaccine_development=None
    ):
        """
        APPLY VACCINATION INTERVENTION AT A SPECIFIC DAY OR BEGINNING OF VACCINE DEVELOPMENT

        Args:
            v_rate (float): Vaccination rate (0 to 1).
            vaccination_day (int): Day to start vaccination.
            begin_vaccine_development (int): Days until vaccine is available.

        """

        if not (0 <= v_rate <= 1):
            raise ValueError("Vaccination rate must be between 0 and 1.")

        if vaccination_day:
            if begin_vaccine_development:
                self.vaccine_start = vaccination_day + begin_vaccine_development
                self.vaccine_rate = v_rate
            else:
                self.vaccine_start = vaccination_day
                self.vaccine_rate = v_rate

            self.vaccination_enabled = True

        elif begin_vaccine_development and not vaccination_day:
            raise ValueError(
                "Vaccination day must be set if vaccine development time is specified."
            )

    def apply_masking(self, mask_effectiveness, mask_day=None, mask_threshold=None):
        """
        APPLY MASKING INTERVENTION AT A SPECIFIC DAY OR THRESHOLD

        Args:
            mask_effectiveness (float): Effectiveness of the mask (0 to 1).
            mask_day (int): Day to start masking.
            mask_threshold (int): Threshold of infectious individuals to start masking.

        """

        if not (0 <= mask_effectiveness <= 1):
            raise ValueError("Mask effectiveness must be between 0 and 1.")

        if mask_day and mask_threshold:
            raise ValueError(
                "Cannot set both mask_day and mask_threshold at the same time."
            )

        elif mask_day:
            self.mask_start = mask_day
            self.mask_effectiveness = mask_effectiveness
            self.mask_enabled_day = True

        elif mask_threshold:
            self.mask_threshold = mask_threshold
            self.mask_effectiveness = mask_effectiveness
            self.mask_enabled_threshold = True

        self.masking_enabled = True

    def apply_distancing(
        self, reduced_contacts, distancing_day=None, distancing_threshold=None
    ):
        """
        APPLY SOCIAL DISTANCING INTERVENTION AT A SPECIFIC DAY OR THRESHOLD

        Args:
            reduced_contacts (int): Number of contacts per day after distancing.
            distancing_day (int): Day to start social distancing.
            distancing_threshold (int): Threshold of infectious individuals to start distancing.

        """

        if not (0 < reduced_contacts < self.act_rate):
            raise ValueError(
                "Reduced contacts must be between 0 and the original activity rate."
            )

        if distancing_day and distancing_threshold:
            raise ValueError(
                "Cannot set both distancing_day and distancing_threshold at the same time."
            )

        elif distancing_day:
            self.distancing_start = distancing_day
            self.reduced_contacts = reduced_contacts
            self.distancing_enabled_day = True

        elif distancing_threshold:
            self.distancing_threshold = distancing_threshold
            self.reduced_contacts = reduced_contacts
            self.distancing_enabled_threshold = True

        self.distancing_enabled = True

    def sim(self):
        """
        SIMULATE EPIDEMIC MODEL

        """

        ### REINITIALIZE MODEL ###
        self.history = {
            "S": [self.N - self.init_exposed - self.init_infected],
            "E": [self.init_exposed],
            "I": [self.init_infected],
            "R": [0],
            "Q": [0],
            "V": [0],
            "infected": [self.init_exposed + self.init_infected],
        }

        self.totals = {
            "S": self.N - self.init_exposed - self.init_infected,
            "E": self.init_exposed,
            "I": self.init_infected,
            "R": 0,
            "V": 0,
            "Q": 0,
            "max_infected": self.init_infected,
            "max_exposed": self.init_exposed,
            "max_quarantined": 0,
            "max_vaccinated": 0,
            "infected": 0,
        }

        ### INITIALIZE STATES ###
        self.states = np.full(self.N, SUSCEPTIBLE)
        self.states[: self.init_exposed] = EXPOSED
        self.states[self.init_exposed : self.init_exposed + self.init_infected] = (
            INFECTIOUS
        )
        np.random.shuffle(self.states)
        self.vaccinated = np.zeros(self.N, dtype=int)
        self.quarantined = np.zeros(self.N, dtype=int)

        for day in range(self.days):
            new_states = self.states.copy()
            new_vaccinated = self.vaccinated.copy()
            new_quarantined = self.quarantined.copy()

            ### ADJUST CONTACTS IF DISTANCING INTERVENTION IS ENABLED ###
            if self.distancing_enabled and (
                (self.distancing_enabled_day and day >= self.distancing_start)
                or (
                    self.distancing_enabled_threshold
                    and np.sum(self.states == INFECTIOUS) >= self.distancing_threshold
                )
            ):
                current_contacts = self.reduced_contacts

            else:
                current_contacts = self.act_rate

            ### ADJUST BETA (inf_rate) IF MASKING INTERVENTION IS ENABLED ###
            if self.masking_enabled and (
                (self.mask_enabled_day and day >= self.mask_start)
                or (
                    self.mask_enabled_threshold
                    and np.sum(self.states == INFECTIOUS) >= self.mask_threshold
                )
            ):

                current_beta = self.beta * (1 - self.mask_effectiveness)

            else:
                current_beta = self.beta

            ### VACCINATION MODULE ###
            if self.vaccination_enabled and day >= self.vaccine_start:
                non_vaccinated_indices = np.where(self.vaccinated != VACCINATED)[0]

                if len(non_vaccinated_indices) > 0:
                    num_vaccinated = round(
                        np.random.binomial(
                            len(non_vaccinated_indices), self.vaccine_rate
                        )
                    )

                    if num_vaccinated > 0:
                        vaccinated = np.random.choice(
                            non_vaccinated_indices, size=num_vaccinated, replace=False
                        )
                        new_vaccinated[vaccinated] = VACCINATED
                        self.totals["V"] += num_vaccinated

            ### SIMULATE PROGRESSION FOR EACH INDIVIDUAL ###
            for i, state in enumerate(self.states):

                if state == SUSCEPTIBLE:
                    # Check if susceptible individual becomes exposed
                    contacts = np.random.choice(self.N, current_contacts, replace=False)

                    if np.any(self.states[contacts] == INFECTIOUS):
                        if np.random.rand() < 1 - (1 - current_beta) ** (np.sum(
                            self.states[contacts] == INFECTIOUS)
                            - np.sum(self.quarantined[contacts] == QUARANTINED)
                        ):
                            new_states[i] = EXPOSED
                            self.totals["E"] += 1
                            self.totals["infected"] += 1

                elif state == EXPOSED:
                    # Check if exposed individual becomes infectious
                    if np.random.rand() < self.sigma:
                        new_states[i] = INFECTIOUS
                        self.totals["I"] += 1

                elif state == INFECTIOUS:
                    # Check if infectious individual recovers
                    if np.random.rand() < self.gamma:
                        new_states[i] = RECOVERED
                        new_quarantined[i] = 0
                        self.totals["R"] += 1

                    elif self.quarantine_enabled:
                        # Check if infectious individual is quarantined
                        if (
                            self.quarantine_enabled_day and day >= self.quarantine_start
                        ) or (
                            self.quarantine_enabled_threshold
                            and np.sum(self.states == INFECTIOUS)
                            >= self.quarantine_threshold
                        ):
                            if np.random.rand() < self.quarantine_prob:
                                new_quarantined[i] = QUARANTINED
                                self.totals["Q"] += 1

            ### UPDATE STATES ###
            self.states = new_states
            self.vaccinated = new_vaccinated
            self.quarantined = new_quarantined

            ### RECORD STATES ###
            unique, counts = np.unique(self.states, return_counts=True)
            count_dict = dict(zip(unique, counts))
            self.history["S"].append(count_dict.get(SUSCEPTIBLE, 0))
            self.history["E"].append(count_dict.get(EXPOSED, 0))
            self.history["I"].append(count_dict.get(INFECTIOUS, 0))
            self.history["R"].append(count_dict.get(RECOVERED, 0))
            self.history["infected"].append(count_dict.get(INFECTIOUS, 0) + count_dict.get(EXPOSED, 0))

            ### RECORD INTERVENTION STATES ###
            unique, counts = np.unique(self.vaccinated, return_counts=True)
            count_dict = dict(zip(unique, counts))
            self.history["V"].append(count_dict.get(VACCINATED, 0))

            unique, counts = np.unique(self.quarantined, return_counts=True)
            count_dict = dict(zip(unique, counts))
            self.history["Q"].append(count_dict.get(QUARANTINED, 0))

        ### CONVERT HISTORY AND TOTALS TO DATAFRAME ###
        self.history_df = pd.DataFrame(self.history)
        self.history_df["Day"] = np.arange(self.days + 1)
        self.history_df = self.history_df[["Day", "S", "E", "I", "R", "Q", "V", "infected"]]

        self.totals["max_infected"] = np.max(self.history_df["infected"])
        self.totals["max_exposed"] = np.max(self.history_df["E"])
        self.totals["max_quarantined"] = np.max(self.history_df["Q"])
        self.totals["max_vaccinated"] = np.max(self.history_df["V"])
        self.totals_df = pd.DataFrame(self.totals, index=[0])

        return self.history_df, self.totals_df

    def save_to_db(self, db_name="epidemic_data.db"):
        """
        SAVE SIMULATION DATA TO SQLITE DATABASE

        Args:
            db_name (str): Name of the SQLite database file.
        """
        if self.history_df.empty or self.totals_df.empty:
            raise ValueError("No data to save. Please run the simulation first.")

        db_manager = DatabaseManager(db_name)
        db_manager.create_tables()

        # Insert simulation run data
        sim_run_data = (
            self.N,
            self.init_infected,
            self.init_exposed,
            self.days,
            self.beta,
            self.sigma,
            self.gamma,
            self.act_rate,
            self.quarantine_enabled,
            self.quarantine_enabled_day,
            self.quarantine_enabled_threshold,
            self.quarantine_prob,
            self.quarantine_start,
            self.quarantine_threshold,
            self.vaccination_enabled,
            self.vaccine_start,
            self.vaccine_rate,
            self.vaccine_enabled_day,
            self.vaccine_enabled_threshold,
            self.distancing_enabled,
            self.distancing_start,
            self.distancing_threshold,
            self.reduced_contacts,
            self.distancing_enabled_day,
            self.masking_enabled,
            self.mask_enabled_day,
            self.mask_enabled_threshold,
            self.mask_start,
            self.mask_threshold,
            self.mask_effectiveness,
        )
        sim_run_id = db_manager.insert_simulation_run(sim_run_data)

        # Insert simulation results and totals
        db_manager.insert_simulation_results(sim_run_id, self.history_df)
        db_manager.insert_totals(sim_run_id, self.totals_df)

    def save_to_csv(self, filename="epidemic_data.csv"):
        """
        SAVE SIMULATION DATA TO CSV FILE

        Args:
            filename (str): Name of the CSV file.

        """

        if self.history_df.empty or self.totals_df.empty:
            raise ValueError("No data to save. Please run the simulation first.")

        totals = self.totals_df.copy()
        totals = totals / 1000
        totals["quarantine_day"] = self.quarantine_enabled_day
        totals["quarantine_prob"] = self.quarantine_prob
        totals["mask_start"] = self.mask_start
        totals["mask_effectiveness"] = self.mask_effectiveness

        if os.path.exists(filename):
            existing_data = pd.read_csv(filename)
            updated_data = pd.concat([existing_data, totals], ignore_index=True)
            updated_data.to_csv(filename, index=False)
        else:
            totals.to_csv(filename, index=False)
        

    def plot_results(self):
        """
        PLOT RESULTS OF SIMULATION

        """

        plt.figure(figsize=(12, 8))
        plt.plot(
            self.history_df["Day"],
            self.history_df["S"],
            label="Susceptible",
            color="blue",
        )
        plt.plot(
            self.history_df["Day"],
            self.history_df["E"],
            label="Exposed",
            color="orange",
        )
        plt.plot(
            self.history_df["Day"],
            self.history_df["I"],
            label="Infectious",
            color="red",
        )
        plt.plot(
            self.history_df["Day"],
            self.history_df["R"],
            label="Recovered",
            color="green",
        )
        plt.plot(
            self.history_df["Day"],
            self.history_df["Q"],
            label="Quarantined",
            color="purple",
        )
        plt.plot(
            self.history_df["Day"],
            self.history_df["V"],
            label="Vaccinated",
            color="brown",
        )
        plt.plot(
            self.history_df["Day"],
            self.history_df["infected"],
            label="Total Infected",
            color="black",
            linestyle="--",
        )

        plt.title("Epidemic Model Simulation Results")
        plt.xlabel("Days")
        plt.ylabel("Population Count")
        plt.legend()
        plt.grid()
        plt.show()
        return self.history_df


N = 10000
init_infected = 10
init_exposed = 5
days = 100
beta = 0.2
sigma = 0.1
gamma = 0.1
act_rate = 7

for _ in range(15):
    print(f"Running simulation {_} with no interventions...")

    model = EpidemicModel(
        N,
        init_infected,
        init_exposed,
        days,
        beta,
        sigma,
        gamma,
        act_rate
    )

    model.sim() 
    model.save_to_csv()

for _ in range(15):
    print(f"Running simulation {_} with distancing intervention...")

    model = EpidemicModel(
        N,
        init_infected,
        init_exposed,
        days,
        beta,
        sigma,
        gamma,
        act_rate
    )

    model.apply_masking(0.5, 10)
    model.sim()
    model.save_to_csv()

for _ in range(15):
    print(f"Running simulation {_} with masking intervention...")

    model = EpidemicModel(
        N,
        init_infected,
        init_exposed,
        days,
        beta,
        sigma,
        gamma,
        act_rate
    )

    model.apply_quarantine(0.5, 10)
    model.sim()
    model.save_to_csv()

for _ in range(15):
    print(f"Running simulation {_} with quarantine intervention...")
    
    model = EpidemicModel(
        N,
        init_infected,
        init_exposed,
        days,
        beta,
        sigma,
        gamma,
        act_rate
    )

    model.apply_quarantine(0.75, 10)
    model.sim()
    model.save_to_csv()

for _ in range(15):
    print(f"Running simulation {_} with masking and quarantine intervention...")

    model = EpidemicModel(
        N,
        init_infected,
        init_exposed,
        days,
        beta,
        sigma,
        gamma,
        act_rate
    )

    model.apply_masking(0.5, 10)
    model.apply_quarantine(0.5, 10)
    model.sim()
    model.save_to_csv()

for _ in range(15):
    print(f"Running simulation {_} with masking and quarantine intervention...")

    model = EpidemicModel(
        N,
        init_infected,
        init_exposed,
        days,
        beta,
        sigma,
        gamma,
        act_rate
    )

    model.apply_masking(0.5, 10)
    model.apply_quarantine(0.75, 10)
    model.sim()
    model.save_to_csv()
