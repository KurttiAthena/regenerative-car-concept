import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from car_physics_model import (
    calculate_energy,
    get_efficiency,
    find_activation_speed, 
    find_positive_cases,
    should_open_gate
)


from driving_cycles import (
    CITY_CYCLE,
    HIGHWAY_CYCLE,
    MOTORWAY_CYCLE,
    simulate_cycle
)



st.set_page_config(
    page_title="Regenerative Car Model",
    page_icon="🚗"
)


st.title("🚗 Regenerative Car Simulator")


# -------------------
# GLOBAL INPUTS
# -------------------

st.sidebar.header("Vehicle")


mass = st.sidebar.slider(
    "Mass (kg)",
    500,
    3000,
    2000
)


LD = st.sidebar.slider(
    "L/D ratio",
    2.0,
    15.0,
    8.0
)


diameter = st.sidebar.slider(
    "Turbine diameter (m)",
    0.1,
    2.0,
    0.5
)


eff_mode = st.sidebar.radio(
    "Efficiency model",
    [
        "Realistic",
        "Idealised slider"
    ]
)


if eff_mode=="Idealised slider":

    efficiency = st.sidebar.slider(
        "Energy transfer efficiency (%)",
        0,
        100,
        40
    )

else:

    efficiency = 0


eff = get_efficiency(
    eff_mode,
    efficiency
)

variable_cycle = st.sidebar.checkbox(
    "Enable variable driving cycle"
)

grade = 0

speed_min = 0
speed_max = 250

if variable_cycle:

    cycle_name = st.sidebar.selectbox(
        "Driving scenario",
        [
            "City",
            "Highway",
            "Motorway"
        ]
    )

    if cycle_name == "City":
        selected_cycle = CITY_CYCLE

    elif cycle_name == "Highway":
        selected_cycle = HIGHWAY_CYCLE

    elif cycle_name == "Motorway":
        selected_cycle = MOTORWAY_CYCLE

    grade = st.sidebar.slider(
        "Road gradient (%)",
        -20,
        20,
        0
    )

    braking = st.sidebar.slider(
        "Braking intensity (%)",
        0,
        100,
        0
    )

    cycle_energy = simulate_cycle(
        selected_cycle,
        mass,
        LD,
        diameter,
        eff
    )


# -------------------
# TABS
# -------------------

tab1, tab2 = st.tabs(
    [
        "Version 1 - Always Open",
        "Version 2 - Smart Gates"
    ]
)



# ==================================================
# VERSION 1
# ==================================================

with tab1:

    st.header("Version 1 - Turbine always open")


    speed = st.slider(
        "Vehicle speed",
        0,
        250,
        100,
        key="v1"
    )


    result = calculate_energy(
        mass,
        speed,
        LD,
        diameter,
        eff,
        True,
        grade
    )


    col1,col2,col3 = st.columns(3)


    col1.metric(
        "Recovered power",
        f"{result['recovered_power']:.0f} W"
    )


    col2.metric(
        "Turbine penalty",
        f"{result['turbine_drag_power']:.0f} W"
    )


    col3.metric(
        "Net effect",
        f"{result['net_power']:.0f} W"
    )


    st.divider()


    speeds = np.linspace(
        1,
        250,
        100
    )


    recovery=[]

    net=[]


    for s in speeds:

        r = calculate_energy(
            mass,
            s,
            LD,
            diameter,
            eff,
            True, 
            grade
        )

        recovery.append(
            r["recovered_power"]
        )

        net.append(
            r["net_power"]
        )


    fig,ax=plt.subplots()

    ax.plot(
        speeds,
        recovery,
        label="Recovered"
    )

    ax.plot(
        speeds,
        net,
        label="Net"
    )

    ax.axhline(0)

    ax.set_xlabel(
        "Speed km/h"
    )

    ax.set_ylabel(
        "Power W"
    )

    ax.legend()


    st.pyplot(fig)

    st.metric(
        "Energy recovered in cycle",
        f"{cycle_energy/1000:.2f} kJ"
    )



# ==================================================
# VERSION 2
# ==================================================

with tab2:


    st.header(
        "Version 2 - Smart gate turbine"
    )


    opening_speed = st.slider(
        "Gate opening speed (km/h)",
        20,
        200,
        80
    )


    max_speed = st.slider(
        "Maximum speed",
        opening_speed,
        250,
        150
    )


    speeds=np.linspace(
        opening_speed,
        max_speed,
        100
    )


    data=[]


    for s in speeds:


        test_result = calculate_energy(
            mass,
            s,
            LD,
            diameter,
            eff,
            True,
            grade
        )


        turbine_active = should_open_gate(
            test_result,
            grade < 0
        )


        r=calculate_energy(
            mass,
            s,
            LD,
            diameter,
            eff,
            turbine_active,
            grade
        )

        data.append(
            [
                s,
                r["recovered_power"],
                r["net_power"],
                r["recovery_percentage"]
            ]
        )



    df=pd.DataFrame(
        data,
        columns=[
            "Speed",
            "Recovered W",
            "Net W",
            "Recovery %"
        ]
    )



    st.subheader(
        "Energy recovery after gate opening"
    )


    st.line_chart(
        df.set_index("Speed")
        [
        [
        "Recovered W",
        "Net W"
        ]
        ]
    )


    st.subheader(
        "Recovery percentage"
    )


    st.line_chart(
        df.set_index("Speed")
        [
        "Recovery %"
        ]
    )



    st.subheader(
        "Numerical values"
    )


    st.dataframe(df)

    optimal_speed = find_activation_speed(
        mass,
        LD,
        diameter,
        eff, 
        grade
    )


    if optimal_speed:

        st.success(
             f"Turbine becomes energetically useful at approximately {optimal_speed} km/h"
        )

    else:

        st.warning(
            "Turbine never reaches positive energy balance"
        )

    positive = find_positive_cases(
        mass,
        LD,
        diameter,
        eff,
        speed_min,
        speed_max
    )

    if positive:

        st.success(
            f"Positive energy balance found between {min(positive)}-{max(positive)} km/h"
        )

    else:

        st.warning(
            "No positive energy balance in this speed range"
        )

    st.metric(
        "Energy recovered in cycle",
        f"{cycle_energy/1000:.2f} kJ"
    )
