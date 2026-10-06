# Regenerative Car Concept

A simplified screening tool for investigating whether a vehicle-mounted airflow turbine could recover a meaningful amount of electrical energy relative to the aerodynamic penalty it introduces, evaluating whether this can act as an energy-recovery system.

The project originated from a client concept and is still a work in progress. It does not constitute as a validated vehicle simulation. 

The project compares two configurations:

1. **Version 1 — Always-open turbine**  
   The turbine remains exposed to the airflow throughout the entire driving event.

2. **Version 2 — Gated turbine**  
   The turbine is exposed only above a selected vehicle-speed threshold. The model scans possible opening thresholds and identifies the one that gives the best recovery metric for the simulated event.

---

## Why this project exists

A turbine placed in the airflow around a moving vehicle can generate electricity, but extracting that energy also produces aerodynamic resistance.

The important question is therefore not simply:

> How much electricity can the turbine generate?

but rather:

> How much electricity can it generate relative to the additional energy required to move the vehicle?

This tool was built to explore that trade-off.

It evaluates electrical generation alongside:

- turbine-induced aerodynamic penalty
- baseline vehicle aerodynamic drag
- vehicle acceleration or deceleration
- road gradient
- turbine size and efficiency
- vehicle mass
- different simplified driving scenarios

The model then allows an always-exposed turbine (_Ver 1_) to be compared against a turbine isolated by controllable gates (_Ver 2_).

---

## Current model

The application calculates quantities including:

- electrical energy generated
- turbine aerodynamic penalty
- net turbine energy cost
- total simplified event energy
- generated energy / total energy spent
- generated energy / turbine aerodynamic penalty

It also plots instantaneous turbine generation, turbine aerodynamic penalty and baseline vehicle aerodynamic drag against vehicle speed.

For _Ver 2_ of the car concept, the current optimization criterion is:

- **Acceleration / cruise:** maximize recovered electrical energy relative to total energy spent.
- **Deceleration / braking:** maximize recovered turbine energy relative to kinetic energy lost.

If multiple thresholds produce the same recovery ratio, the threshold recovering the greater absolute amount of electrical energy is preferred.

This makes it possible to investigate whether restricting turbine operation to part of a journey improves the overall result compared with leaving the turbine permanently exposed.

The present turbine model assumes constant aerodynamic and electrical efficiencies. The turbine is represented using a simplified one-dimensional actuator-disk model.

---

## Driving scenarios

The application currently contains four simplified synthetic scenarios:

- Dirt Road
- City
- Highway
- Motorway

Each scenario contains separate acceleration and cruise events. The events are normalized to a 20-second duration, with travelled distance calculated from the resulting speed trace.

Braking/deceleration can also be analysed separately.

These are intentionally simple screening cases and are not intended to reproduce WLTP, EPA or other certification drive cycles.

---

## Optional additional energy recovery

The application also includes simplified models for two conventional vehicle energy sources (regenerative braking and solar power provided through panels on the roof). Their inclusion was specifically requested by the client. 

### Regenerative braking

During a braking event, some of the wheel-side energy that would otherwise need to be dissipated can be recovered through the traction motor.

A fixed motor-generator, inverter and battery charging efficiency is currently assumed.

### Solar roof

A simple roof-mounted photovoltaic model can also be enabled. The percentage of solar light available can be controlled as a user input.

These features are intended mainly to provide context for the magnitude of turbine recovery relative to more conventional energy-recovery approaches.

---

## Project structure

```text
regenerative-car-concept/
│
├── app.py
│   Streamlit interface, visualisation and comparison logic
│
├── car_physics_model.py
│   Vehicle, turbine and energy calculations
│
├── driving_cycles.py
│   Simplified normalized driving scenarios
│
└── requirements.txt
    Python dependencies
```

---

## Main assumptions and limitations

Some important simplifications are:

- fixed vehicle frontal area
- simplified relationship between L/D and vehicle drag coefficient
- one-dimensional actuator-disk turbine model
- constant turbine efficiency and aerodynamic coefficients
- no turbine \(C_p/C_t\) map versus operating point
- no detailed blade or duct geometry
- no CFD interaction between the turbine and vehicle body
- instantaneous, lossless gate operation
- no gate actuator energy consumption
- synthetic linear speed profiles
- no rolling resistance
- no complete electric powertrain efficiency model
- no battery state-of-charge or thermal model
- no motor/generator power limits
- fixed air density
- no ambient wind
- no detailed tyre or road model
- no vehicle pitch, suspension or downforce effects
- no interaction between multiple turbines

These are outlined in the **Limitations** tab of in the application.

---

## Q&A

The current tool is most useful for questions such as:

- How does turbine diameter affect recoverable energy?
- How large is turbine generation compared with the aerodynamic penalty it creates?
- How does vehicle speed affect the absolute magnitude of both quantities?
- Does gating the turbine change the result over a prescribed driving event?
- How sensitive is the concept to turbine efficiency?
- How does turbine recovery compare in magnitude with regenerative braking or roof solar?
- Which assumptions need higher-fidelity modelling before the concept can be evaluated properly?

---

## Disclaimer

This repository is an exploratory engineering model.

It does not demonstrate that a vehicle-mounted turbine can provide a net energy benefit, nor should its results be interpreted as validation of the underlying vehicle concept.

Any conclusions about real-world feasibility would require substantially higher-fidelity aerodynamic, mechanical, electrical and vehicle-level modelling, followed by experimental validation.
