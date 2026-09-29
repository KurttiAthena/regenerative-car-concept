def get_cycle(name):

    if name=="City":

        return [
            (0,20,10),
            (20,40,15),
            (40,0,8),
            (0,50,20)
        ]



    if name=="Highway":

        return [
            (0,90),
            (90,110),
            (110,100)
        ]



    if name=="Motorway":

        return [
            (0,120),
            (120,130),
            (130,120)
        ]



    if name=="Stationary wind":

        return [
            (0,10)
        ]


    if name=="Braking":

        return [
            (100,50),
            (50,0)
        ]

def calculate_braking_power(
        mass,
        initial_speed,
        final_speed,
        time,
        regen_efficiency=0.7
):

    v_initial = initial_speed / 3.6
    v_final = final_speed / 3.6


    kinetic_energy_lost = (
        0.5 *
        mass *
        (
            v_initial**2 -
            v_final**2
        )
    )


    recovered_energy = (
        kinetic_energy_lost *
        regen_efficiency
    )


    braking_power = (
        recovered_energy /
        time
    )


    return braking_power
