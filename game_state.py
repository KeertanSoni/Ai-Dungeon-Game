
initial_game_state = {
    "player": {
        "name": "Kaelan",
        "hp": 20,
        "max_hp": 20,
        "attack_power": 5,
        "inventory": ["a rusty sword", "a healing potion"],
    },
    "current_location": {
        "name": "The Whispering Cavern",
        "description": "You find yourself in a dimly lit cavern. The air is damp, and a faint, eerie whisper seems to echo from the deeper shadows. A single, narrow passage leads further into the darkness.",
        "npcs": [],
    },
    "game_log": [
        # COMMENT: This line is the fix. It's now a dictionary, just like the others.
        {"role": "dm", "content": "Your adventure begins."}
    ]
}