import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from car_physics_model import (
    calculate_energy,
    get_efficiency,
    simulate_speed_event,
    find_optimal_gate_speed,
)

from driving_cycles import (
    DIRT_ROAD_CYCLE,
    CITY_CYCLE,
    HIGHWAY_CYCLE,
    MOTORWAY_CYCLE,
    NORMALIZED_EVENT_DURATION,
    get_cycle_event,
    simulate_cycle,
)


st.set_page_config(
    page_title="Regenerative Car Model",
    page_icon="🚗",
    layout="wide",
)

st.title("🚗 Regenerative Car Simulator")


# ==================================================
# HELPERS
# ==================================================


def kj(value):
    return value / 1000.0


def render_event_metrics(result, braking_mode=False):
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Electrical energy generated",
        f"{kj(result['recovered_energy']):.2f} kJ",
    )

    col2.metric(
        "Turbine aerodynamic penalty",
        f"{kj(result['turbine_drag_energy']):.2f} kJ",
    )

    col3.metric(
        "Net turbine energy cost",
        f"{kj(result['turbine_drag_energy'] - result['recovered_energy']):.2f} kJ",
    )

    col4, col5, col6 = st.columns(3)

    if result["total_energy_spent"] > 0:
        col4.metric(
            "Generated / total energy spent",
            f"{result['recovery_vs_total_spent_pct']:.2f}%",
        )
    else:
        col4.metric(
            "Generated / total energy spent",
            "N/A",
        )

    col5.metric(
        "Generated / turbine penalty",
        f"{result['recovery_vs_turbine_penalty_pct']:.2f}%",
    )

    if braking_mode:
        col6.metric(
            "Generated / kinetic energy lost",
            f"{result['recovery_vs_kinetic_loss_pct']:.2f}%",
        )
    else:
        col6.metric(
            "Net battery-side event energy",
            f"{kj(result['net_battery_energy']):.2f} kJ",
        )

    st.caption(
        f"Normalized event: {result['duration_s']:.0f} s, "
        f"{result['distance_m']:.0f} m travelled. "
        f"Turbine open for {result['open_time_s']:.1f} s."
    )


# ==================================================
# GLOBAL INPUTS
# ==================================================

st.sidebar.header("Vehicle")

mass = st.sidebar.slider(
    "Mass (kg)",
    500,
    3000,
    2000,
)

LD = st.sidebar.slider(
    "L/D ratio",
    2.0,
    15.0,
    8.0,
)

diameter = st.sidebar.slider(
    "Turbine diameter (m)",
    0.1,
    2.0,
    0.5,
)

eff_mode = st.sidebar.radio(
    "Efficiency model",
    [
        "Realistic",
        "Idealised slider",
    ],
)

if eff_mode == "Idealised slider":
    efficiency = st.sidebar.slider(
        "Energy transfer efficiency (%)",
        0,
        100,
        40,
    )
else:
    efficiency = 0

eff = get_efficiency(
    eff_mode,
    efficiency,
)

st.sidebar.divider()
st.sidebar.header("Driving event")

variable_cycle = st.sidebar.checkbox(
    "Use a predefined driving scenario"
)

selected_cycle = None
cycle_name = None
event_type = "acceleration"

if variable_cycle:
    cycle_name = st.sidebar.selectbox(
        "Driving scenario",
        [
            "Dirt Road",
            "City",
            "Highway",
            "Motorway",
        ],
    )

    cycle_map = {
        "Dirt Road": DIRT_ROAD_CYCLE,
        "City": CITY_CYCLE,
        "Highway": HIGHWAY_CYCLE,
        "Motorway": MOTORWAY_CYCLE,
    }

    selected_cycle = cycle_map[cycle_name]

    event_type = st.sidebar.selectbox(
        "Driving condition",
        ["Acceleration", "Cruise"],
    ).lower()

grade = st.sidebar.slider(
    "Road gradient (%)",
    -20,
    20,
    0,
)

braking_mode = st.sidebar.checkbox(
    "Analyse braking / deceleration"
)

st.sidebar.caption(
    f"Synthetic events use a common {NORMALIZED_EVENT_DURATION:.0f} s duration. "
    "Distance is calculated from the speed trace rather than imposed separately."
)


# ==================================================
# TABS
# ==================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Version 1 - Always Open",
        "Version 2 - Smart Gates",
        "Direct Comparison",
        "Limitations",
    ]
)


# ==================================================
# VERSION 1
# ==================================================

with tab1:
    st.header("Version 1 - Turbine always open")

    if variable_cycle:
        v1_result = simulate_cycle(
            selected_cycle,
            mass,
            LD,
            diameter,
            eff,
            "always_open",
            grade,
            braking_mode,
            event_type,
        )

        event = v1_result["event"]
        st.write(
            f"Scenario: **{cycle_name} / {event_type.capitalize()}** — "
            f"{event['start_speed']:.0f} → {event['end_speed']:.0f} km/h"
        )

    else:
        speed = st.slider(
            "Vehicle speed (km/h)",
            0,
            250,
            100,
            key="v1_speed",
        )

        if braking_mode:
            v1_initial_speed = speed
            v1_final_speed = 0
        else:
            # With no driving scenario selected, Version 1 is treated as a
            # normalized constant-speed event.
            v1_initial_speed = speed
            v1_final_speed = speed

        v1_result = simulate_speed_event(
            v1_initial_speed,
            v1_final_speed,
            NORMALIZED_EVENT_DURATION,
            mass,
            LD,
            diameter,
            eff,
            gate_mode="always_open",
            grade=grade,
        )

    render_event_metrics(
        v1_result,
        braking_mode,
    )

    st.divider()
    st.subheader("Instantaneous power across vehicle speed")

    speeds = np.linspace(1, 250, 150)
    recovery = []
    turbine_penalty = []
    vehicle_drag = []

    for s in speeds:
        result = calculate_energy(
            mass,
            s,
            LD,
            diameter,
            eff,
            True,
            grade,
        )

        recovery.append(result["recovered_power"])
        turbine_penalty.append(result["turbine_drag_power"])
        vehicle_drag.append(result["vehicle_drag_power"])

    fig, ax = plt.subplots()
    ax.plot(speeds, recovery, label="Electrical generation")
    ax.plot(speeds, turbine_penalty, label="Turbine aerodynamic penalty")
    ax.plot(speeds, vehicle_drag, label="Baseline vehicle aerodynamic drag")
    ax.set_xlabel("Speed (km/h)")
    ax.set_ylabel("Power (W)")
    ax.legend()
    st.pyplot(fig)


# ==================================================
# VERSION 2
# ==================================================

with tab2:
    st.header("Version 2 - Smart gate turbine")

    if variable_cycle:
        v2_event = get_cycle_event(
            selected_cycle,
            event_type,
            braking_mode,
        )

        v2_initial_speed = v2_event["start_speed"]
        v2_final_speed = v2_event["end_speed"]
        v2_duration = v2_event["duration"]

        speed_low = int(min(v2_initial_speed, v2_final_speed))
        speed_high = int(max(v2_initial_speed, v2_final_speed))
        default_opening = int(round((speed_low + speed_high) / 2))

        opening_speed = st.slider(
            "Gate opening threshold (km/h)",
            speed_low,
            speed_high,
            default_opening,
            key="v2_cycle_opening",
        )

        st.write(
            f"Scenario: **{cycle_name} / {event_type.capitalize()}** — "
            f"{v2_initial_speed:.0f} → {v2_final_speed:.0f} km/h"
        )

    else:
        max_speed = st.slider(
            "Final / maximum vehicle speed (km/h)",
            1,
            250,
            150,
            key="v2_max_speed",
        )

        opening_speed = st.slider(
            "Gate opening threshold (km/h)",
            0,
            max_speed,
            min(80, max_speed),
            key="v2_manual_opening",
        )

        v2_duration = NORMALIZED_EVENT_DURATION

        if braking_mode:
            v2_initial_speed = max_speed
            v2_final_speed = 0
        else:
            v2_initial_speed = 0
            v2_final_speed = max_speed

    v2_result = simulate_speed_event(
        v2_initial_speed,
        v2_final_speed,
        v2_duration,
        mass,
        LD,
        diameter,
        eff,
        gate_mode="smart",
        opening_speed=opening_speed,
        grade=grade,
    )

    render_event_metrics(
        v2_result,
        braking_mode,
    )

    st.divider()
    st.subheader("Gate-opening threshold scan")

    best_gate, gate_scan = find_optimal_gate_speed(
        v2_initial_speed,
        v2_final_speed,
        v2_duration,
        mass,
        LD,
        diameter,
        eff,
        grade,
    )

    if best_gate is not None:
        st.success(
            f"Best threshold in this simplified event: "
            f"{best_gate['opening_speed']} km/h, maximizing "
            f"{best_gate['objective_label']}."
        )

        scan_df = pd.DataFrame(gate_scan)

        display_scan = pd.DataFrame({
            "Opening speed (km/h)": scan_df["opening_speed"],
            "Generated energy (kJ)": scan_df["recovered_energy"] / 1000.0,
            "Turbine penalty (kJ)": scan_df["turbine_drag_energy"] / 1000.0,
            "Generated / total spent (%)": scan_df[
                "recovery_vs_total_spent_pct"
            ],
            "Generated / turbine penalty (%)": scan_df[
                "recovery_vs_turbine_penalty_pct"
            ],
            "Generated / kinetic loss (%)": scan_df[
                "recovery_vs_kinetic_loss_pct"
            ],
        })

        fig, ax = plt.subplots()
        ax.plot(
            display_scan["Opening speed (km/h)"],
            display_scan["Generated / total spent (%)"],
            label="Generated / total spent",
        )

        if braking_mode:
            ax.plot(
                display_scan["Opening speed (km/h)"],
                display_scan["Generated / kinetic loss (%)"],
                label="Generated / kinetic energy lost",
            )

        ax.set_xlabel("Gate opening threshold (km/h)")
        ax.set_ylabel("Recovery ratio (%)")
        ax.legend()
        st.pyplot(fig)

        penalty_ratios = scan_df.loc[
            scan_df["turbine_drag_energy"] > 0,
            "recovery_vs_turbine_penalty_pct",
        ]

        if (
            not penalty_ratios.empty
            and penalty_ratios.max() - penalty_ratios.min() < 1e-9
        ):
            st.info(
                "Under the current constant-efficiency turbine model, "
                "generated energy / turbine aerodynamic penalty is constant "
                "whenever the turbine is open. The gate threshold therefore "
                "cannot create a special speed where that instantaneous ratio "
                "suddenly becomes better."
            )

        st.dataframe(
            display_scan,
            use_container_width=True,
            hide_index=True,
        )


# ==================================================
# DIRECT COMPARISON
# ==================================================

with tab3:
    st.header("Version 1 vs Version 2 on the same event")

    if variable_cycle:
        comparison_event = get_cycle_event(
            selected_cycle,
            event_type,
            braking_mode,
        )

        comparison_initial = comparison_event["start_speed"]
        comparison_final = comparison_event["end_speed"]
        comparison_duration = comparison_event["duration"]

    else:
        comparison_initial = v2_initial_speed
        comparison_final = v2_final_speed
        comparison_duration = v2_duration

    comparison_v1 = simulate_speed_event(
        comparison_initial,
        comparison_final,
        comparison_duration,
        mass,
        LD,
        diameter,
        eff,
        gate_mode="always_open",
        grade=grade,
    )

    comparison_best_gate, _ = find_optimal_gate_speed(
        comparison_initial,
        comparison_final,
        comparison_duration,
        mass,
        LD,
        diameter,
        eff,
        grade,
    )

    if comparison_best_gate is not None:
        comparison_v2 = simulate_speed_event(
            comparison_initial,
            comparison_final,
            comparison_duration,
            mass,
            LD,
            diameter,
            eff,
            gate_mode="smart",
            opening_speed=comparison_best_gate["opening_speed"],
            grade=grade,
        )

        st.write(
            f"Version 2 uses its scanned threshold of "
            f"**{comparison_best_gate['opening_speed']} km/h** for this comparison."
        )

        comparison_table = pd.DataFrame(
            {
                "Version 1 - Always Open": [
                    kj(comparison_v1["recovered_energy"]),
                    kj(comparison_v1["turbine_drag_energy"]),
                    kj(
                        comparison_v1["turbine_drag_energy"]
                        - comparison_v1["recovered_energy"]
                    ),
                    kj(comparison_v1["total_energy_spent"]),
                    comparison_v1["recovery_vs_total_spent_pct"],
                    comparison_v1["recovery_vs_turbine_penalty_pct"],
                ],
                "Version 2 - Smart Gates": [
                    kj(comparison_v2["recovered_energy"]),
                    kj(comparison_v2["turbine_drag_energy"]),
                    kj(
                        comparison_v2["turbine_drag_energy"]
                        - comparison_v2["recovered_energy"]
                    ),
                    kj(comparison_v2["total_energy_spent"]),
                    comparison_v2["recovery_vs_total_spent_pct"],
                    comparison_v2["recovery_vs_turbine_penalty_pct"],
                ],
            },
            index=[
                "Electrical energy generated (kJ)",
                "Turbine aerodynamic penalty (kJ)",
                "Net turbine energy cost (kJ)",
                "Total energy spent (kJ)",
                "Generated / total spent (%)",
                "Generated / turbine penalty (%)",
            ],
        )

        st.dataframe(
            comparison_table,
            use_container_width=True,
        )

        chart_df = comparison_table.loc[
            [
                "Electrical energy generated (kJ)",
                "Turbine aerodynamic penalty (kJ)",
                "Net turbine energy cost (kJ)",
            ]
        ]

        st.bar_chart(chart_df)


# ==================================================
# LIMITATIONS
# ==================================================

with tab4:
    st.header("Model limitations")

    st.markdown(
        """
- **Vehicle aerodynamic geometry is simplified.** The code uses a fixed 2.2 m² vehicle frontal area because frontal area cannot be inferred reliably from vehicle mass or turbine diameter. The current `Cd = 1 / (L/D)` relationship is retained only as a screening proxy; a true lift-to-drag ratio does not uniquely determine a road vehicle's drag coefficient.
- **Turbine aerodynamic penalty is a conservative proxy.** The model currently treats the free-stream kinetic power through the turbine swept area as the turbine aerodynamic penalty. It does not solve actuator-disk induction, thrust coefficient, duct blockage, blade aerodynamics, wake interaction, or installation losses.
- **Turbine efficiency is constant with speed and load.** Real turbines and generators have efficiency maps, cut-in torque/speed, bearing losses, electrical controller losses, and power limits. Because the present model uses a constant efficiency, generated energy / turbine penalty is essentially fixed whenever the gate is open.
- **Gate motion is instantaneous and free.** Gate opening time, actuator power, gate drag while moving, sealing losses, and control-system latency are ignored.
- **Driving events are synthetic screening events, not certification cycles.** Each event uses a linear speed-vs-time trace over the same 20 s duration. Distance is calculated from that trace. Real WLTP/EPA-style cycles contain many acceleration, cruise, deceleration, and idle segments.
- **Rolling resistance is omitted.** Tyre deformation, road texture, tyre pressure, bearing friction, and speed-dependent rolling resistance are not included.
- **Propulsion-system losses are omitted.** Traction motor, inverter, gearbox, battery discharge/charge efficiency, battery temperature, state of charge, and auxiliary electrical loads are not modeled.
- **Normal EV regenerative braking is omitted.** The braking analysis only studies electricity from the front turbine; it does not add electricity recovered through the traction motor.
- **Ambient wind is omitted.** Relative airflow is assumed to equal vehicle speed. Headwind, tailwind, crosswind, gusts, and traffic wakes are ignored.
- **Air properties are fixed.** Air density is held at 1.225 kg/m³; altitude, temperature, humidity, and weather are ignored.
- **Road gradient is constant over an event.** Changes in slope within the event are not modeled.
- **Vehicle attitude and downforce are omitted.** Pitch, ride height, suspension response, lift/downforce, cornering, and turbine-induced changes to the rest of the car's aerodynamics are ignored.
- **The model assumes one turbine and no flow coupling.** Multiple turbines, duct networks, recirculation, pressure recovery, and interference between the turbine and the vehicle body are not modeled.
        """
    )

