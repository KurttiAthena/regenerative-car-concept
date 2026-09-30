from car_physics_model import (
    calculate_energy,
    should_open_gate
)

CITY_CYCLE = [

    (0,40,100,8,"acceleration"),

    (40,50,300,20,"cruise"),

    (50,20,80,5,"braking")

]


HIGHWAY_CYCLE = [

    (50,100,1000,20,"acceleration"),

    (100,120,2000,40,"cruise"),

    (120,80,500,10,"braking")

]


MOTORWAY_CYCLE = [

    (100,130,1500,15,"acceleration"),

    (130,130,5000,120,"cruise"),

    (130,90,800,15,"braking")

]


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

def integrate_turbine_energy(
        initial_speed,
        final_speed,
        duration,
        turbine_diameter,
        efficiency,
        steps=100
):

    total_energy = 0

    dt = duration / steps


    for i in range(steps):

        speed = (
            initial_speed +
            (final_speed-initial_speed)
            *
            i/steps
        )


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


        recovered_power = (
            wind_power *
            efficiency
        )


        total_energy += (
            recovered_power *
            dt
        )


    return total_energy


def simulate_cycle(
        cycle,
        mass,
        LD,
        turbine_diameter,
        efficiency,
        gate_mode
):

    total_energy = 0


    for start_speed,end_speed,distance,time,condition in cycle:


        if condition == "braking":

            closed_result = calculate_energy(
                mass,
                start_speed,
                LD,
                turbine_diameter,
                efficiency,
                False
            )


            open_result = calculate_energy(
                mass,
                start_speed,
                LD,
                turbine_diameter,
                efficiency,
                True
            )


            if gate_mode == "always_open":

                turbine_open = True


            elif gate_mode == "smart":

                turbine_open = should_open_gate(
                    closed_result,
                    open_result
                )


            if turbine_open:

                recovered = integrate_turbine_energy(
                    start_speed,
                    end_speed,
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
