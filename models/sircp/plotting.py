import numpy as np
import math
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# ---------- helper functions ----------
ncols = 2

try: 
    S, I, C, R, P = compartments
except ValueError:
    raise ValueError("Expected compartments not match the provided data.")

try:
    compliance = meta["compliance"]
    beta_eff = meta["beta_eff"]
    beta_0 = meta["beta_0"]
    R0 = meta["R0"]
    state = meta["state"]
    rho = meta["rho"]
except ValueError:
    raise ValueError("Expected meta not match the provided data.")

def subplot_index(row, col):
    return (row - 1) * ncols + col

def add_subplot_box(fig, row, col, line_width=1):
    """Draws a thin border box around the subplot (domain coords 0..1)."""
    idx = subplot_index(row, col)
    fig.add_shape(
        type="rect",
        xref=f"x{idx} domain", yref=f"y{idx} domain",
        x0=0, y0=0, x1=1, y1=1,
        line=dict(color="black", width=line_width),
        fillcolor="rgba(0,0,0,0)",
        layer="above",
    )

def add_local_legend(fig, row, col, labels_colors, x_right=0.97, y_top=0.95, font_size=14):
    """
    Adds a compact legend box with small colored line samples at top-right inside the subplot.
    labels_colors: list of (label, color, dash) tuples where dash is 'solid' or 'dash'
    Coordinates are in subplot domain (0..1).
    """
    idx = subplot_index(row, col)
    xref = f"x{idx} domain"
    yref = f"y{idx} domain"

    # Dynamic sizing: width depends on label length, height depends on number of items
    max_chars = max((len(lbl) for lbl,_,_ in labels_colors), default=6)
    box_w = min(0.45, 0.20 + max_chars * 0.01)   # domain units
    box_h = 0.06 * len(labels_colors) + 0.02

    x0 = x_right - box_w
    x1 = x_right
    y1 = y_top
    y0 = y_top - box_h

    # background box
    fig.add_shape(
        type="rect",
        xref=xref, yref=yref,
        x0=x0, x1=x1, y0=y0, y1=y1,
        line=dict(color="black", width=1),
        fillcolor="white",
        opacity=0.95,
        layer="above",
    )

    # add each row: a small line sample + label
    for i, (label, color, dash) in enumerate(labels_colors):
        # compute annotation position within the box: small left padding
        ann_x = x0 + 0.03
        ann_y = y1 - 0.03 - i * 0.06

        # small line-sample as an inline-block HTML swatch (Plotly supports simple HTML)
        sample_html = (
            f"<span style='display:inline-block;"
            f"width:28px;height:3px;border-radius:2px;"
            f"background:{color};margin-right:8px;"
            f"border: 1px solid rgba(0,0,0,0.15);"
            f"opacity:1;"
            f"'></span>"
        )

        # show dashed style by adding a small dashed unicode bar if requested (dash effect)
        if dash == "dash":
            # append small dashed text after the swatch to indicate dash (visual cue)
            sample_html = (
                f"<span style='display:inline-block;"
                f"width:28px;height:3px;border-radius:2px;"
                f"background:{color};margin-right:6px;"
                f"border: 1px solid rgba(0,0,0,0.12);"
                f"'></span>"
                f"<span style='color:gray;margin-right:6px;'>– –</span>"
            )

        fig.add_annotation(
            xref=xref, yref=yref,
            x=ann_x, y=ann_y,
            xanchor="left", yanchor="middle",
            showarrow=False,
            text= f"{sample_html}{label}",
            align="left",
            font=dict(size=font_size, family="Times New Roman", color="black"),
            captureevents=False,
            valign="middle"
        )

# ---------- compute tick spacing (8 intervals -> 9 ticks) ----------
t_max = float(np.max(t))
ticks_count = 8  # 8 intervals (so 9 tick positions)
raw_ticks = np.linspace(0.0, t_max, ticks_count + 1)
# If t is integer-based days, make ticks integers; otherwise 1-decimal
if np.allclose(np.round(t), t):
    tickvals = [int(round(v)) for v in raw_ticks]
else:
    tickvals = [round(float(v), 1) for v in raw_ticks]

# ---------- build subplots ----------
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Disease Compartments: S — I — C — R",
        "Risk Perception and Behavioral Response",
        "Transmission Rate vs. Infected / Reported",
        f"Reporting Delay: {1/rho:.1f} days"
    ),
    specs=[[{}, {}],
           [{"secondary_y": True}, {}]],
    horizontal_spacing=0.04,  # tighten the gaps
    vertical_spacing=0.07
)

# --- Add traces (turn off global legend; fake local legends will be used) ---
# Plot 1: Compartments
fig.add_trace(go.Scatter(x=t, y=S, mode="lines", name="Susceptible",
                         line=dict(color="royalblue", width=3), showlegend=False), row=1, col=1)
fig.add_trace(go.Scatter(x=t, y=I, mode="lines", name="Infected",
                         line=dict(color="orange", width=3), showlegend=False), row=1, col=1)
fig.add_trace(go.Scatter(x=t, y=C, mode="lines", name="Reported Cases",
                         line=dict(color="red", width=3), showlegend=False), row=1, col=1)
fig.add_trace(go.Scatter(x=t, y=R, mode="lines", name="Recovered",
                         line=dict(color="green", width=3), showlegend=False), row=1, col=1)
fig.update_yaxes(title_text="Population", row=1, col=1)

# Plot 2: Risk perception & compliance
fig.add_trace(go.Scatter(x=t, y=P, mode="lines", name="Risk Perception (P)",
                         line=dict(color="magenta", width=3), showlegend=False), row=1, col=2)
fig.add_trace(go.Scatter(x=t, y=compliance, mode="lines", name="Compliance",
                         line=dict(color="cyan", dash="dash", width=2), showlegend=False), row=1, col=2)
fig.update_yaxes(title_text="Level", row=1, col=2)

# Plot 3: Transmission (left) vs Cases (right)
fig.add_trace(go.Scatter(x=t, y=beta_eff, mode="lines", name="β_eff",
                         line=dict(color="red", width=3), showlegend=False), row=2, col=1, secondary_y=False)
fig.add_trace(go.Scatter(x=t, y=[beta_0]*len(t), mode="lines", name="β₀ (base)",
                         line=dict(color="red", dash="dash", width=2), showlegend=False), row=2, col=1, secondary_y=False)
fig.add_trace(go.Scatter(x=t, y=I, mode="lines", name="Infections (I)",
                         line=dict(color="blue", width=3), showlegend=False), row=2, col=1, secondary_y=True)
fig.add_trace(go.Scatter(x=t, y=C, mode="lines", name="Reported (C)",
                         line=dict(color="orange", width=3), showlegend=False), row=2, col=1, secondary_y=True)

fig.update_yaxes(title_text="Transmission rate", row=2, col=1, secondary_y=False)
fig.update_yaxes(title_text="Number of cases", row=2, col=1, secondary_y=True)

# Plot 4: Reporting delay + shaded region
fig.add_trace(go.Scatter(x=t, y=I, mode="lines", name="Infections (I)",
                         line=dict(color="blue", width=3), showlegend=False), row=2, col=2)
fig.add_trace(go.Scatter(x=t, y=C, mode="lines", name="Reported (C)",
                         line=dict(color="orange", width=3), showlegend=False), row=2, col=2)

peak_i_time = float(t[np.argmax(I)])
peak_c_time = float(t[np.argmax(C)])
if peak_c_time < peak_i_time:  # swap if reporting peak earlier (safety)
    peak_i_time, peak_c_time = peak_c_time, peak_i_time

# shaded rect (reporting delay interval)
fig.add_vrect(x0=peak_i_time, x1=peak_c_time, fillcolor="gray", opacity=0.20,
              layer="below", line_width=0, row=2, col=2)

# vertical lines & annotations (kept inside the subplot)
fig.add_vline(x=peak_i_time, line=dict(color="blue", dash="dash"),
              annotation_text=f"Peak I (Day {peak_i_time:.1f})", annotation_position="top left",
              row=2, col=2)
fig.add_vline(x=peak_c_time, line=dict(color="orange", dash="dash"),
              annotation_text=f"Peak C (Day {peak_c_time:.1f})", annotation_position="top right",
              row=2, col=2)

fig.update_yaxes(title_text="Cases", row=2, col=2)
fig.update_xaxes(title_text="Time (days)", row=2, col=2)

# --- Add framed boxes around subplots and small in-plot legends ---
for r in (1,2):
    for c in (1,2):
        add_subplot_box(fig, r, c)

# add tight local legends (top-right inside each plot)
add_local_legend(fig, 1, 1, [
    ("Susceptible", "royalblue", "solid"),
    ("Infected", "orange", "solid"),
    ("Reported", "red", "solid"),
    ("Recovered", "green", "solid"),
], x_right=0.97, y_top=0.95, font_size=13)

add_local_legend(fig, 1, 2, [
    ("Risk Perception (P)", "magenta", "solid"),
    ("Compliance", "cyan", "dash"),
], x_right=0.97, y_top=0.95, font_size=13)

add_local_legend(fig, 2, 1, [
    ("β_eff", "red", "solid"),
    ("β₀ (base)", "red", "dash"),
    ("Infections (I)", "blue", "solid"),
    ("Reported (C)", "orange", "solid"),
], x_right=0.97, y_top=0.95, font_size=13)

add_local_legend(fig, 2, 2, [
    ("Infections (I)", "blue", "solid"),
    ("Reported (C)", "orange", "solid"),
    ("Reporting delay", "gray", "solid"),
], x_right=0.97, y_top=0.95, font_size=13)

# --- Fix grids & ticks (apply consistent tick positions based on t) ---
# Use explicit tickvals computed above so vertical gridlines align across subplots.
for r in (1,2):
    for c in (1,2):
        fig.update_xaxes(row=r, col=c,
                         tickmode="array",
                         tickvals=tickvals,
                         ticktext=[str(v) for v in tickvals],
                         showgrid=True, gridcolor="lightgray",
                         zeroline=False,
                         tickfont=dict(size=11))

# For the transmission panel (row=2,col=1) ensure the left y-axis provides horizontal gridlines
fig.update_yaxes(row=2, col=1, secondary_y=False, showgrid=True, gridcolor="lightgray", zeroline=False)
# and suppress gridlines from the secondary (right) y-axis so horizontal grid is continuous
fig.update_yaxes(row=2, col=1, secondary_y=True, showgrid=False, zeroline=False)

# General axis & layout cosmetics
fig.update_layout(
    autosize=True,                    # allow container to control width
    height=920,
    margin=dict(l=50, r=20, t=80, b=50),
    plot_bgcolor="white",
    title=dict(text="SIRCP Model Dashboard", x=0.5, xanchor="center",
               font=dict(size=20, family="Times New Roman")),
    font=dict(family="Times New Roman", size=13)
)

# disable Plotly's global legend (we use fake in-plot legends)
fig.update_layout(showlegend=False)

# Show/Render:
# - In a browser or notebook: use responsive config so the figure stretches to container width.
fig.show(config={"responsive": True})
