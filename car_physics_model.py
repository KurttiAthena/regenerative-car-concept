import math


# -----------------------------
# CONSTANTS
# -----------------------------

AIR_DENSITY = 1.225  # kg/m3


# -----------------------------
# EFFICIENCY CALCULATION
# -----------------------------

def automatic_efficiency():

    # Approximate values from realistic systems:
    # turbine Cp ~ 0.35-0.45
    # generator efficiency ~0.9
    # electrical losses ~0.9

    turbine = 0.40
    generator = 0.90
    electronics = 0.90

    return turbine * generator * electronics



# -----------------------------
# MAIN MODEL
# -----------------------------

def regenerative_car(
        mass,
        speed_kmh,
        LD_ratio,
        turbine_diameter,
        efficiency_mode="automatic",
        manual_efficiency=0.4
):

    # velocity
    V = speed_kmh / 3.6


    # frontal area approximation
    frontal_area = 0.0005 * mass


    # approximate drag coefficient
    Cd = 1 / LD_ratio


    # vehicle aerodynamic drag

    drag_force = (
        0.5 *
        AIR_DENSITY *
        Cd *
        frontal_area *
        V**2
    )


    drag_power = drag_force * V



    # turbine area

    turbine_area = math.pi * (turbine_diameter/2)**2


    # wind kinetic power

    wind_power = (
        0.5 *
        AIR_DENSITY *
        turbine_area *
        V**3
    )


    # efficiency selection

    if efficiency_mode == "automatic":
        efficiency = automatic_efficiency()

    else:
        efficiency = manual_efficiency



    recovered_power = wind_power * efficiency



    # turbine aerodynamic penalty
    # simplified equal to captured energy extraction

    turbine_drag_power = wind_power


    net_power = recovered_power - turbine_drag_power



    recovery_percentage = (
        recovered_power /
        drag_power *
        100
    )



    return {

        "speed km/h": speed_kmh,

        "vehicle drag power W":
            round(drag_power,2),

        "available wind power W":
            round(wind_power,2),

        "recovered electricity W":
            round(recovered_power,2),

        "turbine drag penalty W":
            round(turbine_drag_power,2),

        "net balance W":
            round(net_power,2),

        "% aerodynamic energy recovered":
            round(recovery_percentage,2),

        "efficiency used":
            round(efficiency*100,1)

    }



# -----------------------------
# USER INPUTS
# -----------------------------

print("\n=== Regenerative Car Concept Model ===\n")


mass = float(input("Vehicle mass (kg): "))
speed = float(input("Vehicle speed (km/h): "))
LD = float(input("Vehicle L/D ratio: "))
diameter = float(input("Turbine diameter (m): "))


mode = input(
    "Efficiency mode (automatic/manual): "
)


if mode == "manual":

    eff = float(
        input("Efficiency %: ")
    ) / 100

else:
    eff = 0



# Version 1
print("\n--- VERSION 1 : TURBINE ALWAYS OPEN ---")

result1 = regenerative_car(
    mass,
    speed,
    LD,
    diameter,
    mode,
    eff
)

for k,v in result1.items():
    print(k,":",v)



# Version 2

print("\n--- VERSION 2 : TURBINE OPENS AT THIS SPEED ---")

result2 = regenerative_car(
    mass,
    speed,
    LD,
    diameter,
    mode,
    eff
)


for k,v in result2.items():
    print(k,":",v)


