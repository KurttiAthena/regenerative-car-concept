import math


AIR_DENSITY = 1.225



def automatic_efficiency():

    turbine = 0.40
    generator = 0.90
    electronics = 0.90

    return turbine * generator * electronics




def calculate_energy(
        mass,
        speed_kmh,
        LD_ratio,
        turbine_diameter,
        efficiency,
        turbine_active=True
):


    V = speed_kmh / 3.6


    # Vehicle aerodynamics

    frontal_area = 0.0005 * mass

    Cd = 1 / LD_ratio


    drag_force = (
        0.5 *
        AIR_DENSITY *
        Cd *
        frontal_area *
        V**2
    )


    vehicle_drag_power = drag_force * V



    # Turbine

    turbine_area = (
        math.pi *
        (turbine_diameter/2)**2
    )


    available_wind_power = (
        0.5 *
        AIR_DENSITY *
        turbine_area *
        V**3
    )


    if turbine_active:

        recovered_power = (
            available_wind_power *
            efficiency
        )


        turbine_drag_power = (
            available_wind_power
        )

    else:

        recovered_power = 0

        turbine_drag_power = 0



    net_power = (
        recovered_power -
        turbine_drag_power
    )


    total_power_effect = (
        vehicle_drag_power +
        turbine_drag_power -
        recovered_power
    )



    if vehicle_drag_power > 0:

        recovery_percentage = (
            recovered_power /
            vehicle_drag_power
            *
            100
        )

    else:
        recovery_percentage = 0



    return {

        "vehicle_drag_power": vehicle_drag_power,

        "turbine_drag_power": turbine_drag_power,

        "available_wind_power": available_wind_power,

        "recovered_power": recovered_power,

        "net_power": net_power,

        "total_power_effect": total_power_effect,

        "recovery_percentage": recovery_percentage

    }
