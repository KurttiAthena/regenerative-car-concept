from car_physics_model import (
    calculate_energy,
    should_open_gate,
    calculate_kinetic_energy_change,
    calculate_drag_energy,
    calculate_gravity_energy,
    calculate_turbine_drag_energy
)

CITY_CYCLE = [

    (0,40,100,8,"acceleration"),

    (40,50,300,20,"cruise")

]


HIGHWAY_CYCLE = [

    (50,100,1000,20,"acceleration"),

    (100,120,2000,40,"cruise")

]


MOTORWAY_CYCLE = [

    (100,160,1500,15,"acceleration"),

    (130,130,5000,120,"cruise"),

]

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

def calculate_event_recovery_ratio(
        recovered_energy,
        energy_available
):

    if energy_available <= 0:

        return 0


    return (
        recovered_energy /
        energy_available *
        100
    )

def simulate_cycle(
    cycle,
    mass,
    LD,
    turbine_diameter,
    efficiency,
    gate_mode,
    grade, 
    braking_mode
):

    total_recovered_energy = 0
    total_available_energy = 0

    acceleration_recovered = 0
    acceleration_available = 0

    braking_recovered = 0
    braking_available = 0


    for start_speed,end_speed,distance,time,condition in cycle:

        is_braking = False
        if braking_mode:

            start_speed, end_speed = end_speed, start_speed
            is_braking = True


        # ---------------------------------
        # ACCELERATION
        # ---------------------------------

        if condition == "acceleration" and not is_braking:


            energy_available = (
                calculate_kinetic_energy_change(
                    mass,
                    start_speed,
                    end_speed
                )
                +
                calculate_drag_energy(
                    mass,
                    LD,
                    (start_speed+end_speed)/2,
                    distance
                )
                +
                calculate_gravity_energy(
                    mass,
                    grade,
                    distance
                )
            )

            electric_energy = integrate_turbine_energy(
                start_speed,
                end_speed,
                time,
                turbine_diameter,
                efficiency
            )

            turbine_drag_energy = calculate_turbine_drag_energy(
                start_speed,
                end_speed,
                time,
                turbine_diameter
            )


            recovered_energy = (
                electric_energy -
                turbine_drag_energy
            )

            if is_braking:

                braking_recovered += recovered_energy

                braking_available += energy_available

            else:

                acceleration_recovered += recovered_energy

                acceleration_available += energy_available


        # ---------------------------------
        # CRUISE
        # ---------------------------------

        elif condition == "cruise":


            energy_available = (
                calculate_drag_energy(
                    mass,
                    LD,
                    end_speed,
                    distance
                )
                +
                calculate_gravity_energy(
                    mass,
                    grade,
                    distance
                )
            )


            electric_energy = integrate_turbine_energy(
                start_speed,
                end_speed,
                time,
                turbine_diameter,
                efficiency
            )

            turbine_drag_energy = calculate_turbine_drag_energy(
                start_speed,
                end_speed,
                time,
                turbine_diameter
            )


            recovered_energy = (
                electric_energy -
                turbine_drag_energy
            )

            if is_braking:

                braking_recovered += recovered_energy

                braking_available += energy_available

            else:

                acceleration_recovered += recovered_energy

                acceleration_available += energy_available


        # ---------------------------------
        # BRAKING
        # ---------------------------------

        elif condition == "acceleration" and is_braking::


            energy_available = (
                -calculate_kinetic_energy_change(
                    mass,
                    start_speed,
                    end_speed
                )
                +
                calculate_gravity_energy(
                    mass,
                    grade,
                    distance
                 )
            )


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

            turbine_open = False

            if gate_mode == "always_open":

                turbine_open = True


            elif gate_mode == "smart":

                turbine_open = should_open_gate(
                    closed_result,
                    open_result
                )


            if turbine_open:

                electric_energy = integrate_turbine_energy(
                    start_speed,
                    end_speed,
                    time,
                    turbine_diameter,
                    efficiency
                )

                turbine_drag_energy = calculate_turbine_drag_energy(
                    start_speed,
                    end_speed,
                    time,
                    turbine_diameter
                )


                recovered_energy = (
                    electric_energy -
                    turbine_drag_energy
                )

            else:

                recovered_energy = 0

            if is_braking:

                braking_recovered += recovered_energy

                braking_available += energy_available

            else:

                acceleration_recovered += recovered_energy

                acceleration_available += energy_available

        total_recovered_energy += recovered_energy

        total_available_energy += energy_available

    if total_available_energy > 0:

        recovery_percentage = (
            total_recovered_energy /
            total_available_energy *
            100
        )

    else:

        recovery_percentage = 0

    return {

        "mode":
            "Braking" if braking_mode else "Acceleration",

        "total_recovered_energy":
            total_recovered_energy,

        "total_available_energy":
            total_available_energy,

        "recovery_percentage":
            recovery_percentage,

        "acceleration":
        {
            "recovered":
                acceleration_recovered,

            "available":
                acceleration_available
        },

        "braking":
        {
            "recovered":
                braking_recovered,

            "available":
                braking_available
        }
    }
