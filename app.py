import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from car_physics_model import calculate_energy, get_efficiency



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

    efficiency = 32

eff = get_efficiency()



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
        True
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
            True
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


        r=calculate_energy(
            mass,
            s,
            LD,
            diameter,
            eff,
            True
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
