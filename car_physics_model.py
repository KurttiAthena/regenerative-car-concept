import math


AIR_DENSITY = 1.225



def get_efficiency(mode, user_value):

    if mode == "Realistic":

        turbine = 0.40
        generator = 0.90
        electronics = 0.90

        return turbine * generator * electronics


    else:

        return user_value / 100

def calculate_gravity_power(mass, speed_kmh, grade):

    V = speed_kmh / 3.6

    angle = math.atan(grade / 100)

    gravity_power = (
        mass *
        9.81 *
        V *
        math.sin(angle)
    )

    return -gravity_power

def find_positive_cases(
        mass,
        LD_ratio,
        turbine_diameter,
        efficiency,
        speed_min,
        speed_max, 
        grade=0
):

    positive_speeds = []

    for speed in range(speed_min, speed_max + 1):

        result = calculate_energy(
            mass,
            speed,
            LD_ratio,
            turbine_diameter,
            efficiency,
            True, 
            grade
        )

        if result["net_power"] > 0:
            positive_speeds.append(speed)


    return positive_speeds

def find_activation_speed(
        mass,
        LD_ratio,
        turbine_diameter,
        efficiency, 
        grade
):

    for speed in range(1,251):

        result = calculate_energy(
            mass,
            speed,
            LD_ratio,
            turbine_diameter,
            efficiency,
            True,
            grade
        )


        if result["net_power"] >= 0:

            return speed


    return None



def calculate_energy(
        mass,
        speed_kmh,
        LD_ratio,
        turbine_diameter,
        efficiency,
        turbine_active=True,
        grade=0
):


    V = speed_kmh / 3.6

    gravity_power = calculate_gravity_power(
        mass,
        speed_kmh,
        grade
    )
    
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
        gravity_power +
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

        "recovery_percentage": recovery_percentage,

        "gravity_power": gravity_power

    }
