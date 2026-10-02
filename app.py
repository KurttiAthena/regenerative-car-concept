import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from car_physics_model import (
    calculate_energy,
    get_efficiency,
    simulate_speed_event,
    find_optimal_gate_speed,
    calculate_solar_energy,
    calculate_regenerative_braking_energy,
    TURBINE_THRUST_COEFFICIENT,
    SOLAR_ROOF_AREA,
    SOLAR_IRRADIANCE,
    SOLAR_PANEL_EFFICIENCY,
    SOLAR_CHARGE_EFFICIENCY,
    REGEN_BRAKING_EFFICIENCY,
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
            "Simplified net event energy after recovery",
            f"{kj(result['net_event_energy_after_recovery']):.2f} kJ",
        )

    st.caption(
        f"Normalized event: {result['duration_s']:.0f} s, "
        f"{result['distance_m']:.0f} m travelled. "
        f"Turbine open for {result['open_time_s']:.1f} s."
    )


def render_result_guide():
    with st.expander("Why do some results change much more than others?"):
        st.markdown(
            f"""
- **Absolute turbine power changes strongly with speed and turbine diameter.** Both generated power and turbine-induced drag scale approximately with vehicle speed cubed, and with turbine swept area (diameter squared).
- **Generated / turbine penalty changes very little with speed.** With a fixed turbine efficiency and fixed actuator-disk thrust coefficient, both numerator and denominator scale with the same speed and area terms. Their ratio is therefore mostly fixed by the assumed turbine coefficients.
- **Mass mainly changes acceleration, hill and braking energy.** It does not directly change the kinetic power in the air crossing a fixed-size turbine.
- **L/D changes the baseline vehicle aerodynamic-drag estimate, not the turbine's own airflow power.**
- The current simplified actuator-disk model uses a turbine thrust coefficient of **{TURBINE_THRUST_COEFFICIENT:.3f}**.
            """
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

st.sidebar.divider()
additional_vehicle_efficiency = st.sidebar.checkbox(
    "Additional vehicle efficiency?"
)

if additional_vehicle_efficiency:
    solar_light_percentage = st.sidebar.slider(
        "Solar light available (%)",
        0,
        100,
        100,
        help=(
            "Scales the reference solar irradiance from 0% (no usable "
            "sunlight) to 100% (1000 W/m² peak/STC-style irradiance)."
        ),
    )
    st.sidebar.caption(
        "Adds roof solar to the comparison. Regenerative braking is added "
        "only when braking/deceleration is selected."
    )
else:
    solar_light_percentage = 0


# ==================================================
# TABS
# ==================================================

tab_labels = [
    "Version 1 - Always Open",
    "Version 2 - Smart Gates",
    "Direct Comparison",
]

if additional_vehicle_efficiency:
    tab_labels.append("Additional Vehicle Efficiency")

tab_labels.append("Limitations")
tabs = st.tabs(tab_labels)

tab1 = tabs[0]
tab2 = tabs[1]
tab3 = tabs[2]

if additional_vehicle_efficiency:
    additional_efficiency_tab = tabs[3]
    limitations_tab = tabs[4]
else:
    additional_efficiency_tab = None
    limitations_tab = tabs[3]


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
    render_result_guide()

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
        # Use the normal cycle definition to establish the available speed
        # range. Braking remains an external analysis mode.
        base_v2_event = get_cycle_event(
            selected_cycle,
            event_type,
            False,
        )

        base_start_speed = base_v2_event["start_speed"]
        base_end_speed = base_v2_event["end_speed"]
        v2_duration = base_v2_event["duration"]

        speed_low = int(min(base_start_speed, base_end_speed))
        speed_high = int(max(base_start_speed, base_end_speed))
        default_opening = int(round((speed_low + speed_high) / 2))

        opening_speed = st.slider(
            "Gate opening threshold (km/h)",
            speed_low,
            speed_high,
            default_opening,
            key="v2_cycle_opening",
        )

        if braking_mode:
            # Full-stop braking event. The smart gate remains open only while
            # speed is at or above the selected threshold.
            v2_initial_speed = speed_high
            v2_final_speed = 0
            v2_scan_initial_speed = speed_high
            v2_scan_final_speed = 0
        else:
            v2_initial_speed = base_start_speed
            v2_final_speed = base_end_speed
            v2_scan_initial_speed = base_start_speed
            v2_scan_final_speed = base_end_speed

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
            # Full-stop braking event. The turbine closes automatically once
            # vehicle speed falls below the selected gate threshold.
            v2_initial_speed = max_speed
            v2_final_speed = 0
            v2_scan_initial_speed = max_speed
            v2_scan_final_speed = 0
        else:
            v2_initial_speed = 0
            v2_final_speed = max_speed
            v2_scan_initial_speed = 0
            v2_scan_final_speed = max_speed

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
    render_result_guide()

    st.divider()
    st.subheader("Gate-opening threshold scan")

    best_gate, gate_scan = find_optimal_gate_speed(
        v2_scan_initial_speed,
        v2_scan_final_speed,
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

    # The comparison uses the same complete underlying Version 2 speed event
    # for both concepts so the always-open and gated cases are directly
    # comparable. Version 2 braking remains a full-stop event to 0 km/h.
    comparison_scan_initial = v2_scan_initial_speed
    comparison_scan_final = v2_scan_final_speed
    comparison_duration = v2_duration

    comparison_best_gate, _ = find_optimal_gate_speed(
        comparison_scan_initial,
        comparison_scan_final,
        comparison_duration,
        mass,
        LD,
        diameter,
        eff,
        grade,
    )

    if comparison_best_gate is not None:
        comparison_initial = comparison_scan_initial
        comparison_final = comparison_scan_final

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
# OPTIONAL ADDITIONAL VEHICLE EFFICIENCY
# ==================================================

if additional_vehicle_efficiency:
    with additional_efficiency_tab:
        st.header(
            "Additional vehicle efficiency: solar + regenerative braking"
        )

        st.info(
            "This uses the same Version 1 vs Version 2 event as the Direct "
            "Comparison tab, then adds roof-solar electricity at the selected "
            "sunlight level. Traction-motor regenerative braking is included "
            "only when 'Analyse braking / deceleration' is selected."
        )

        if comparison_best_gate is not None:
            solar = calculate_solar_energy(
                comparison_duration,
                solar_light_percentage,
            )

            def enhanced_summary(result):
                if braking_mode:
                    regen = calculate_regenerative_braking_energy(
                        result["braking_energy_to_dissipate"]
                    )
                    regen_energy = regen["regen_recovered_energy"]
                else:
                    regen_energy = 0.0

                turbine_generated = result["recovered_energy"]
                turbine_penalty = result["turbine_drag_energy"]
                solar_energy = solar["solar_energy"]
                energy_spent = result["total_energy_spent"]

                total_electrical_input = (
                    turbine_generated
                    + regen_energy
                    + solar_energy
                )

                return {
                    "turbine_generated": turbine_generated,
                    "turbine_penalty": turbine_penalty,
                    "regen_energy": regen_energy,
                    "solar_energy": solar_energy,
                    "total_electrical_input": total_electrical_input,
                    "energy_spent": energy_spent,
                    "net_after_all_inputs": (
                        energy_spent - total_electrical_input
                    ),
                }

            enhanced_v1 = enhanced_summary(comparison_v1)
            enhanced_v2 = enhanced_summary(comparison_v2)

            st.caption(
                f"Solar input: {solar_light_percentage}% of the "
                f"{SOLAR_IRRADIANCE:.0f} W/m² reference irradiance "
                f"({solar['available_irradiance']:.0f} W/m² available). "
                f"With {SOLAR_ROOF_AREA:.1f} m² of roof PV at "
                f"{SOLAR_PANEL_EFFICIENCY*100:.0f}% panel efficiency and "
                f"{SOLAR_CHARGE_EFFICIENCY*100:.0f}% charging efficiency, "
                f"this gives {solar['solar_power']:.0f} W during the event."
            )

            if braking_mode:
                st.caption(
                    f"Regenerative braking is active for this braking event "
                    f"using the fixed {REGEN_BRAKING_EFFICIENCY*100:.1f}% "
                    "wheel-to-battery screening efficiency."
                )
            else:
                st.caption(
                    "Regenerative braking contribution is 0 kJ because this "
                    "is not currently a braking/deceleration case."
                )

            enhanced_table = pd.DataFrame(
                {
                    "Version 1 - Always Open": [
                        kj(enhanced_v1["turbine_generated"]),
                        kj(enhanced_v1["turbine_penalty"]),
                        kj(enhanced_v1["regen_energy"]),
                        kj(enhanced_v1["solar_energy"]),
                        kj(enhanced_v1["total_electrical_input"]),
                        kj(enhanced_v1["energy_spent"]),
                        kj(enhanced_v1["net_after_all_inputs"]),
                    ],
                    "Version 2 - Smart Gates": [
                        kj(enhanced_v2["turbine_generated"]),
                        kj(enhanced_v2["turbine_penalty"]),
                        kj(enhanced_v2["regen_energy"]),
                        kj(enhanced_v2["solar_energy"]),
                        kj(enhanced_v2["total_electrical_input"]),
                        kj(enhanced_v2["energy_spent"]),
                        kj(enhanced_v2["net_after_all_inputs"]),
                    ],
                },
                index=[
                    "Turbine electricity (kJ)",
                    "Turbine aerodynamic penalty (kJ)",
                    "Traction-motor regenerative braking (kJ)",
                    "Roof-solar external input (kJ)",
                    "Total electrical energy into battery (kJ)",
                    "Simplified propulsion energy spent (kJ)",
                    "Simplified net event energy after all inputs (kJ)",
                ],
            )

            st.dataframe(
                enhanced_table,
                use_container_width=True,
            )

            recovery_sources = pd.DataFrame(
                {
                    "Version 1 - Always Open": [
                        kj(enhanced_v1["turbine_generated"]),
                        kj(enhanced_v1["regen_energy"]),
                        kj(enhanced_v1["solar_energy"]),
                    ],
                    "Version 2 - Smart Gates": [
                        kj(enhanced_v2["turbine_generated"]),
                        kj(enhanced_v2["regen_energy"]),
                        kj(enhanced_v2["solar_energy"]),
                    ],
                },
                index=[
                    "Front turbine",
                    "Regenerative braking",
                    "Solar",
                ],
            )

            st.subheader("Electrical energy contributions")
            st.bar_chart(recovery_sources)

            net_difference = (
                enhanced_v2["net_after_all_inputs"]
                - enhanced_v1["net_after_all_inputs"]
            )

            st.metric(
                "V2 minus V1 simplified net event energy",
                f"{kj(net_difference):+.2f} kJ",
                help=(
                    "Negative means Version 2 requires less simplified net "
                    "event energy than Version 1 in this comparison; positive "
                    "means more."
                ),
            )


# ==================================================
# LIMITATIONS
# ==================================================

with limitations_tab:
    st.header("Model limitations")

    st.markdown(
        """
- **Vehicle aerodynamic geometry is simplified.** The code uses a fixed 2.2 m² vehicle frontal area because frontal area cannot be inferred reliably from vehicle mass or turbine diameter. The current `Cd = 1 / (L/D)` relationship is retained only as a screening proxy; a true lift-to-drag ratio does not uniquely determine a road vehicle's drag coefficient.
- **Turbine aerodynamics still use a simplified actuator-disk model.** The code now links a fixed rotor power coefficient to a thrust coefficient using classical 1-D momentum theory, then uses turbine thrust × vehicle speed as the aerodynamic power penalty. It still does not model duct blockage, blade geometry, detailed wake interaction, installation losses, or a speed-dependent Cp/Ct map.
- **Turbine efficiency is constant with speed and load.** Real turbines and generators have efficiency maps, cut-in torque/speed, bearing losses, electrical controller losses, and power limits. Because the present model uses a constant efficiency, generated energy / turbine penalty is essentially fixed whenever the gate is open.
- **Gate motion is instantaneous and free.** Gate opening time, actuator power, gate drag while moving, sealing losses, and control-system latency are ignored.
- **Driving events are synthetic screening events, not certification cycles.** Each event uses a linear speed-vs-time trace over the same 20 s duration. Distance is calculated from that trace. Real WLTP/EPA-style cycles contain many acceleration, cruise, deceleration, and idle segments.
- **Rolling resistance is omitted.** Tyre deformation, road texture, tyre pressure, bearing friction, and speed-dependent rolling resistance are not included.
- **Propulsion-system losses are omitted.** Traction motor, inverter, gearbox, battery discharge/charge efficiency, battery temperature, state of charge, and auxiliary electrical loads are not modeled.
- **Traction-motor regenerative braking is simplified and only added in the optional Additional Vehicle Efficiency tab when braking/deceleration is selected.** It uses one fixed wheel-to-battery efficiency and has no motor/generator power limit, battery state-of-charge limit, tyre-adhesion limit, brake blending, low-speed cutoff, or temperature dependence.
- **Solar remains a simplified screening model.** The optional Additional Vehicle Efficiency tab assumes a fixed 2.0 m² roof area and fixed panel/charging efficiencies. The user-selected 0–100% solar-light value linearly scales a 1000 W/m² reference irradiance; shading, roof curvature, detailed sun angle, panel temperature, parking orientation and daily/seasonal yield are not modeled.
- **Ambient wind is omitted.** Relative airflow is assumed to equal vehicle speed. Headwind, tailwind, crosswind, gusts, and traffic wakes are ignored.
- **Air properties are fixed.** Air density is held at 1.225 kg/m³; altitude, temperature, humidity, and weather are ignored.
- **Road gradient is constant over an event.** Changes in slope within the event are not modeled.
- **Vehicle attitude and downforce are omitted.** Pitch, ride height, suspension response, lift/downforce, cornering, and turbine-induced changes to the rest of the car's aerodynamics are ignored.
- **The model assumes one turbine and no flow coupling.** Multiple turbines, duct networks, recirculation, pressure recovery, and interference between the turbine and the vehicle body are not modeled.
        """
    )
