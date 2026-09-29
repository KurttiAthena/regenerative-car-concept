def get_cycle(name):


    if name=="City":

        return [
            (0,20),
            (20,40),
            (40,0),
            (0,50)
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
