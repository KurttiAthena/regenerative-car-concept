import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from car_physics_model import calculate_energy, automatic_efficiency



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



eff = automatic_efficiency()



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


    st.header(
        "Turbine exposed at all speeds"
    )


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
        eff
    )


    st.metric(
        "Recovered power",
        f"{result['recovered_power']:.0f} W"
    )


    st.metric(
        "Net balance",
        f"{result['net_power']:.0f} W"
    )



# ==================================================
# VERSION 2
# ==================================================

with tab2:


    st.header(
        "Turbine opens only after threshold speed"
    )


    opening_speed = st.slider(
        "Gate opening speed (km/h)",
        20,
        200,
        80
    )


    max_speed = st.slider(
        "Maximum vehicle speed",
        opening_speed,
        250,
        150
    )


    speeds = np.linspace(
        opening_speed,
        max_speed,
        100
    )


    recovered = []
    net = []


    for s in speeds:


        result = calculate_energy(
            mass,
            s,
            LD,
            diameter,
            eff
        )


        recovered.append(
            result["recovered_power"]
        )


        net.append(
            result["net_power"]
        )



    fig, ax = plt.subplots()


    ax.plot(
        speeds,
        recovered,
        label="Recovered power"
    )


    ax.plot(
        speeds,
        net,
        label="Net balance"
    )


    ax.axhline(
        0
    )


    ax.set_xlabel(
        "Speed (km/h)"
    )

    ax.set_ylabel(
        "Power (W)"
    )


    ax.legend()


    st.pyplot(fig)



    st.write(
        """
        The turbine remains closed below the gate speed.
        Above this speed, energy recovery increases approximately with V³.
        """
    )
