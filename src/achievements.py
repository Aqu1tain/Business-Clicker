from dataclasses import dataclass

@dataclass
class Achievement:
    title: str
    description: str
    condition_type: str
    condition_value: int
    reward: float
    unlocked: bool = False

ACHIEVEMENTS = [
    Achievement(
        "Travailleur Acharné",
        "Cliquez 1000 fois",
        "clicks",
        1000,
        100.0
    ),
    Achievement(
        "Entrepreneur",
        "Achetez 10 améliorations",
        "upgrades",
        10,
        200.0
    ),
    Achievement(
        "Millionnaire",
        "Gagnez 1 000 000€",
        "money_earned",
        1000000,
        1000.0
    )
]