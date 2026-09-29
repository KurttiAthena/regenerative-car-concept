def get_speed_range(name):

    if name == "City":
        return 20, 50

    elif name == "Highway":
        return 50, 100

    elif name == "Motorway":
        return 100, 150

    else:
        return 0, 0

def calculate_regenerative_braking(
        mass,
        initial_speed,
        final_speed,
        duration,
        efficiency
):

    v_initial = initial_speed / 3.6
    v_final = final_speed / 3.6


    energy_lost = (
        0.5 *
        mass *
        (
            v_initial**2 -
            v_final**2
        )
    )


    recovered_energy = (
        energy_lost *
        efficiency
    )


    power = (
        recovered_energy /
        duration
    )


    return power


for step in cycle:

    start_speed = step[0]
    end_speed = step[1]
    duration = step[2]


    if end_speed < start_speed:

        regen_power = calculate_braking_power(
            mass,
            start_speed,
            end_speed,
            duration
        )

    else:

        regen_power = 0
