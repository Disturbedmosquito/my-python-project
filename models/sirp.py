import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

###### MODEL PARAMETERS ######
params = {
    "N": 10_000,            # Total population
    "beta_0": 0.075,         # Base transmission rate
    "gamma": 1/6.5,         # Recovery rate
    "alpha": 1e-5,          # Perception growth factor
    "delta": 0.05,          # Perception decay rate
    "compliance_max": 0.75, # Maximum compliance
    "k": 1                  # Compliance sensitivity
}


###### INITIAL CONDITIONS ######
I0 = 10
initial_conditions = [
    params["N"] - I0,       # S0
    I0,                     # I0
    0,                      # R0
    0                       # P0
]

###### MODEL DEFINITION ######
def sirp_model_with_compliance(t, y, beta_0, gamma, alpha, delta, compliance_max, k, N):
    S, I, R, P = y
    
    # Calculate compliance and effective transmission rate
    compliance = compliance_max * (1 - np.exp(k * P))
    beta_eff = beta_0 * (1 - compliance)
    
    #Calculate incidence - new infections per day
    incidence = beta_eff * S * I / N
   
   #ODE system
    dSdt = - incidence
    dIdt = incidence - gamma * I
    dRdt = gamma * I
    dPdt = alpha * incidence - delta * P    #perception driven by incidence
    
    return [dSdt, dIdt, dRdt, dPdt]
    
###### EQUATION INTEGRATION ######
t_span = [0, 365]
t_eval = np.linspace(t_span[0], t_span[1], t_span[1]*2)

solution = solve_ivp(
    lambda t, y: sirp_model_with_compliance(t, y, **params), #Pass parameters by name
    t_span,
    initial_conditions,
    t_eval=np.linspace(t_span[0], t_span[1], int((t_span[1]-t_span[0])*2)+1),
    method='RK45'
)

####### PLOT RESULTS ######
S, I, R, P = solution.y
compliance = params['compliance_max'] * (1 - np.exp(-params['k'] * P))
beta_eff = params['beta_0'] * (1 - compliance)
incidence = beta_eff * S * I / params['N']

plt.figure(figsize=(12, 8))

# Plot S, I, R
plt.subplot(2, 2, 1)
plt.plot(solution.t, S, label="Susceptibles")
plt.plot(solution.t, I, label="Infectés")
plt.plot(solution.t, R, label="Récupérés")
plt.xlabel("Temps (jours)")
plt.ylabel("Population")
plt.title("Compartiments SIR")
plt.legend()
plt.grid(True)

# Plot perception P
plt.subplot(2, 2, 2)
plt.plot(solution.t, P, "b-")
plt.xlabel("Temps (jours)")
plt.ylabel("Perception")
plt.title("Perception du risque")
plt.grid(True)

# Plot effective transmission rate
plt.subplot(2, 2, 3)
plt.plot(solution.t, beta_eff, "r-")
plt.xlabel("Temps (jours)")
plt.ylabel("Taux")
plt.title("Transmission efficace (β_eff)")
plt.grid(True)

# Plot incidence
plt.subplot(2, 2, 4)
plt.plot(solution.t, incidence, "g-")
plt.xlabel("Temps (jours)")
plt.ylabel("Nouveaux cas/jour")
plt.title("Incidence")
plt.grid(True)

plt.tight_layout()
plt.show()