from models.sir_dash import run_sir
from models.sircp_dash import run_sirp_with_compliance
#from models.agent import run_agent_based

MODEL_REGISTRY = {
    "sir": {
        "function": run_sir,
        "params": ["I0", "beta", "gamma"],
        "default_names": ["Susceptible", "Infected", "Recovered"],
        "plot": "default"
    },
    "sirp": {
        "function": run_sirp_with_compliance,
        "params": ["I0","beta", "gamma", "alpha", "delta", "compliance_max", "k", "rho", "N"],
        "default_names": ["Susceptible", "Infected", "Reportd Cases", "Recovered", "Perceived Risk"],
        "plot": "sircp_dashboard"
    }
    #"agent": {
    #    "function": run_agent_based,
    #    "params": ["N", "steps", "p_infect", "p_recover"],
    #    "compartments": ["Healthy", "Infected", "Recovered"]
    #}
}
