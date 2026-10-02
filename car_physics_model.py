import math


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
    Integrate the current simplified turbine aerodynamic-penalty proxy.

    The model treats the free-stream kinetic power through the turbine swept
    area as the aerodynamic penalty proxy. This is intentionally conservative
    and is listed as a model limitation in the UI.
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


def simulate_speed_event(
    initial_speed,
    final_speed,
    duration,
    mass,
    LD_ratio,
    turbine_diameter,
    efficiency,
    gate_mode="always_open",
    opening_speed=0.0,
    grade=0,
    steps=200,
):
    """
    Integrate one simplified event using a linear speed-vs-time trace.

    The same function is used for acceleration, slight-speed-change cruise,
    and braking. For smart gates, the turbine is open only while vehicle speed
    is at or above `opening_speed`.
    """

    if duration <= 0:
        raise ValueError("duration must be greater than zero")

    dt = duration / steps

    vehicle_drag_energy = 0.0
    gravity_energy = 0.0
    turbine_drag_energy = 0.0
    recovered_energy = 0.0
    distance = 0.0
    open_time = 0.0

    for i in range(steps):
        fraction = (i + 0.5) / steps
        speed = initial_speed + (final_speed - initial_speed) * fraction
        V = speed / 3.6

        if gate_mode == "always_open":
            turbine_active = True
        elif gate_mode == "smart":
            turbine_active = should_open_gate(speed, opening_speed)
        else:
            turbine_active = False

        result = calculate_energy(
            mass,
            speed,
            LD_ratio,
            turbine_diameter,
            efficiency,
            turbine_active,
            grade,
        )

        distance += V * dt
        vehicle_drag_energy += result["vehicle_drag_power"] * dt
        gravity_energy += result["gravity_power"] * dt
        turbine_drag_energy += result["turbine_drag_power"] * dt
        recovered_energy += result["recovered_power"] * dt

        if turbine_active:
            open_time += dt

    kinetic_energy_change = calculate_kinetic_energy_change(
        mass,
        initial_speed,
        final_speed,
    )

    # Required wheel work for the prescribed event before crediting generated
    # electricity. It can be negative during a braking/downhill event.
    required_wheel_energy = (
        kinetic_energy_change
        + vehicle_drag_energy
        + gravity_energy
        + turbine_drag_energy
    )

    total_energy_spent = max(required_wheel_energy, 0.0)
    braking_energy_to_dissipate = max(-required_wheel_energy, 0.0)
    net_event_energy_after_recovery = total_energy_spent - recovered_energy

    recovery_vs_total_spent_pct = (
        recovered_energy / total_energy_spent * 100.0
        if total_energy_spent > 0
        else 0.0
    )

    recovery_vs_turbine_penalty_pct = (
        recovered_energy / turbine_drag_energy * 100.0
        if turbine_drag_energy > 0
        else 0.0
    )

    kinetic_energy_lost = max(-kinetic_energy_change, 0.0)
    recovery_vs_kinetic_loss_pct = (
        recovered_energy / kinetic_energy_lost * 100.0
        if kinetic_energy_lost > 0
        else 0.0
    )

    distance_km = distance / 1000.0
    recovered_wh_per_km = (
        recovered_energy / 3600.0 / distance_km
        if distance_km > 0
        else 0.0
    )

    net_event_wh_per_km_after_recovery = (
        net_event_energy_after_recovery / 3600.0 / distance_km
        if distance_km > 0
        else 0.0
    )

    return {
        "initial_speed": initial_speed,
        "final_speed": final_speed,
        "duration_s": duration,
        "distance_m": distance,
        "open_time_s": open_time,
        "kinetic_energy_change": kinetic_energy_change,
        "vehicle_drag_energy": vehicle_drag_energy,
        "gravity_energy": gravity_energy,
        "turbine_drag_energy": turbine_drag_energy,
        "recovered_energy": recovered_energy,
        "required_wheel_energy": required_wheel_energy,
        "total_energy_spent": total_energy_spent,
        "braking_energy_to_dissipate": braking_energy_to_dissipate,
        "net_event_energy_after_recovery": net_event_energy_after_recovery,

        # Compatibility alias. This is a simplified cross-domain screening
        # balance, not full battery energy consumption.
        "net_battery_energy": net_event_energy_after_recovery,
        "recovery_vs_total_spent_pct": recovery_vs_total_spent_pct,
        "recovery_vs_turbine_penalty_pct": recovery_vs_turbine_penalty_pct,
        "recovery_vs_kinetic_loss_pct": recovery_vs_kinetic_loss_pct,
        "recovered_wh_per_km": recovered_wh_per_km,
        "net_event_wh_per_km_after_recovery": net_event_wh_per_km_after_recovery,
        "net_battery_wh_per_km": net_event_wh_per_km_after_recovery,
    }


def scan_gate_opening_speeds(
    initial_speed,
    final_speed,
    duration,
    mass,
    LD_ratio,
    turbine_diameter,
    efficiency,
    grade=0,
):
    """
    Evaluate every integer gate threshold on the same complete speed event.

    Keeping the event fixed is important: changing the event endpoint for each
    candidate would make the thresholds incomparable. Braking events therefore
    remain full prescribed events while the gate simply closes below each
    candidate threshold.
    """

    low_speed = int(math.ceil(min(initial_speed, final_speed)))
    high_speed = int(math.floor(max(initial_speed, final_speed)))

    if high_speed < low_speed:
        return []

    scan = []

    for opening_speed in range(low_speed, high_speed + 1):
        result = simulate_speed_event(
            initial_speed,
            final_speed,
            duration,
            mass,
            LD_ratio,
            turbine_diameter,
            efficiency,
            gate_mode="smart",
            opening_speed=opening_speed,
            grade=grade,
        )

        scan.append({
            "opening_speed": opening_speed,
            "recovered_energy": result["recovered_energy"],
            "turbine_drag_energy": result["turbine_drag_energy"],
            "total_energy_spent": result["total_energy_spent"],
            "net_event_energy_after_recovery": result[
                "net_event_energy_after_recovery"
            ],
            "recovery_vs_total_spent_pct": result[
                "recovery_vs_total_spent_pct"
            ],
            "recovery_vs_turbine_penalty_pct": result[
                "recovery_vs_turbine_penalty_pct"
            ],
            "recovery_vs_kinetic_loss_pct": result[
                "recovery_vs_kinetic_loss_pct"
            ],
        })

    return scan

def find_optimal_gate_speed(
    initial_speed,
    final_speed,
    duration,
    mass,
    LD_ratio,
    turbine_diameter,
    efficiency,
    grade=0,
):
    """
    Find the threshold that maximizes recovered energy / total energy spent.

    If several thresholds have the same percentage, prefer the one that
    recovers more absolute electrical energy.
    """

    scan = scan_gate_opening_speeds(
        initial_speed,
        final_speed,
        duration,
        mass,
        LD_ratio,
        turbine_diameter,
        efficiency,
        grade,
    )

    if not scan:
        return None, []

    if final_speed < initial_speed:
        objective_key = "recovery_vs_kinetic_loss_pct"
        objective_label = "recovered energy / kinetic energy lost"
    else:
        objective_key = "recovery_vs_total_spent_pct"
        objective_label = "recovered energy / total energy spent"

    best = max(
        scan,
        key=lambda row: (
            row[objective_key],
            row["recovered_energy"],
        ),
    )

    best = dict(best)
    best["objective_key"] = objective_key
    best["objective_label"] = objective_label

    return best, scan
