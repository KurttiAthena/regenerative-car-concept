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


from car_physics_model import calculate_energy


def simulate_cycle(
        cycle,
        mass,
        LD,
        turbine_diameter,
        efficiency
):

    total_energy = 0


    for start_speed,end_speed,time in cycle:


        if end_speed < start_speed:


            recovered = calculate_turbine_braking(
                start_speed,
                time,
                turbine_diameter,
                efficiency
            )


            total_energy += recovered


        else:


            result = calculate_energy(
                mass,
                end_speed,
                LD,
                turbine_diameter,
                efficiency,
                True
            )


            total_energy += (
                result["net_power"] *
                time
            )


    return total_energy
