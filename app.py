import streamlit as st
import os
import copy
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
from game_state import initial_game_state
from game_engine import roll_dice

# --- Configuration and Initialization ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found. Please set it in your .env file.")
else:
    genai.configure(api_key=api_key)

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=[roll_dice]
)

# --- Helper Function for State Management ---
def update_game_state(current_state, state_update_json):
    """Deeply updates the game state dictionary with changes from the AI."""
    try:
        updates = json.loads(state_update_json)
        def merge_dicts(d1, d2):
            for k, v in d2.items():
                if k in d1 and isinstance(d1[k], dict) and isinstance(v, dict):
                    merge_dicts(d1[k], v)
                else:
                    d1[k] = v
        merge_dicts(current_state, updates)
        st.rerun() # Rerun the app to show the updated state in the sidebar
    except json.JSONDecodeError:
        st.warning("AI did not produce a valid JSON for state update.")

# --- Streamlit UI Setup ---
st.set_page_config(page_title="AI Dungeon Master", page_icon="🐉", layout="wide")
st.title("AI Dungeon Master 🐲")

# --- Session State Initialization ---
# This is the "memory" of your app. It remembers the game state across interactions.
if 'game_state' not in st.session_state:
    st.session_state.game_state = copy.deepcopy(initial_game_state)
    st.session_state.chat = model.start_chat(enable_automatic_function_calling=False)
    # Add the first message to the game log
    st.session_state.game_state["game_log"].append(
        {"role": "dm", "content": st.session_state.game_state["current_location"]["description"]}
    )

# --- Character Sheet Sidebar ---
with st.sidebar:
    st.header("Character Sheet")
    player = st.session_state.game_state['player']
    st.write(f"**Name:** {player['name']}")
    st.progress(int((player['hp'] / player['max_hp']) * 100), text=f"**HP:** {player['hp']}/{player['max_hp']}")
    st.write(f"**Attack Power:** {player['attack_power']}")
    st.write("**Inventory:**")
    for item in player['inventory']:
        st.write(f"- {item}")

# --- Main Chat Interface ---
# Display the game log
for message in st.session_state.game_state["game_log"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get player input using the chat input box
if player_input := st.chat_input("What do you do?"):
    # Add player's message to the log
    st.session_state.game_state["game_log"].append({"role": "player", "content": player_input})
    with st.chat_message("player"):
        st.markdown(player_input)

    # Show a spinner while the DM is "thinking"
    with st.spinner("The Dungeon Master is pondering your fate..."):
        prompt = f"""
        You are the Dungeon Master. Your goal is to create a compelling story.
        Current Game State: {json.dumps(st.session_state.game_state, indent=2)}
        The player's command is: '{player_input}'
        **Your Task:**
        1. Describe what happens next.
        2. If a dice roll is needed, call the 'roll_dice' tool.
        3. After the description, you MUST output a JSON block with any changes to the game state.
           The JSON block must start with ```json and end with ```.
        """
        
        # Send prompt to the model
        response = st.session_state.chat.send_message(prompt)
        
        # Handle potential tool calls
        if response.parts[0].function_call:
            fc = response.parts[0].function_call
            tool_result = globals()[fc.name](**fc.args)
            response = st.session_state.chat.send_message(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=fc.name,
                        response={"result": tool_result}
                    )
                )
            )
        
        # Process and display the final response
        final_response_text = ""
        if response.parts[0].text:
            final_response_text = response.parts[0].text
        
        narrative = final_response_text
        state_update_match = re.search(r"```json\n(\{.*?\})\n```", final_response_text, re.DOTALL)
        
        if state_update_match:
            state_update_json = state_update_match.group(1)
            narrative = re.sub(r"```json\n(\{.*?\})\n```", "", narrative, flags=re.DOTALL).strip()
            # We call the update function here, which will also trigger a rerun
            update_game_state(st.session_state.game_state, state_update_json)
        
        # Add the DM's narrative to the log and display it
        st.session_state.game_state["game_log"].append({"role": "dm", "content": narrative})
        with st.chat_message("dm"):
            st.markdown(narrative)