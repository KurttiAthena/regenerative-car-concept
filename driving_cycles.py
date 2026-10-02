from car_physics_model import simulate_speed_event


# All synthetic events use the same duration. Distance is derived from the
# speed-vs-time trace so the kinematics remain self-consistent.
NORMALIZED_EVENT_DURATION = 20.0  # seconds


def _make_event(start_speed, end_speed, condition):
    average_speed_ms = ((start_speed + end_speed) / 2.0) / 3.6
    distance = average_speed_ms * NORMALIZED_EVENT_DURATION

    return (
        start_speed,
        end_speed,
        distance,
        NORMALIZED_EVENT_DURATION,
        condition,
    )


DIRT_ROAD_CYCLE = [
    _make_event(0, 30, "acceleration"),
    _make_event(20, 30, "cruise"),
]

CITY_CYCLE = [
    _make_event(0, 50, "acceleration"),
    _make_event(40, 50, "cruise"),
]

HIGHWAY_CYCLE = [
    _make_event(50, 100, "acceleration"),
    _make_event(90, 100, "cruise"),
]

MOTORWAY_CYCLE = [
    _make_event(80, 130, "acceleration"),
    _make_event(120, 130, "cruise"),
]


def get_cycle_event(cycle, event_type, braking_mode=False):
    """Return the single selected event; acceleration and cruise are never summed."""

    for start_speed, end_speed, distance, duration, condition in cycle:
        if condition != event_type:
            continue

        if braking_mode:
            start_speed, end_speed = end_speed, start_speed

        return {
            "start_speed": start_speed,
            "end_speed": end_speed,
            "distance": distance,
            "duration": duration,
            "condition": condition,
        }

    raise ValueError(f"No '{event_type}' event exists in the selected cycle")


def simulate_cycle(
    cycle,
    mass,
    LD,
    turbine_diameter,
    efficiency,
    gate_mode,
    grade,
    braking_mode,
    event_type="acceleration",
    opening_speed=0.0,
):
    """Simulate exactly one user-selected event from the chosen driving scenario."""

    event = get_cycle_event(
        cycle,
        event_type,
        braking_mode,
    )

    result = simulate_speed_event(
        event["start_speed"],
        event["end_speed"],
        event["duration"],
        mass,
        LD,
        turbine_diameter,
        efficiency,
        gate_mode=gate_mode,
        opening_speed=opening_speed,
        grade=grade,
    )

    result["mode"] = (
        ("Braking / " if braking_mode else "Normal / ")
        + event_type.capitalize()
    )

    result["event"] = event

    # Compatibility aliases used by the previous app.py.
    result["total_recovered_energy"] = result["recovered_energy"]
    result["total_available_energy"] = result["total_energy_spent"]
    result["recovery_percentage"] = result["recovery_vs_total_spent_pct"]

    return result
