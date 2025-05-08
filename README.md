\documentclass[11pt]{article}
\usepackage{geometry}
\usepackage{listings}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{hyperref}
\geometry{margin=1in}
\title{Epidemic Simulation Model Documentation}
\author{}
\date{}

\begin{document}

\maketitle

\section*{Overview}

This document describes a Python-based SEIR epidemic simulation model that includes optional interventions such as quarantine, masking, vaccination, and social distancing. The simulation is designed to track epidemic spread and evaluate the effectiveness of interventions across multiple simulation runs.

\section*{Features}

\begin{itemize}
    \item \textbf{SEIR States:} Susceptible, Exposed, Infectious, Recovered
    \item \textbf{Intervention Options:}
    \begin{itemize}
        \item Quarantine (triggered by time or infection threshold)
        \item Masking (with adjustable effectiveness)
        \item Vaccination (with start time and rollout rate)
        \item Social Distancing (reduces contact rate)
    \end{itemize}
    \item \textbf{Data Output:}
    \begin{itemize}
        \item CSV and SQLite database output
        \item Time-series plot of compartment values
    \end{itemize}
\end{itemize}

\section*{Simulation Parameters}

\begin{tabular}{|l|l|}
\hline
\textbf{Parameter} & \textbf{Description} \\
\hline
\texttt{N} & Total population size \\
\texttt{init\_infected} & Initial number of infected individuals \\
\texttt{init\_exposed} & Initial number of exposed individuals \\
\texttt{days} & Duration of the simulation in days \\
\texttt{beta} & Probability of infection per contact \\
\texttt{sigma} & Transition rate from exposed to infectious \\
\texttt{gamma} & Recovery rate \\
\texttt{act\_rate} & Number of contacts per individual per day \\
\hline
\end{tabular}

\section*{Usage Instructions}

\subsection*{Installing Dependencies}
\begin{lstlisting}[language=bash]
pip install numpy pandas matplotlib
\end{lstlisting}

\subsection*{Running the Simulation}

Run the Python script to perform 90 simulations:
\begin{itemize}
    \item 15 baseline (no intervention)
    \item 15 masking only
    \item 15 quarantine (moderate)
    \item 15 quarantine (strong)
    \item 15 masking + moderate quarantine
    \item 15 masking + strong quarantine
\end{itemize}

Each run appends its summary results to \texttt{epidemic\_data.csv}.

\section*{Example Code}

\begin{lstlisting}[language=Python]
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
\end{lstlisting}

\section*{Output}

\begin{itemize}
    \item \textbf{CSV File:} Summary metrics including max infections, vaccinations, quarantines
    \item \textbf{Plot:} Time series of SEIR states and intervention statuses
    \item \textbf{SQLite DB:} Optional save of each simulation run to a relational database
\end{itemize}

\section*{Metrics Collected}

\begin{itemize}
    \item Maximum infected individuals
    \item Maximum exposed, quarantined, vaccinated individuals
    \item Total number of individuals infected during simulation
    \item Daily counts of all SEIR compartments
\end{itemize}

\section*{Project Structure}

\begin{verbatim}
.
├── epidemic_model.py         # Main simulation script
├── DatabaseManager.py        # SQLite interface (assumed present)
├── epidemic_data.csv         # Output of simulation runs
├── README.tex                # This file
\end{verbatim}

\section*{License}

This project is released under the MIT License.

\end{document}
