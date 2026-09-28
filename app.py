import streamlit as st
from car_physics_model import car_physics_model.py


# ------------------------
# PAGE CONFIG
# ------------------------

st.set_page_config(
    page_title="Regenerative Car Simulator",
    page_icon="🚗"
)


st.title("🚗 Regenerative Car Physics Model")

st.write(
"""
Simple 0D energy balance model for a turbine-assisted EV.
Compare:
- Version 1: turbine always open
- Version 2: turbine opens only at target speed
"""
)


# ------------------------
# INPUTS
# ------------------------

st.sidebar.header("Vehicle Parameters")


mass = st.sidebar.slider(
    "Vehicle mass (kg)",
    500,
    3000,
    2000
)


speed = st.sidebar.slider(
    "Vehicle speed (km/h)",
    0,
    250,
    100
)


LD = st.sidebar.slider(
    "Aerodynamic L/D ratio",
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



# Efficiency

st.sidebar.header("Efficiency")


mode = st.sidebar.radio(
    "Efficiency calculation",
    [
        "Automatic",
        "Manual"
    ]
)


if mode == "Manual":

    efficiency = st.sidebar.slider(
        "System efficiency (%)",
        1,
        100,
        40
    ) / 100


else:

    efficiency = 0.4



# ------------------------
# CALCULATIONS
# ------------------------

if st.button("Calculate"):


    st.subheader("Version 1 - Turbine always open")


    result1 = regenerative_car(
        mass,
        speed,
        LD,
        diameter,
        "manual",
        efficiency
    )


    col1,col2,col3 = st.columns(3)


    col1.metric(
        "Recovered power",
        f"{result1['recovered electricity W']} W"
    )

    col2.metric(
        "Drag penalty",
        f"{result1['turbine drag penalty W']} W"
    )

    col3.metric(
        "Net balance",
        f"{result1['net balance W']} W"
    )



    st.divider()



    st.subheader(
        "Version 2 - Smart opening turbine"
    )


    st.info(
        "For this first version the turbine opens exactly at the selected speed."
    )


    result2 = regenerative_car(
        mass,
        speed,
        LD,
        diameter,
        "manual",
        efficiency
    )


    col1,col2 = st.columns(2)


    col1.metric(
        "Energy recovered",
        f"{result2['% aerodynamic energy recovered']} %"
    )


    col2.metric(
        "Efficiency used",
        f"{result2['efficiency used']} %"
    )



    st.divider()


    st.subheader("Detailed Energy Balance")


    st.json(result1)
