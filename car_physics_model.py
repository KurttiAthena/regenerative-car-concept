import math


AIR_DENSITY = 1.225


def automatic_efficiency():

    turbine_efficiency = 0.40
    generator = 0.90
    electronics = 0.90

    return turbine_efficiency * generator * electronics



def calculate_energy(
        mass,
        speed_kmh,
        LD_ratio,
        turbine_diameter,
        efficiency
):

    V = speed_kmh / 3.6


    frontal_area = 0.0005 * mass

    Cd = 1 / LD_ratio


    drag_force = (
        0.5 *
        AIR_DENSITY *
        Cd *
        frontal_area *
        V**2
    )


    drag_power = drag_force * V



    turbine_area = math.pi*(turbine_diameter/2)**2


    wind_power = (
        0.5 *
        AIR_DENSITY *
        turbine_area *
        V**3
    )


    recovered_power = (
        wind_power *
        efficiency
    )


    net_power = (
        recovered_power -
        wind_power
    )


    return {

        "drag_power": drag_power,

        "wind_power": wind_power,

        "recovered_power": recovered_power,

        "net_power": net_power,

        "recovery_percentage":
            recovered_power / drag_power * 100

    }
