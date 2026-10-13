import math
import numpy as np


AIR_DENSITY = 1.225
GRAVITY = 9.81

# Screening assumption used because the UI does not ask the user for vehicle
# frontal area.  Do not derive frontal area from vehicle mass or turbine size:
# neither quantity determines the vehicle's projected frontal area.
REFERENCE_FRONTAL_AREA = 2.2  # m^2

# Simplified actuator-disk turbine model.  The rotor is assumed to operate at
# an aerodynamic power coefficient Cp = 0.40 in the realistic case.  Cp and Ct
# are related through classical 1-D actuator-disk momentum theory.
TURBINE_AERODYNAMIC_CP = 0.40
BETZ_LIMIT = 16.0 / 27.0

# Enhanced-recovery screening assumptions.  These are deliberately constants,
# not extra user inputs, so the application stays a simple concept screener.
SOLAR_ROOF_AREA = 2.0  # m^2 of roof-mounted PV
SOLAR_IRRADIANCE = 1000.0  # W/m^2, peak/STC-style irradiance
SOLAR_PANEL_EFFICIENCY = 0.22
SOLAR_CHARGE_EFFICIENCY = 0.95

REGEN_MOTOR_GENERATOR_EFFICIENCY = 0.90
REGEN_INVERTER_EFFICIENCY = 0.95
REGEN_BATTERY_CHARGE_EFFICIENCY = 0.95
REGEN_BRAKING_EFFICIENCY = (
    REGEN_MOTOR_GENERATOR_EFFICIENCY
    * REGEN_INVERTER_EFFICIENCY
    * REGEN_BATTERY_CHARGE_EFFICIENCY
)


def _axial_induction_from_cp(cp):
    """Return the low-induction actuator-disk solution for a given Cp."""

    cp = max(0.0, min(cp, BETZ_LIMIT))

    if cp == 0.0:
        return 0.0

    low = 0.0
    high = 1.0 / 3.0

    for _ in range(80):
        a = 0.5 * (low + high)
        cp_here = 4.0 * a * (1.0 - a) ** 2

        if cp_here < cp:
            low = a
        else:
            high = a

    return 0.5 * (low + high)


TURBINE_AXIAL_INDUCTION = _axial_induction_from_cp(
    TURBINE_AERODYNAMIC_CP
)
TURBINE_THRUST_COEFFICIENT = (
    4.0
    * TURBINE_AXIAL_INDUCTION
    * (1.0 - TURBINE_AXIAL_INDUCTION)
)


def get_efficiency(mode, user_value):
    """Return overall wind-to-electric efficiency as a fraction."""

    if mode == "Realistic":
        turbine = 0.40
        generator = 0.90
        electronics = 0.90
        return turbine * generator * electronics

    return user_value / 100.0


def calculate_gravity_power(mass, speed_kmh, grade):
    """
    Road-grade power at the wheels.

    Positive = extra propulsion power required uphill.
    Negative = gravity supplies power downhill.
    """

    V = speed_kmh / 3.6
    angle = math.atan(grade / 100.0)

    return mass * GRAVITY * V * math.sin(angle)


def calculate_kinetic_energy_change(mass, initial_speed, final_speed):
    """Positive when the vehicle accelerates, negative when it decelerates."""

    vi = initial_speed / 3.6
    vf = final_speed / 3.6

    return 0.5 * mass * (vf**2 - vi**2)


def calculate_vehicle_drag_power(speed_kmh, LD_ratio):
    """
    Simplified vehicle aerodynamic power.

    IMPORTANT: Cd = 1 / L/D is only a screening proxy. A true vehicle L/D ratio
    is not sufficient to determine Cd. This approximation is kept so the model
    does not require a new user input.
    """

    V = speed_kmh / 3.6
    Cd_proxy = 1.0 / LD_ratio

    drag_force = (
        0.5
        * AIR_DENSITY
        * Cd_proxy
        * REFERENCE_FRONTAL_AREA
        * V**2
    )

    return drag_force * V


def calculate_drag_energy(mass, LD_ratio, speed, distance):
    """Compatibility helper for a constant-speed segment."""

    del mass  # Vehicle mass does not determine aerodynamic frontal area.

    V = speed / 3.6
    Cd_proxy = 1.0 / LD_ratio

    drag_force = (
        0.5
        * AIR_DENSITY
        * Cd_proxy
        * REFERENCE_FRONTAL_AREA
        * V**2
    )

    return drag_force * distance


def calculate_turbine_drag_energy(
    initial_speed,
    final_speed,
    duration,
    turbine_diameter,
    steps=200,
):
    """
    Integrate the fixed actuator-disk thrust × vehicle-speed penalty.

    The free-stream kinetic flux is multiplied by Ct, consistent with
    calculate_energy and simulate_speed_event.
    """

    total_energy = 0.0
    dt = duration / steps
    turbine_area = math.pi * (turbine_diameter / 2.0) ** 2

    for i in range(steps):
        fraction = (i + 0.5) / steps
        speed = initial_speed + (final_speed - initial_speed) * fraction
        V = speed / 3.6

        drag_power = (
            0.5
            * AIR_DENSITY
            * turbine_area
            * V**3
            * TURBINE_THRUST_COEFFICIENT
        )
        total_energy += drag_power * dt

    return total_energy


def calculate_gravity_energy(mass, grade, distance):
    """Positive uphill, negative downhill."""

    angle = math.atan(grade / 100.0)
    return mass * GRAVITY * math.sin(angle) * distance


def calculate_energy(
    mass,
    speed_kmh,
    LD_ratio,
    turbine_diameter,
    efficiency,
    turbine_active=True,
    grade=0,
):
    """
    Instantaneous power balance at one vehicle speed.

    Generation and turbine aerodynamic penalty are deliberately kept separate.
    No turbine penalty is subtracted from `recovered_power`.
    """

    V = speed_kmh / 3.6

    vehicle_drag_power = calculate_vehicle_drag_power(
        speed_kmh,
        LD_ratio,
    )

    gravity_power = calculate_gravity_power(
        mass,
        speed_kmh,
        grade,
    )

    turbine_area = math.pi * (turbine_diameter / 2.0) ** 2

    available_wind_power = (
        0.5
        * AIR_DENSITY
        * turbine_area
        * V**3
    )

    if turbine_active:
        # `efficiency` is the overall free-stream-wind-to-electric coefficient.
        # In realistic mode it is 0.40 * 0.90 * 0.90 = 0.324.
        recovered_power = available_wind_power * efficiency

        # Turbine-induced vehicle drag is represented by actuator-disk thrust,
        # not by assigning the entire free-stream kinetic flux as a penalty.
        turbine_drag_power = (
            available_wind_power
            * TURBINE_THRUST_COEFFICIENT
        )
    else:
        recovered_power = 0.0
        turbine_drag_power = 0.0

    # Positive means the turbine adds a net load to the vehicle.
    turbine_net_cost_power = turbine_drag_power - recovered_power

    # Mechanical power that the propulsion system would have to supply before
    # crediting the generated electricity. A sufficiently steep downhill can
    # make this zero.
    total_power_spent = max(
        vehicle_drag_power + gravity_power + turbine_drag_power,
        0.0,
    )

    # Signed battery-side screening balance. Negative means that, under the
    # simplified model, the event could charge rather than consume battery.
    net_event_power_after_recovery = total_power_spent - recovered_power

    recovery_vs_total_spent_pct = (
        recovered_power / total_power_spent * 100.0
        if total_power_spent > 0
        else 0.0
    )

    recovery_vs_turbine_penalty_pct = (
        recovered_power / turbine_drag_power * 100.0
        if turbine_drag_power > 0
        else 0.0
    )

    return {
        "vehicle_drag_power": vehicle_drag_power,
        "turbine_drag_power": turbine_drag_power,
        "available_wind_power": available_wind_power,
        "recovered_power": recovered_power,
        "gravity_power": gravity_power,
        "turbine_net_cost_power": turbine_net_cost_power,
        "total_power_spent": total_power_spent,
        "net_event_power_after_recovery": net_event_power_after_recovery,

        # Compatibility alias. This is NOT a complete battery-consumption model;
        # it mixes simplified wheel-side demand with generated electrical power.
        "net_battery_power": net_event_power_after_recovery,
        "recovery_vs_total_spent_pct": recovery_vs_total_spent_pct,
        "recovery_vs_turbine_penalty_pct": recovery_vs_turbine_penalty_pct,

        # Compatibility aliases for code that still expects the old keys.
        "net_power": recovered_power - turbine_drag_power,
        "total_power_effect": net_event_power_after_recovery,
        "recovery_percentage": recovery_vs_total_spent_pct,
        "turbine_net_effect": recovered_power - turbine_drag_power,
    }


def calculate_solar_energy(duration, sunlight_percentage=100.0):
    """
    Roof-PV electrical energy delivered toward the battery.

    `sunlight_percentage` scales the reference 1000 W/m² irradiance from
    0% (no usable sunlight) to 100% (peak/STC-style irradiance).
    """

    sunlight_fraction = max(
        0.0,
        min(float(sunlight_percentage), 100.0),
    ) / 100.0

    available_irradiance = (
        SOLAR_IRRADIANCE * sunlight_fraction
    )

    solar_power = (
        available_irradiance
        * SOLAR_ROOF_AREA
        * SOLAR_PANEL_EFFICIENCY
        * SOLAR_CHARGE_EFFICIENCY
    )

    return {
        "sunlight_percentage": sunlight_fraction * 100.0,
        "available_irradiance": available_irradiance,
        "solar_power": solar_power,
        "solar_energy": solar_power * duration,
    }


def calculate_regenerative_braking_energy(braking_energy_to_dissipate):
    """
    Simplified traction-motor regenerative braking.

    `braking_energy_to_dissipate` is wheel-side braking energy remaining after
    aerodynamic, grade and turbine-drag effects have already been accounted for.
    """

    available = max(braking_energy_to_dissipate, 0.0)

    return {
        "regen_available_energy": available,
        "regen_recovered_energy": (
            available * REGEN_BRAKING_EFFICIENCY
        ),
        "regen_efficiency": REGEN_BRAKING_EFFICIENCY,
    }


def should_open_gate(speed_kmh, opening_speed_kmh):
    """The physical gate state: open at or above the chosen threshold."""

    return speed_kmh >= opening_speed_kmh


def event_duration_for_distance(initial_speed, final_speed, distance_m):
    """Stretch one linear speed-time event; do not repeat kinetic changes."""
    if not all(math.isfinite(float(x)) for x in (initial_speed, final_speed, distance_m)):
        raise ValueError("Inputs must be finite")
    if initial_speed < 0 or final_speed < 0 or distance_m <= 0:
        raise ValueError("Speeds must be non-negative and distance positive")
    average_speed = (initial_speed + final_speed) / 7.2
    if average_speed <= 0:
        raise ValueError("Positive distance requires a non-zero average speed")
    return distance_m / average_speed


def percentage(numerator, denominator):
    """Undefined fractions stay undefined (None), rather than reporting 0%."""
    return 100.0 * numerator / denominator if denominator > 1e-12 else None


def simulate_speed_event(
    initial_speed, final_speed, duration, mass, LD_ratio,
    turbine_diameter, efficiency, gate_mode="always_open", opening_speed=0.0,
    grade=0, steps=1200,
):
    """Integrate signed wheel power before separating propulsion and braking.

    Returned trace powers are midpoint values over equal intervals. Cumulative
    energy plots must use the interval edges, starting explicitly at zero.
    Electrical recovery is a simplified cross-domain credit, not a full battery
    model. All coefficients and the 2.2 m² frontal area retain the original scope.
    """
    values = (initial_speed, final_speed, duration, mass, LD_ratio,
              turbine_diameter, efficiency, opening_speed, grade)
    if not all(math.isfinite(float(x)) for x in values):
        raise ValueError("Inputs must be finite")
    if duration <= 0 or mass <= 0 or LD_ratio <= 0 or turbine_diameter <= 0:
        raise ValueError("Duration, mass, L/D proxy and diameter must be positive")
    if min(initial_speed, final_speed, opening_speed) < 0 or not 0 <= efficiency <= 1:
        raise ValueError("Invalid speed or efficiency")
    if steps < 2 or int(steps) != steps:
        raise ValueError("At least two integer integration steps are required")
    dt = duration / steps
    edges = np.linspace(0.0, duration, steps + 1)
    time = (edges[:-1] + edges[1:]) / 2
    speed = initial_speed + (final_speed - initial_speed) * time / duration
    velocity = speed / 3.6
    acceleration = (final_speed - initial_speed) / (3.6 * duration)
    if gate_mode == "always_open":
        active = np.ones(steps, dtype=bool)
    elif gate_mode == "smart":
        active = speed >= opening_speed
    elif gate_mode == "closed":
        active = np.zeros(steps, dtype=bool)
    else:
        raise ValueError("Unknown gate mode")
    area = math.pi * (turbine_diameter / 2) ** 2
    available = .5 * AIR_DENSITY * area * velocity ** 3
    generated = available * efficiency * active
    turbine = available * TURBINE_THRUST_COEFFICIENT * active
    vehicle = .5 * AIR_DENSITY * REFERENCE_FRONTAL_AREA / LD_ratio * velocity ** 3
    gravity = mass * GRAVITY * math.sin(math.atan(grade / 100)) * velocity
    kinetic = mass * velocity * acceleration
    required = vehicle + turbine + gravity + kinetic
    propulsion = np.maximum(required, 0)
    braking = np.maximum(-required, 0)
    trace = dict(time_s=time, time_edges_s=edges, speed_kmh=speed,
                 dt_s=dt, gate_open=active, recovered_power=generated,
                 turbine_drag_power=turbine, vehicle_drag_power=vehicle,
                 total_aerodynamic_power=vehicle + turbine,
                 gravity_power=gravity, kinetic_power=kinetic,
                 required_wheel_power=required, propulsion_power=propulsion,
                 braking_power=braking,
                 turbine_net_power=generated - turbine,
                 net_event_power=generated - propulsion)
    energy = lambda power: float(np.sum(power) * dt)
    recovered_energy, turbine_energy = energy(generated), energy(turbine)
    spent, brake_energy = energy(propulsion), energy(braking)
    kinetic_change = calculate_kinetic_energy_change(mass, initial_speed, final_speed)
    distance = float(np.sum(velocity) * dt)
    total_aero = energy(vehicle + turbine)
    net = spent - recovered_energy
    ratio = percentage(recovered_energy, spent)
    penalty_ratio = percentage(recovered_energy, turbine_energy)
    result = dict(initial_speed=initial_speed, final_speed=final_speed,
                  duration_s=duration, distance_m=distance,
                  open_time_s=float(np.sum(active) * dt),
                  kinetic_energy_change=kinetic_change,
                  vehicle_drag_energy=energy(vehicle), gravity_energy=energy(gravity),
                  turbine_drag_energy=turbine_energy, recovered_energy=recovered_energy,
                  total_aerodynamic_energy=total_aero,
                  required_wheel_energy=energy(required), total_energy_spent=spent,
                  braking_energy_to_dissipate=brake_energy,
                  net_event_energy_after_recovery=net, net_battery_energy=net,
                  recovery_vs_total_spent_pct=ratio,
                  recovery_vs_turbine_penalty_pct=penalty_ratio,
                  recovery_vs_total_aero_pct=percentage(recovered_energy, total_aero),
                  recovery_vs_kinetic_loss_pct=percentage(recovered_energy, max(-kinetic_change, 0)),
                  recovered_wh_per_km=recovered_energy / 3600 / (distance / 1000) if distance > 0 else None,
                  net_event_wh_per_km_after_recovery=net / 3600 / (distance / 1000) if distance > 0 else None,
                  trace=trace)
    result["net_battery_wh_per_km"] = result["net_event_wh_per_km_after_recovery"]
    return result


def generation_concentration_speed(initial_speed, final_speed):
    """Threshold where instantaneous output equals mean always-open output.

    For P=K*D²*v³ and a linear speed trace, v*=mean(v³)^(1/3).
    Maximizes retained electricity fraction minus exposure time fraction.
    This is an explicitly chosen, scale-free screening objective; it does NOT
    optimize net energy or improve generation / turbine drag. Diameter and
    efficiency cancel. No cut-in torque, wattage target or rating is invented.
    """
    lo, hi = sorted((initial_speed, final_speed))
    return ((hi ** 3 + hi ** 2 * lo + hi * lo ** 2 + lo ** 3) / 4) ** (1 / 3)


def scan_gate_opening_speeds(
    initial_speed, final_speed, duration, mass, LD_ratio,
    turbine_diameter, efficiency, grade=0,
):
    maximum = max(initial_speed, final_speed)
    candidates = sorted(set([0.0, float(maximum),
        generation_concentration_speed(initial_speed, final_speed)] +
        [float(x) for x in range(int(math.ceil(maximum)) + 1)]))
    reference = simulate_speed_event(initial_speed, final_speed, duration, mass,
        LD_ratio, turbine_diameter, efficiency, grade=grade)
    rows = []
    for threshold in candidates + [None]:
        result = simulate_speed_event(initial_speed, final_speed, duration, mass,
            LD_ratio, turbine_diameter, efficiency,
            gate_mode="closed" if threshold is None else "smart",
            opening_speed=threshold or 0, grade=grade)
        retained = (result["recovered_energy"] / reference["recovered_energy"]
                    if reference["recovered_energy"] > 1e-12 else 0.0)
        exposure = result["open_time_s"] / duration
        row = {key: result[key] for key in (
            "recovered_energy", "turbine_drag_energy", "total_energy_spent",
            "net_event_energy_after_recovery", "recovery_vs_total_spent_pct",
            "recovery_vs_turbine_penalty_pct", "recovery_vs_total_aero_pct",
            "recovery_vs_kinetic_loss_pct", "open_time_s")}
        row.update(opening_speed=threshold, policy="closed" if threshold is None else "threshold",
                   retained_generation_pct=retained * 100,
                   exposure_time_pct=exposure * 100,
                   concentration_score=retained - exposure)
        rows.append(row)
    return rows


def find_optimal_gate_speed(
    initial_speed, final_speed, duration, mass, LD_ratio,
    turbine_diameter, efficiency, grade=0,
):
    """Return a generation-concentration recommendation, not a net-energy optimum.

    Always-closed remains a reference candidate; it is not the default objective.
    A constant-speed or zero-output case has no distinguished useful threshold.
    """
    scan = scan_gate_opening_speeds(initial_speed, final_speed, duration, mass,
                                  LD_ratio, turbine_diameter, efficiency, grade)
    if abs(final_speed - initial_speed) < 1e-9 or efficiency <= 0 or max(initial_speed, final_speed) == 0:
        return None, scan
    theoretical = generation_concentration_speed(initial_speed, final_speed)
    # Use the analytical optimum to avoid claiming an integer scan artefact is
    # a unique speed. Its integrated metrics use the same trace as all cases.
    best = dict(min((row for row in scan if row["policy"] == "threshold"),
                    key=lambda row: abs(row["opening_speed"] - theoretical)))
    best["objective_key"] = "concentration_score"
    best["objective_label"] = "retained generation fraction minus exposure time fraction"
    return best, scan
