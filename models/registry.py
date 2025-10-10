from models.sir_dash import run_sir
from models.sircp_dash import run_sirp_with_compliance
from models.sicr_pf import run_sicr_pf

MODEL_REGISTRY = {
    "sir": {
        "function": run_sir,
        "params": ["I0", "beta", "gamma"],
        "default_names": ["Susceptible", "Infected", "Recovered"],
        "plot": "default"
    },
    "sirc-p": {
        "function": run_sirp_with_compliance,
        "params": ["I0","beta", "gamma", "alpha", "delta", "compliance_max", "k", "rho", "N"],
        "default_names": ["Susceptible", "Infected", "Reportd Cases", "Recovered", "Perceived Risk"],
        "plot": "sircp_dashboard"
    },
    "sirc-pf": {
        "function": run_sicr_pf,
        "params": ["I0", "N", "beta_0", "gamma", "rho", "alpha", "delta", "compliance_max", "gamma_F", "epsilon", "phi"],
        "default_names": ["Susceptible", "Infected", "Reportd Cases", "Recovered", "Perceived Risk", "Fatigue"],
        "plot": "sicr_pf_dashboard"
    }
}
