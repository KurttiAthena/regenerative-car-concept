"""Streamlit screening UI. Draft inputs never overwrite a submitted study."""
import html
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from car_physics_model import (
    simulate_speed_event, event_duration_for_distance, get_efficiency,
    find_optimal_gate_speed, calculate_solar_energy, percentage,
    TURBINE_THRUST_COEFFICIENT, TURBINE_AERODYNAMIC_CP,
    SOLAR_ROOF_AREA, SOLAR_IRRADIANCE, SOLAR_PANEL_EFFICIENCY,
    SOLAR_CHARGE_EFFICIENCY, REGEN_BRAKING_EFFICIENCY,
)
from driving_cycles import (DIRT_ROAD_CYCLE, CITY_CYCLE, HIGHWAY_CYCLE,
                           MOTORWAY_CYCLE, get_cycle_event)
from aerodynamic_presets import PRESETS, PRESET_MAP, SOURCES
from translations import translate, GUIDE, LIMITATIONS

st.set_page_config(page_title="Regenerative Car / Coche regenerativo", page_icon="𖣘", layout="wide")
# Read the stable language key before the heading so the title is first.
language = st.session_state.get("language", "en")
t = lambda key, **kw: translate(key, language, **kw)
st.markdown("""
<style>
.st-key-hero_title h1 {
    text-align: center;
    font-size: clamp(2.2rem, 4vw, 3.5rem);
    line-height: 1.15;
}
.st-key-language_controls [role="radiogroup"] {
    justify-content: center;
}
:is(.st-key-vehicle_inputs, .st-key-driving_inputs, .st-key-alternative_inputs)[data-testid="stVerticalBlock"],
:is(.st-key-vehicle_inputs, .st-key-driving_inputs, .st-key-alternative_inputs) [data-testid="stVerticalBlock"] {
    gap: 1.4rem;
}
.st-key-run button {
    min-height: 3.7rem;
    border-radius: .7rem;
}
.st-key-run button p {
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: .08em;
}
#braking-deceleration, [id^="net-v"], [id^="result-v"] {
    scroll-margin-top: 5rem;
}

[class*="st-key-centered_net_"] [data-testid="stCheckbox"] {
    display: flex;
    justify-content: center;
    width: 100%;
}
.st-key-comparison_selection {
    background: rgba(36,99,188,.08);
    border: 1px solid rgba(36,99,188,.22);
    border-radius: .5rem;
    padding: .6rem .8rem;
}
</style>
""", unsafe_allow_html=True)

# --- HEADER: car sketch, title, language selector ---

import base64
from pathlib import Path

image_path = Path(__file__).parent / "assets" / "turbine_car.png"
image_base64 = base64.b64encode(image_path.read_bytes()).decode()

hero_css = """
<style>
.st-key-hero_header {
    position: relative;
    isolation: isolate;
    min-height: 260px;
    padding: 3.5rem 0 4rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Car sketch as a background watermark */
.st-key-hero_header::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image: url("data:image/png;base64,IMAGE_DATA");
    background-repeat: no-repeat;
    background-position: center;
    background-size: 80% auto;
    opacity: 0.20;
    pointer-events: none;
    z-index: 0;
}

/* Keep actual content above the sketch */
.st-key-hero_header > div {
    position: relative;
    z-index: 1;
}

/* Center title */
.st-key-hero_title h1 {
    text-align: center;
    font-size: clamp(2.2rem, 4vw, 3.5rem);
    line-height: 1.15;
}

/* Center entire radio widget */
.st-key-language_controls [data-testid="stRadio"] {
    width: fit-content;
    margin-left: auto;
    margin-right: auto;
}

/* Center language choices inside the widget */
.st-key-language_controls [role="radiogroup"] {
    justify-content: center;
    flex-wrap: nowrap;
}

</style>
"""

st.markdown(
    hero_css.replace("IMAGE_DATA", image_base64),
    unsafe_allow_html=True
)

with st.container(key="hero_header"):
    with st.container(key="hero_title"):
        st.title(t("title"))

    with st.container(key="language_controls"):
        left, center, right = st.columns([2, 1, 2])

        with center:
            language = st.radio(
                "Language / Idioma",
                ["en", "es"],
                horizontal=True,
                format_func=lambda x: "English" if x == "en" else "Español",
                key="language",
                label_visibility="collapsed",
            )

GREEN, RED, BLUE, PURPLE, AMBER = "#16834b", "#c53535", "#2463bc", "#8356b5", "#b57812"


def apply_preset():
    cd = PRESET_MAP[st.session_state.preset][3]
    if cd is not None:
        st.session_state.ld = 1.0 / cd


st.session_state.setdefault("ld", 8.0)
cycle_map = {
    "dirt": DIRT_ROAD_CYCLE,
    "city": CITY_CYCLE,
    "highway": HIGHWAY_CYCLE,
    "motorway": MOTORWAY_CYCLE,
}
with st.container(border=True, key="analysis_inputs"):
    st.subheader(t("inputs"))
    left, right = st.columns(2)
    with left:
        with st.container(border=True, key="vehicle_inputs"):
            st.markdown(
                f'<h3 style="margin:0 0 .3rem">{html.escape(t("vehicle"))}</h3>'
                f'<p style="font-size:.85rem;opacity:.7;margin:0">'
                f'{html.escape(t("vehicle_subtitle"))}</p>',
                unsafe_allow_html=True,
            )
            mass = st.slider(t("mass"), 500, 3000, 2000, key="mass", help=t("mass_help"))
            preset = st.selectbox(t("preset"), [x[0] for x in PRESETS], key="preset",
                                  format_func=lambda x: PRESET_MAP[x][1 + (language == "es")],
                                  on_change=apply_preset, help=t("preset_help"))
            ld = st.slider(t("ld"), 0.5, 50.0, step=.01, format="%.3f", key="ld",
                           help=t("ld_help", cd=1 / st.session_state["ld"]))
            diameter = st.slider(t("diameter"), .1, 2.0, .5, step=.01, key="diameter", help=t("diameter_help"))
            eff_mode = st.radio(t("eff_mode"), ["realistic", "ideal"],
                                format_func=t, key="eff_mode", horizontal=True)
            eff_percent = st.slider(t("eff"), 0, 100, 40, disabled=eff_mode == "realistic", key="eff_percent", help=t("eff_help"))
            eff = get_efficiency("Realistic" if eff_mode == "realistic" else "Idealised slider", eff_percent)
            if eff_mode == "ideal":
                st.caption(t("ideal_note"))
                
        with st.container(border=True, key="alternative_inputs"):
            st.subheader(t("alternatives"))
            extra = st.checkbox(t("extra"), key="extra", help=t("extra_help"))
            sunlight = st.slider(t("sun"), 0, 100, 100, disabled=not extra, key="sun", help=t("sun_help"))
            alternative_braking_mode = st.radio(
                t("braking_mode_label"), ["calculated_braking", "normalized_braking"],
                format_func=t, key="alternative_braking_mode", disabled=not extra,
                help=t("braking_mode_help"),
            )
            normalize_braking = alternative_braking_mode == "normalized_braking"
            if extra and normalize_braking:
                st.caption(t("normalize_braking_help"))
            # elif extra and not st.session_state.get("braking", False):
               # st.markdown(t("calculated_braking_instruction"))
            
    with right:
        with st.container(border=True, key="driving_inputs"):
            st.markdown(
                f'<h3 style="margin:0 0 .3rem">{html.escape(t("drive"))}</h3>'
                f'<p style="font-size:.85rem;opacity:.7;margin:0">'
                f'{html.escape(t("drive_subtitle"))}</p>',
                unsafe_allow_html=True,
            )
            source = st.radio(t("drive_source"), ["manual", "cycle"], format_func=t,
                              key="source", horizontal=True, help=t("drive_source_help"))
            speed = st.slider(t("speed"), 0, 250, 100, disabled=source == "cycle", key="speed", help=t("speed_help"))
            cycle_id = st.selectbox(t("scenario"), ["dirt", "city", "highway", "motorway"],
                                   format_func=t, disabled=source == "manual", key="cycle_id")
            condition = st.selectbox(t("condition"), ["acceleration", "cruise"],
                                    format_func=t, disabled=source == "manual", key="condition")
            # The normal-text link in the alternatives box targets this anchor.
            st.markdown('<span id="braking-deceleration"></span>', unsafe_allow_html=True)
            braking_mode = st.checkbox(t("braking"), key="braking", help=t("braking_help"))
            grade = st.slider(t("grade"), -20, 20, 0, key="grade", help=t("grade_help"))
            distance_km = st.number_input(t("distance"), min_value=.001, max_value=10000.0,
                                          value=1.0, step=.1, format="%.3f", key="distance",
                                          help=t("distance_help"))
            closed = st.checkbox(t("closed"), key="closed", help=t("closed_help"))

            if source == "cycle":
                gate_event = get_cycle_event(
                    cycle_map[cycle_id],
                    condition,
                    braking_mode,
                )
                gate_min = float(min(
                    gate_event["start_speed"],
                    gate_event["end_speed"],
                ))
                gate_max = float(max(
                    gate_event["start_speed"],
                    gate_event["end_speed"],
                ))
            else:
                gate_min = 0.0
                gate_max = 251.0

            # Clamp the previous selection before creating the widget.
            # This prevents an old motorway threshold surviving a switch to Dirt Road.
            previous_opening = float(st.session_state.get("opening", 80.0))
            st.session_state["opening"] = min(
                max(previous_opening, gate_min),
                gate_max,
            )
            gate_help = t("gate_help")
            if source == "cycle":
                gate_help += "\n\n" + t("gate_range", low=gate_min, high=gate_max)
            opening = st.slider(
                t("gate"),
                min_value=gate_min,
                max_value=gate_max,
                step=0.1,
                disabled=closed,
                key="opening",
                help=gate_help,
            )


# Canonical submitted configuration uses internal IDs, never translated labels.
# Inactive controls are excluded so they cannot change a study's driving event.

if source == "manual":
    initial, final = float(speed), 0.0 if braking_mode else float(speed)
else:
    event = get_cycle_event(cycle_map[cycle_id], condition, braking_mode)
    initial, final = event["start_speed"], event["end_speed"]
config = dict(mass=mass, ld=ld, diameter=diameter, efficiency=eff,
              source=source, cycle=cycle_id if source == "cycle" else None,
              condition=condition if source == "cycle" else None,
              initial=initial, final=final, grade=grade, distance_m=distance_km*1000,
              opening=opening if not closed else None, closed=closed,
              braking=braking_mode, extra=extra, sunlight=sunlight if extra else 0, 
              normalize_braking=bool(
                 normalize_braking and extra
              ))


def analyse(c):
    duration = event_duration_for_distance(c["initial"], c["final"], c["distance_m"])
    args = (c["initial"], c["final"], duration, c["mass"], c["ld"], c["diameter"], c["efficiency"])
    v1 = simulate_speed_event(*args, grade=c["grade"])
    v2 = simulate_speed_event(*args, grade=c["grade"],
        gate_mode="closed" if c["closed"] else "smart", opening_speed=c["opening"] or 0)
    no_turbine = simulate_speed_event(*args, grade=c["grade"], gate_mode="closed")
    best, scan = find_optimal_gate_speed(*args, grade=c["grade"])
    recommended = (simulate_speed_event(*args, grade=c["grade"], gate_mode="smart",
                                        opening_speed=best["opening_speed"]) if best else None)
    return dict(config=dict(c), v1=v1, v2=v2, baseline=no_turbine,
                recommended=recommended, best=best, scan=scan)



invalid_calculated_mode = (
    extra
    and not normalize_braking
    and not braking_mode
)

if invalid_calculated_mode:
    st.warning(t("calculated_braking_instruction"))


if st.button(
    t("run"),
    type="primary",
    key="run",
    width="stretch",
    disabled=invalid_calculated_mode,
):

    try:
        st.session_state.study = analyse(config)
        # Reset display switches after a new study, not on language changes.
        for key in list(st.session_state):
            if key.startswith("view_"):
                del st.session_state[key]
        st.session_state.analysis_error = False
    except ValueError:
        st.session_state.analysis_error = True
if st.session_state.get("analysis_error"):
    st.error(t("invalid"))
if "study" not in st.session_state:
    st.info(t("ready"))
    st.stop()
study = st.session_state.study
if config != study["config"]:
    st.warning(t("pending"))
c = study["config"]
v1, v2 = study["v1"], study["v2"]


def plot_lines(x, series, ylabel="power", xlabel="time", suffix="", markers=None, chart_help=True):
    if chart_help:
        st.markdown(t("chart_help"), help=t("sign_note"))
    fig, ax = plt.subplots(figsize=(10, 3.5))
    for label, values, colour, style in series:
        ax.plot(x, values, label=textwrap.fill(label, 48), color=colour, linestyle=style, linewidth=2)
    for label, position, colour in markers or []:
        ax.axvline(position, label=label, color=colour, linestyle=":", linewidth=1.4)
    ax.axhline(0, color="#666", linewidth=.8)
    ax.set_xlabel(t(xlabel))
    ax.set_ylabel(t(ylabel) + suffix)
    ax.grid(alpha=.15)
    ax.legend(loc="upper left", bbox_to_anchor=(0, 1.25), frameon=False, ncol=2, fontsize=8)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def cumulative(result, power):
    return np.r_[0., np.cumsum(power) * result["trace"]["dt_s"] / 3600]


def formatted(value, unit="Wh", polarity="neutral"):
    if value is None:
        return html.escape(t("na"))
    colour = GREEN if polarity == "return" else RED if polarity == "loss" else "inherit"
    if polarity == "net":
        colour = GREEN if value > 1e-9 else RED if value < -1e-9 else "inherit"
    if polarity == "cost":
        colour = RED if value > 1e-9 else GREEN if value < -1e-9 else "inherit"
    prefix = "+" if polarity == "return" and value > 0 else "−" if polarity == "loss" and value > 0 else ""
    number = f"{value:+.2f}" if polarity == "net" else f"{value:.2f}"
    return f'<span style="color:{colour};font-weight:600">{prefix}{number} {html.escape(unit)}</span>'


def table(rows, columns, anchor_prefix=None):
    # All strings are escaped; only locally produced numeric colour spans are HTML.
    out = ['<table style="width:100%;border-collapse:collapse"><thead><tr>',
           f'<th style="text-align:left;padding:8px">{html.escape(t("quantity"))}</th>']
    out += [f'<th style="text-align:right;padding:8px">{html.escape(col)}</th>' for col in columns]
    out.append('</tr></thead><tbody>')
    for key, values, unit, polarity in rows:
        anchor = f' id="result-{anchor_prefix}-{key}"' if anchor_prefix else ""
        out.append(f'<tr{anchor} style="border-top:1px solid #8884"><td style="padding:8px">{html.escape(t(key))}</td>')
        for value in values:
            out.append(f'<td style="padding:8px;text-align:right">{formatted(value, unit, polarity)}</td>')
        out.append('</tr>')
    out.append('</tbody></table>')
    st.markdown(''.join(out), unsafe_allow_html=True)


def result_rows(results):
    definitions = [
        ("generation", lambda r: r["recovered_energy"]/3600, "Wh", "return"),
        ("penalty", lambda r: r["turbine_drag_energy"]/3600, "Wh", "loss"),
        ("net_turbine", lambda r: (r["recovered_energy"]-r["turbine_drag_energy"])/3600, "Wh", "net"),
        ("baseline", lambda r: r["vehicle_drag_energy"]/3600, "Wh", "loss"),
        ("aero", lambda r: r["total_aerodynamic_energy"]/3600, "Wh", "loss"),
        ("spent", lambda r: r["total_energy_spent"]/3600, "Wh", "loss"),
        ("remaining", lambda r: r["net_event_energy_after_recovery"]/3600, "Wh", "cost"),
        ("offset_penalty", lambda r: r["recovery_vs_turbine_penalty_pct"], "%", "neutral"),
        ("offset_aero", lambda r: r["recovery_vs_total_aero_pct"], "%", "neutral"),
        ("offset_spent", lambda r: r["recovery_vs_total_spent_pct"], "%", "neutral"),
        ("yield", lambda r: r["recovered_wh_per_km"], "Wh/km", "return"),
        ("open_time", lambda r: r["open_time_s"], "s", "neutral"),
    ]
    return [(key, [fn(r) if r is not None else None for r in results], unit, polarity)
            for key, fn, unit, polarity in definitions]


def guide():
    with st.expander(t("guide")):
        st.markdown(GUIDE[language == "es"].format(ct=TURBINE_THRUST_COEFFICIENT))


def gate_opening_time(result):
    """Read opening transitions from the simulated gate state, not the input threshold."""
    active = result["trace"]["gate_open"]
    transitions = np.flatnonzero(~active[:-1] & active[1:]) + 1
    return (float(result["trace"]["time_edges_s"][transitions[0]])
            if len(transitions) else None)


def percent_text(value):
    return f"{value:.2f}%" if value is not None else t("na")


def technical_key(kind):
    keys = (
        ["key_generation", "key_turbine_drag", "key_turbine_net"]
        if kind == "turbine"
        else ["key_generation", "key_propulsion", "key_drive_net"]
    )

    # Match the text colors to the existing graph colors.
    key_colours = {
        "key_generation": GREEN,
        "key_turbine_drag": RED,
        "key_turbine_net": BLUE,
        "key_propulsion": RED,
        "key_drive_net": BLUE,
    }

    with st.expander(t("chart_help"), expanded=False):
        items = []

        for key in keys:
            # Separate the bold heading from its explanation.
            heading, _, description = (
                t(key).removeprefix("**").partition("**")
            )

            items.append(
                f'<li>'
                f'<span style="color:{key_colours[key]}; '
                f'font-weight:700;">'
                f'{html.escape(heading)}'
                f'</span>'
                f'{html.escape(description)}'
                f'</li>'
            )

        st.markdown(
            "<ul>" + "".join(items) + "</ul>",
            unsafe_allow_html=True
        )



def version_graphs(result, prefix):
    z, x = result["trace"], result["trace"]["time_s"]
    opening_time = gate_opening_time(result)
    st.subheader(t("g1"))
    explanation = t("g1_intro", anchor=f"net-{prefix}-turbine")
    if prefix == "v2":
        if opening_time is not None:
            explanation += " " + t("gates_transition", time=opening_time)
        elif z["gate_open"][0]:
            explanation += " " + t("gates_start")
        else:
            explanation += " " + t("gates_closed")
    st.markdown(explanation)
    st.markdown(f'<span id="net-{prefix}-turbine"></span>', unsafe_allow_html=True)
    with st.container(key=f"centered_net_{prefix}_turbine"):
        show_net = st.checkbox(t("net_toggle"), key=f"view_{prefix}_turbine")
    technical_key("turbine")
    lines = [(t("generation"), z["recovered_power"], GREEN, "-"),
             (t("penalty"), -z["turbine_drag_power"], RED, "-")]
    if show_net:
        lines.append((t("net_turbine"), z["turbine_net_power"], BLUE, "--"))
    plot_lines(x, lines, chart_help=False)

    st.subheader(t("g2"))
    share = percentage(result["turbine_drag_energy"], result["total_aerodynamic_energy"])

    paragraph, bold_text, trailing = t(
        "g2_intro", share=percent_text(share)
    ).split("**")

    # Display the explanatory paragraph normally.
    st.markdown(paragraph.strip())

    # Display the bold statistic on its own, centered line.
    st.markdown(
        f'<p style="text-align:center; font-weight:700; margin:0.5rem 0;">'
        f'{html.escape(bold_text + trailing.strip())}</p>',
        unsafe_allow_html=True,
    )

    with st.expander(t("chart_help"), expanded=False):
        st.markdown(t("key_areas"))
        st.markdown("- " + t("key_vehicle_area", anchor=f"result-{prefix}-baseline")
                    + "\n- " + t("key_turbine_area", anchor=f"result-{prefix}-penalty"))
        st.markdown(t("key_accumulation"))
    # Signed stacked areas show composition, unlike a pie chart which hides time.
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.stackplot(x, -z["vehicle_drag_power"], -z["turbine_drag_power"],
                 labels=[t("baseline"), t("penalty")], colors=["#bf7777", RED], alpha=.8)
    ax.axhline(0, color="#666", linewidth=.8)
    ax.set_xlabel(t("time")); ax.set_ylabel(t("power")); ax.grid(alpha=.15)
    ax.legend(loc="upper left", bbox_to_anchor=(0, 1.2), frameon=False, ncol=2, fontsize=8)
    fig.tight_layout(); st.pyplot(fig, width="stretch"); plt.close(fig)

    st.subheader(t("g3"))

    paragraph, bold_text, trailing = t(
        "g3_intro",
        aero=percent_text(result["recovery_vs_total_aero_pct"]),
        spent=percent_text(result["recovery_vs_total_spent_pct"]),
    ).split("**")

    # Preserve the gates explanation for Version 2.
    if prefix == "v2":
        paragraph = paragraph.strip() + " " + t(
            "gates_propulsion_transition"
            if opening_time is not None
            else "gates_propulsion"
        )

    # Display only the explanatory paragraph.
    st.markdown(paragraph.strip())

    # Display the bold statistics centered underneath.
    st.markdown(
        f'<p style="text-align:center; font-weight:700; margin:0.5rem 0;">'
        f'{html.escape(bold_text + trailing.strip())}</p>',
        unsafe_allow_html=True,
    )

    st.markdown(f'<span id="net-{prefix}-drive"></span>', unsafe_allow_html=True)
    with st.container(key=f"centered_net_{prefix}_drive"):
        show_balance = st.checkbox(t("net_drive_toggle"), key=f"view_{prefix}_drive")
    technical_key("drive")
    lines = [(t("generation"), z["recovered_power"], GREEN, "-"),
             (t("spent"), -z["propulsion_power"], RED, "-")]
    if show_balance:
        lines.append((t("net_drive"), z["net_event_power"], BLUE, "--"))
    plot_lines(x, lines, chart_help=False)


def summary_cards(result, key, accent=BLUE):
    values = ([result["recovered_energy"] / 3600, result["recovery_vs_total_spent_pct"],
               result["recovered_wh_per_km"]] if result is not None else [None, None, None])
    with st.container(key=key):
        for column, label, value in zip(st.columns(3),
                ["card_generation", "card_ratio", "card_yield"], values):
            with column:
                number = f"{value:.2f}" if value is not None else t("na")
                st.markdown(
                    f'<div style="border:1px solid #8884;border-top:3px solid {accent};'
                    f'border-radius:.5rem;padding:1rem;height:100%;">'
                    f'<div style="font-size:.85rem;line-height:1.35">{html.escape(t(label))}</div>'
                    f'<div style="font-size:1.9rem;font-weight:600;margin-top:.5rem">'
                    f'{html.escape(number)}</div></div>', unsafe_allow_html=True)


def threshold_key(absolute=False):
    keys = ["scan_key_generation", "scan_key_drag"] if absolute else [
        "scan_key_retained", "scan_key_exposure", "scan_key_score"]
    if not c["closed"]:
        keys.append("scan_key_user")
    if study["best"]:
        keys.append("scan_key_best_energy" if absolute else "scan_key_best")
    with st.expander(t("chart_help"), expanded=False):
        st.markdown("\n".join("- " + t(key) for key in keys))


def aerodynamic_pie(result, version):
    st.subheader(t("pie_title", version=version))
    total = result["total_aerodynamic_energy"]
    if total <= 1e-12:
        st.info(t("pie_unavailable"))
        return
    values = [result["vehicle_drag_energy"], result["turbine_drag_energy"]]
    labels = [textwrap.fill(t(key), 34) + f"\n{percentage(value, total):.2f}%"
              for key, value in zip(["baseline", "penalty"], values)]
    fig, ax = plt.subplots(figsize=(6, 4.5))
    wedges, _ = ax.pie(values, colors=["#bf7777", RED], startangle=90)
    ax.legend(wedges, labels, loc="lower center", bbox_to_anchor=(.5, -.18),
              frameon=False, fontsize=9)
    fig.tight_layout(); st.pyplot(fig, width="stretch"); plt.close(fig)


# --- OUTPUT TAB STYLING ---

st.html("""
<style>
/* Main tab navigation */
:is(.stTabs, [data-testid="stTabs"]) [role="tablist"] {
    gap: 8px !important;
    padding: 10px 0 16px !important;
    overflow-x: auto !important;
}

/* Individual tab buttons */
:is(.stTabs, [data-testid="stTabs"]) [role="tab"] {
    min-height: 48px !important;
    padding: 10px 15px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(128,128,128,0.4) !important;
    background: rgba(128,128,128,0.08) !important;
    flex-shrink: 0 !important;
}

/* Force large font on tab labels and nested text */
:is(.stTabs, [data-testid="stTabs"]) [role="tab"],
:is(.stTabs, [data-testid="stTabs"]) [role="tab"] * {
    font-size: 17px !important;
    font-weight: 700 !important;
    line-height: 1.3 !important;
}

/* Highlight selected tab */
:is(.stTabs, [data-testid="stTabs"]) [role="tab"][aria-selected="true"] {
    background: rgba(36,99,188,0.18) !important;
    border: 2px solid #2463bc !important;
}

/* Hover */
:is(.stTabs, [data-testid="stTabs"]) [role="tab"]:hover {
    background: rgba(36,99,188,0.10) !important;
}
</style>
""")


labels = [t("v1"), t("v2"), t("comparison")]
if c["extra"]:
    labels.append(t("alternatives"))
labels.append(t("limitations"))
tabs = st.tabs(labels)

with tabs[0]:
    version_graphs(v1, "v1")
    st.subheader(t("v1_results"))
    summary_cards(v1, "summary_v1")
    st.markdown(t("v1_results_intro"))
    table(result_rows([v1]), [t("value")], anchor_prefix="v1")
    guide()
with tabs[1]:
    version_graphs(v2, "v2")
    st.subheader(t("scan_title"))
    best = study["best"]
    st.markdown(t("scan_intro") + " " + (t("scan_recommendation", speed=best["opening_speed"])
                if best else t("no_threshold")))
    if best:
        st.markdown(t("threshold_result", speed=best["opening_speed"],
                      retained=best["retained_generation_pct"], exposure=best["exposure_time_pct"])
                    + " " + t("scan_objective"))
    st.markdown(t("scan_tradeoff"))
    st.markdown(t("scan_formula"))
    st.markdown(t("closed_reference", spent=study["baseline"]["total_energy_spent"]/3600))
    rows = [r for r in study["scan"] if r["policy"] != "closed"]
    markers = []
    if not c["closed"]:
        markers.append((t("selected"), c["opening"], PURPLE))
    if study["best"]:
        markers.append((t("recommended"), study["best"]["opening_speed"], AMBER))
    threshold_key()
    plot_lines([r["opening_speed"] for r in rows], [
        (t("retained"), [r["retained_generation_pct"] for r in rows], GREEN, "-"),
        (t("exposure"), [r["exposure_time_pct"] for r in rows], RED, "-"),
        (t("score"), [r["concentration_score"]*100 for r in rows], BLUE, "--"),
    ], ylabel="value", xlabel="scan_x", suffix=" (%)", markers=markers, chart_help=False)
    # Separate absolute-energy plot makes the retained-fraction scan interpretable.
    threshold_key(absolute=True)
    plot_lines([r["opening_speed"] for r in rows], [
        (t("generation"), [r["recovered_energy"]/3600 for r in rows], GREEN, "-"),
        (t("penalty"), [-r["turbine_drag_energy"]/3600 for r in rows], RED, "-"),
    ], ylabel="energy", xlabel="scan_x", markers=markers, chart_help=False)
    st.subheader(t("results"))
    st.markdown(f'**{t("user_summary")}**')
    summary_cards(v2, "summary_v2_user", PURPLE)
    st.markdown(f'**{t("recommended_summary")}**')
    if best is None:
        st.markdown(t("no_threshold"))
    summary_cards(study["recommended"], "summary_v2_recommended", AMBER)
    st.markdown(t("v2_results_intro"))
    table([("chosen_gate", [None if c["closed"] else c["opening"], best["opening_speed"] if best else None], "km/h", "neutral")]
          + result_rows([v2, study["recommended"]]), [t("selected"), t("recommended")], anchor_prefix="v2")
    if c["closed"]:
        st.caption(t("closed"))
    guide()
with tabs[2]:
    with st.container(key="comparison_selection"):
        compare_user = st.checkbox(t("compare_selector"), key="view_comparison_user", value=False)
    # Direct Comparison uses the generation-concentration recommendation by default.
    # At constant speed there is no distinct recommendation: use always open.
    comparison_v1 = v1
    comparison_v2 = (v2 if compare_user else
                     study["recommended"] if study["recommended"] is not None else v1)
    st.subheader(t("compare_title"))
    explanation = t("compare_intro")
    if compare_user:
        explanation += " " + t("compare_closed" if c["closed"] else "compare_user")
        if not c["closed"]:
            explanation += " " + t("comparison_threshold", speed=c["opening"])
    elif study["best"] is not None:
        explanation += " " + t("compare_recommended")
        explanation += " " + t("comparison_threshold", speed=study["best"]["opening_speed"])
    else:
        explanation += " " + t("comparison_no_threshold")
    st.markdown(explanation)
    keys = ["generation", "penalty", "aero", "spent"]
    vals = [[r["recovered_energy"]/3600, -r["turbine_drag_energy"]/3600,
             -r["total_aerodynamic_energy"]/3600, -r["total_energy_spent"]/3600] for r in (comparison_v1, comparison_v2)]
    fig, ax = plt.subplots(figsize=(10, 4))
    positions = np.arange(len(keys))
    for i, (version, colour) in enumerate([(t("v1"), BLUE), (t("v2"), PURPLE)]):
        bars = ax.bar(positions + (i-.5)*.36, vals[i], width=.36, color=colour, label=version)
        ax.bar_label(bars, labels=[f"{value:.2f}" for value in vals[i]],
                     label_type="edge", padding=4, fontsize=8)
    ax.margins(y=.18)
    ax.axhline(0, color="#666", linewidth=.8)
    ax.set_xticks(positions, [textwrap.fill(t(k), 24) for k in keys]); ax.tick_params(axis="x", labelsize=8)
    ax.set_ylabel(t("energy")); ax.legend(); fig.tight_layout()
    st.pyplot(fig, width="stretch"); plt.close(fig)
    if np.allclose(vals[0], vals[1]):
        st.markdown(t("equal_note"))
    st.subheader(t("compare_lines"))
    st.markdown(t("compare_cumulative") + (" " + t("compare_opening")
                if gate_opening_time(comparison_v2) is not None else ""))
    plot_lines(
        comparison_v1["trace"]["time_edges_s"],
        [
            (
                t("v1"),
                cumulative(
                    comparison_v1,
                    comparison_v1["trace"]["net_event_power"],
                ),
                BLUE,
                "-",
            ),
            (
                t("v2"),
                cumulative(
                    comparison_v2,
                    comparison_v2["trace"]["net_event_power"],
                ),
                PURPLE,
                "--",
            ),
        ],
        ylabel="energy", chart_help=False,
    )
    for column, result, version in zip(st.columns(2), [comparison_v1, comparison_v2], [1, 2]):
        with column:
            aerodynamic_pie(result, version)
    st.subheader(t("compare_results"))
    st.markdown(f'**{t("v1")}**')
    summary_cards(comparison_v1, "summary_comparison_v1", BLUE)
    st.markdown(f'**{t("comparison_summary")}**')
    summary_cards(comparison_v2, "summary_comparison_v2", PURPLE)
    table(
        result_rows([comparison_v1, comparison_v2]),
        [t("v1"), t("v2")],
    )
    guide()

if c["extra"]:
    with tabs[3]:
                # Changes here affect only the alternative-methods tab.
        alternative_study = study


        if c["normalize_braking"]:
            reference_duration = 20.0
            alternative_config = dict(c)

            # Always build a genuine braking event,
            # independent of the main checkbox.
            if c["source"] == "cycle":
                braking_event = get_cycle_event(
                    cycle_map[c["cycle"]],
                    c["condition"],
                    braking_mode=True,
                )
                alternative_config["initial"] = braking_event["start_speed"]
                alternative_config["final"] = braking_event["end_speed"]
            else:
                alternative_config["initial"] = c["initial"]
                alternative_config["final"] = 0.0

            alternative_config["braking"] = True

            # Set distance so this linear braking
            # event lasts exactly 20 seconds.
            average_speed_ms = (
                alternative_config["initial"]
                + alternative_config["final"]
            ) / 7.2

            reference_distance = (
                average_speed_ms * reference_duration
            )

            if reference_distance > 0:
                alternative_config["distance_m"] = reference_distance
                alternative_study = analyse(alternative_config)



        alternative_v1 = alternative_study["v1"]
        alternative_v2 = alternative_study["v2"]

        def combined_energy_cost(result):
            regen_credit = (
                result["braking_energy_to_dissipate"]
                * REGEN_BRAKING_EFFICIENCY
                if c["braking"] or c["normalize_braking"]
                else 0.0
            )

            return (
                result["total_energy_spent"]
                - result["recovered_energy"]
                - regen_credit
            )

        best_version = (
            "v2"
            if combined_energy_cost(alternative_v2)
            < combined_energy_cost(alternative_v1) - 1e-9
            else "v1"
        )


        chosen = alternative_study[best_version]
        z = chosen["trace"]

        solar = calculate_solar_energy(
            chosen["duration_s"],
            c["sunlight"],
        )

        # Calculated mode requires the main braking flag. Normalized mode uses
        # the existing braking demand of its unchanged 20-second reference event.
        if c["braking"] or c["normalize_braking"]:
            regen_standalone = (
                alternative_study["baseline"]["braking_energy_to_dissipate"]
                * REGEN_BRAKING_EFFICIENCY
            )
            regen_combined_power = (
                z["braking_power"] * REGEN_BRAKING_EFFICIENCY
            )
        else:
            regen_standalone = 0.0
            regen_combined_power = np.zeros_like(z["braking_power"])

        regen_combined = float(
            np.sum(regen_combined_power) * z["dt_s"]
        )
        st.info((t("normalized_event") + " " if c["normalize_braking"] else "")
                + t("alternative_reference", duration=(f'{chosen["duration_s"]:.0f}'
                    if c["normalize_braking"] else f'{chosen["duration_s"]:.2f}'),
                    distance=chosen["distance_m"] / 1000,
                    speed=chosen["distance_m"] / chosen["duration_s"] * 3.6))
        st.caption(t("best_note", version=t(best_version)))
        if not c["braking"] and not c["normalize_braking"]:
            st.markdown(t("calculated_braking_instruction"))

        elif c["normalize_braking"] and not c["braking"]:
            st.markdown(t("normalized_limitation"))

        st.subheader(t("methods"))
        method_values = [chosen["recovered_energy"]/3600, regen_standalone/3600, solar["solar_energy"]/3600]
        highest = max(method_values)
        explanation = t("methods_intro")
        if highest > 0:
            winners = [t(key) for key, value in zip(["generation", "regen", "solar"], method_values)
                       if value == highest]
            explanation += " " + t("methods_winner" if len(winners) == 1 else "methods_tie",
                                    methods=", ".join(winners), energy=highest)
        else:
            explanation += " " + t("methods_zero")
        st.markdown(explanation)
        fig, ax = plt.subplots(figsize=(10, 3.5))
        ax.bar([textwrap.fill(t("generation"), 26), t("regen"), t("solar")],
               [chosen["recovered_energy"]/3600, regen_standalone/3600, solar["solar_energy"]/3600],
               color=[GREEN, BLUE, AMBER])
        ax.set_ylabel(t("energy")); fig.tight_layout()
        st.pyplot(fig, width="stretch"); plt.close(fig)
        st.caption(t("standalone_note"))
        st.subheader(t("combined"))
        st.markdown(t("solar_note", sun=c["sunlight"], irr=SOLAR_IRRADIANCE, area=SOLAR_ROOF_AREA,
                     panel=SOLAR_PANEL_EFFICIENCY*100, charge=SOLAR_CHARGE_EFFICIENCY*100,
                     power=solar["solar_power"]))
        st.markdown(t("regen_note", eff=REGEN_BRAKING_EFFICIENCY*100))
        st.markdown(t("charge_note"))
        show = st.checkbox(t("combined_toggle"), key="view_combined")
        solar_power = np.full_like(z["time_s"], solar["solar_power"])
        combined_power = -z["propulsion_power"] + z["recovered_power"] + regen_combined_power + solar_power
        series = [(t("spent"), cumulative(chosen, -z["propulsion_power"]), RED, "-"),
                  (t("generation"), cumulative(chosen, z["recovered_power"]), GREEN, "-"),
                  (t("regen_combined"), cumulative(chosen, regen_combined_power), BLUE, "-"),
                  (t("solar"), cumulative(chosen, solar_power), AMBER, "-")]
        if show:
            series.append((t("combined_net"), cumulative(chosen, combined_power), PURPLE, "--"))
        plot_lines(z["time_edges_s"], series, ylabel="energy", chart_help=False)

        total = chosen["recovered_energy"] + regen_combined + solar["solar_energy"]
        st.subheader(t("method_table"))
        table([
            ("generation", [chosen["recovered_energy"]/3600], "Wh", "return"),
            ("standalone_regen", [regen_standalone/3600], "Wh", "return"),
            ("regen_combined", [regen_combined/3600], "Wh", "return"),
            ("solar", [solar["solar_energy"]/3600], "Wh", "return"),
            ("total_returns", [total/3600], "Wh", "return"),
            ("spent", [chosen["total_energy_spent"]/3600], "Wh", "loss"),
            ("combined_net", [(total-chosen["total_energy_spent"])/3600], "Wh", "net"),
        ], [t("value")])

with tabs[-1]:
    st.header(t("limitations"))
    st.markdown(LIMITATIONS[language == "es"])

    with st.expander(t("preset_sources")):
        st.caption(t("f1_note"))
        st.dataframe(pd.DataFrame({t("preset"): [r[1 + (language == "es")] for r in PRESETS[1:]],
                                  t("cd"): [r[3] for r in PRESETS[1:]],
                                  t("ld"): [1/r[3] for r in PRESETS[1:]]}), hide_index=True)
        for name, url in SOURCES:
            st.markdown(f"[{name.rsplit(' / ', 1)[language == 'es'] if ' / ' in name else name}]({url})")
