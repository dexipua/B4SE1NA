"""Ready-made user profiles: category weights (0-10) and optional ideal levels (0-1)."""

PRESETS: dict[str, dict[str, dict[str, float]]] = {
    "Студент": {
        "weights": {
            "safety": 6,
            "economy": 7,
            "health": 3,
            "environment": 4,
            "governance": 5,
            "digital": 10,
        },
        "ideal": {"economy": 0.7},
    },
    "Віддалений працівник": {
        "weights": {
            "safety": 7,
            "economy": 5,
            "health": 5,
            "environment": 6,
            "governance": 6,
            "digital": 10,
        },
        "ideal": {"economy": 0.6, "governance": 0.8},
    },
    "Сім'я з дітьми": {
        "weights": {
            "safety": 10,
            "economy": 6,
            "health": 9,
            "environment": 8,
            "governance": 6,
            "digital": 4,
        },
        "ideal": {"digital": 0.8},
    },
}
