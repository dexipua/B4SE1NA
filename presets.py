"""Ready-made user profiles: category weights (0-10) and optional ideal levels (0-1).

Keys are stable ids; their display names live in i18n.py under "preset.<id>".
"""

PRESETS: dict[str, dict[str, dict[str, float]]] = {
    "student": {
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
    "remote": {
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
    "family": {
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
    "Пенсіонер": {
        "weights": {
            "safety": 8,
            "economy": 3,
            "health": 10,
            "environment": 8,
            "governance": 6,
            "digital": 2,
        },
        "ideal": {"health": 0.9, "environment": 0.8},
    },
    "Стартапер": {
        "weights": {
            "safety": 4,
            "economy": 9,
            "health": 3,
            "environment": 3,
            "governance": 8,
            "digital": 10,
        },
        "ideal": {"economy": 0.8, "governance": 0.7},
    },
    "IT-спеціаліст": {
        "weights": {
            "safety": 5,
            "economy": 8,
            "health": 4,
            "environment": 4,
            "governance": 6,
            "digital": 10,
        },
        "ideal": {"digital": 0.9, "economy": 0.7},
    },
    "Еко-свідомий": {
        "weights": {
            "safety": 5,
            "economy": 2,
            "health": 6,
            "environment": 10,
            "governance": 7,
            "digital": 4,
        },
        "ideal": {"environment": 0.9},
    },
    "Шукач роботи": {
        "weights": {
            "safety": 6,
            "economy": 10,
            "health": 3,
            "environment": 2,
            "governance": 5,
            "digital": 6,
        },
        "ideal": {"economy": 0.8},
    },
    "Безпека понад усе": {
        "weights": {
            "safety": 10,
            "economy": 3,
            "health": 5,
            "environment": 4,
            "governance": 7,
            "digital": 2,
        },
        "ideal": {"safety": 0.9},
    },
    "Лікування": {
        "weights": {
            "safety": 5,
            "economy": 3,
            "health": 10,
            "environment": 6,
            "governance": 5,
            "digital": 3,
        },
        "ideal": {"health": 0.9},
    },
    "Борець за чесність": {
        "weights": {
            "safety": 6,
            "economy": 3,
            "health": 4,
            "environment": 4,
            "governance": 10,
            "digital": 5,
        },
        "ideal": {"governance": 0.9},
    },
    "Збалансований": {
        "weights": {
            "safety": 5,
            "economy": 5,
            "health": 5,
            "environment": 5,
            "governance": 5,
            "digital": 5,
        },
        "ideal": {},
    },
}
