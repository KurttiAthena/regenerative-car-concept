"""Illustrative presets, NOT standard physical lift-to-drag ratios.

Only L/D_proxy changes. Cd is its displayed reciprocal, not an independent
physical input. Mass, turbine diameter and the fixed 2.2 m² frontal area stay
unchanged. Generic values are deliberately conceptual selections, not claims
of manufacturer measurements. Airfoil/fuselage values are installed-body
placeholders on this common frontal-area basis, not wing-area coefficients.
"""
PRESETS = [
    # id, English name, Spanish name, conceptual Cd
    ("custom", "Custom / keep my value", "Personalizado / mantener mi valor", None),
    ("f1", "F1-style racing car (conceptual)", "Monoplaza estilo F1 (conceptual)", 0.90),
    ("bus", "Schoolbus / box-shaped van", "Autobús escolar / furgoneta rectangular", 0.65),
    ("truck", "Truck", "Camión", 0.60),
    ("van", "Streamlined van", "Furgoneta aerodinámica", 0.40),
    ("large_suv", "Large SUV / Land Rover-style", "SUV grande / estilo Land Rover", 0.38),
    ("suv", "Standard SUV", "SUV estándar", 0.35),
    ("microcar", "Microcar / city car", "Microcoche / coche urbano", 0.33),
    ("sedan", "Standard sedan", "Sedán estándar", 0.30),
    ("sports", "Road sports car / 2015 Porsche 911 reference", "Deportivo / referencia Porsche 911 de 2015", 0.29),
    ("coupe", "Streamlined coupe", "Cupé aerodinámico", 0.28),
    ("tesla", "Tesla Model 3-inspired sedan (illustrative)", "Sedán inspirado en Tesla Model 3 (ilustrativo)", 0.23),
    ("fuselage", "Airplane fuselage on wheels (conceptual)", "Fuselaje de avión con ruedas (conceptual)", 0.15),
    ("airfoil", "NACA 0012-inspired body on wheels (conceptual)", "Carrocería inspirada en NACA 0012 con ruedas (conceptual)", 0.10),
]
PRESET_MAP = {key: row for row in PRESETS for key in row[:3]}
SOURCES = [
    ("Range Rover Sport SVR (2015): Cd = 0.38 / Cx = 0,38",
     "https://media.jlr.com/range-rover/en-us/news/2014/08/2015-range-rover-sport-svr"),
    ("Chalmers thesis: Model 3 SR+ Cd = 0.23 (table 21) / Cx = 0,23 (tabla 21)",
     "https://odr.chalmers.se/bitstreams/376be6c2-2e1c-46a6-816e-b4e46d8b1dea/download"),
    ("Porsche: 2015 911 Carrera Cd = 0.29 / Cx = 0,29",
     "https://newsroom.porsche.com/en/christophorus/porsche-carrera-911s-technique-turbo-engine-11471.html"),
    ("NASA: Cd depends on reference area and flow conditions / Cx depende del área de referencia y del flujo",
     "https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-coefficient/"),
    ("Formula 1: downforce / drag efficiency is a different measure / carga aerodinámica y resistencia son otra medida",
     "https://www.formula1.com/en/latest/article/tech-tuesday-why-aerodynamic-efficiency-now-rules-at-silverstone.65XAovu8LiK7IEqysQ4Sx0"),
]
