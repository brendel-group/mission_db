import random

CHARACTERS = (
    "Frodo",
    "Sam",
    "Merry",
    "Pippin",
    "Aragorn",
    "Legolas",
    "Gimli",
    "Boromir",
    "Gandalf",
    "Saruman",
    "Sauron",
)


def random_character():
    return random.choice(CHARACTERS)


def ring_bearer(name):
    return name in ("Frodo", "Sam")


if __name__ == "__main__":
    character = random_character()
    if ring_bearer(character):
        print(f"{character} is a ring bearer")
    else:
        print(f"{character} is not a ring bearer")
