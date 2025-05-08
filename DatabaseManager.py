import sqlite3 as sql

class DatabaseManager:
    def __init__(self, db_name="epidemic_data.db"):
        """
        Initialize the DatabaseManager with the database name.

        Args:
            db_name (str): Name of the SQLite database file.
        """
        self.db_name = db_name

    def create_tables(self):
        """
        Create necessary tables for storing simulation data.
        """
        connection = sql.connect(self.db_name)
        cursor = connection.cursor()

        create_table_queries = {
            "simulation_run": """
                CREATE TABLE IF NOT EXISTS simulation_run (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    N INTEGER,
                    init_infected INTEGER,
                    init_exposed INTEGER,
                    days INTEGER,
                    beta REAL,
                    sigma REAL,
                    gamma REAL,
                    act_rate INTEGER,
                    quarantine_enabled BOOLEAN,
                    quarantine_enabled_day BOOLEAN,
                    quarantine_enabled_threshold BOOLEAN,
                    quarantine_prob REAL,
                    quarantine_start INTEGER,
                    quarantine_threshold INTEGER,
                    vaccination_enabled BOOLEAN,
                    vaccine_start INTEGER,
                    vaccine_rate REAL,
                    vaccine_enabled_day BOOLEAN,
                    vaccine_enabled_threshold BOOLEAN,
                    distancing_enabled BOOLEAN,
                    distancing_start INTEGER,
                    distancing_threshold INTEGER,
                    reduced_contacts INTEGER,
                    distancing_enabled_day BOOLEAN,
                    masking_enabled BOOLEAN,
                    masking_enabled_day BOOLEAN,
                    masking_enabled_threshold BOOLEAN,
                    mask_start INTEGER,
                    mask_threshold INTEGER,
                    mask_effectiveness REAL
                )
            """,
            "simulation_results": """
                CREATE TABLE IF NOT EXISTS simulation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sim_run_id INTEGER,
                    day INTEGER,
                    susceptible INTEGER,
                    exposed INTEGER,
                    infectious INTEGER,
                    recovered INTEGER,
                    quarantined INTEGER,
                    vaccinated INTEGER,
                    FOREIGN KEY (sim_run_id) REFERENCES simulation_run (id)
                )
            """,
            "totals": """
                CREATE TABLE IF NOT EXISTS totals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sim_run_id INTEGER,
                    total_infected INTEGER,
                    total_exposed INTEGER,
                    total_recovered INTEGER,
                    total_quarantined INTEGER,
                    total_vaccinated INTEGER,
                    total_susceptible INTEGER,
                    max_infected INTEGER,
                    max_exposed INTEGER,
                    max_quarantined INTEGER,
                    max_vaccinated INTEGER,
                    FOREIGN KEY (sim_run_id) REFERENCES simulation_run (id)
                )
            """,
        }

        for query in create_table_queries.values():
            cursor.execute(query)

        connection.commit()
        connection.close()

    def insert_simulation_run(self, sim_run_data):
        """
        Insert a new simulation run into the database.

        Args:
            sim_run_data (tuple): Data for the simulation run.
        Returns:
            int: The ID of the inserted simulation run.
        """
        connection = sql.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO simulation_run (
                N, init_infected, init_exposed, days, beta, sigma, gamma, act_rate,
                quarantine_enabled, quarantine_enabled_day, quarantine_enabled_threshold, quarantine_prob,
                quarantine_start, quarantine_threshold, vaccination_enabled, vaccine_start,
                vaccine_rate, vaccine_enabled_day, vaccine_enabled_threshold, distancing_enabled,
                distancing_start, distancing_threshold, reduced_contacts, distancing_enabled_day,
                masking_enabled, masking_enabled_day, masking_enabled_threshold, mask_start,
                mask_threshold, mask_effectiveness
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            sim_run_data,
        )

        sim_run_id = cursor.lastrowid
        connection.commit()
        connection.close()
        return sim_run_id

    def insert_simulation_results(self, sim_run_id, history_df):
        """
        Insert simulation results into the database.

        Args:
            sim_run_id (int): ID of the simulation run.
            history_df (DataFrame): DataFrame containing the simulation history.
        """
        connection = sql.connect(self.db_name)
        cursor = connection.cursor()

        for row in history_df.itertuples(index=False):
            cursor.execute(
                """
                INSERT INTO simulation_results (
                    sim_run_id, day, susceptible, exposed, infectious, recovered, quarantined, vaccinated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (sim_run_id, row.Day, row.S, row.E, row.I, row.R, row.Q, row.V),
            )

        connection.commit()
        connection.close()

    def insert_totals(self, sim_run_id, totals_df):
        """
        Insert totals into the database.

        Args:
            sim_run_id (int): ID of the simulation run.
            totals_df (DataFrame): DataFrame containing the totals.
        """
        connection = sql.connect(self.db_name)
        cursor = connection.cursor()

        for row in totals_df.itertuples(index=False):
            cursor.execute(
                """
                INSERT INTO totals (
                    sim_run_id, total_infected, total_exposed, total_recovered, total_quarantined, total_vaccinated, total_susceptible,
                    max_infected, max_exposed, max_quarantined, max_vaccinated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    sim_run_id,
                    row.I,
                    row.E,
                    row.R,
                    row.Q,
                    row.V,
                    row.S,
                    row.max_infected,
                    row.max_exposed,
                    row.max_quarantined,
                    row.max_vaccinated,
                ),
            )

        connection.commit()
        connection.close()