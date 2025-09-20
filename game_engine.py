# In game_engine.py
import random

def roll_dice(sides: int, count: int = 1) -> str:
    """
    Rolls a number of dice with a given number of sides.
    This is a tool the AI can use for skill checks or combat.
    """

    # --- START of the fix --- # COMMENT: These two lines will fix the TypeError.
    # We explicitly convert the inputs to integers, just in case the AI
    # sends them as floats (e.g., 20.0 instead of 20).
    sides = int(sides)
    count = int(count)
    # --- END of the fix --- #

    print(f"--> Rolling {count}d{sides}...")

    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls)

    # Return a nice, descriptive string for the AI to use in its story
    if count == 1:
        return f"The die lands on: {total}."
    else:
        rolls_str = " + ".join(map(str, rolls))
        return f"The dice land on: {total} ({rolls_str})."
