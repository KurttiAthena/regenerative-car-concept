def get_speed_range(name):

    if name == "City":
        return 20, 50

    elif name == "Highway":
        return 50, 100

    elif name == "Motorway":
        return 100, 150

    else:
        return 0, 0

def calculate_turbine_braking(
        speed,
        duration,
        turbine_diameter,
        efficiency
):

    V = speed / 3.6


    turbine_area = (
        3.14159 *
        (turbine_diameter/2)**2
    )


    wind_power = (
        0.5 *
        1.225 *
        turbine_area *
        V**3
    )


    recovered_energy = (
        wind_power *
        efficiency *
        duration
    )


    return recovered_energy

