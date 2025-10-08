from resonators.BaseResonator import Resonator
import os

class Danjin(Resonator):
    # Path to the JSON file containing the character's base stats
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "Danjin.json"))
    

    def __init__(self):
        # Dictionary containing the character's base stats
        Danjin_base_stats = {
            "Char_HP": 9438, "HP%": 0.0, "DEF%": 0.0, "Char_DEF": 1149,
            "ER": 100.0, "Crit Rate": 5.0, "Crit DMG": 150, "Healing Bonus": 0.0,
            "Healing": 0.0, "Energy Recharge": 0.0, "Shield Strength": 0.0,
            "Char_ATK": 294, "Weapon ATK": 0.0, "ATK%": 12.0, "Resonance Cost": 100,
            
            # Elemental Damage
            "Spectro DMG": 0.0, "Electro DMG": 0.0, "Aero DMG": 0.0,
            "Fusion DMG": 0.0, "Glacio DMG": 0.0, "Havoc DMG": 12,

            # Echo Elemental Bonuses
            "Spectro Echo DMG": 0.0, "Electro Echo DMG": 0.0, "Aero Echo DMG": 0.0,
            "Fusion Echo DMG": 0.0, "Glacio Echo DMG": 0.0, "Havoc Echo DMG": 0.0,

            # Amplifications
            "Spectro Amp": 0.0, "Electro Amp": 0.0, "Aero Amp": 0.0,
            "Fusion Amp": 0.0, "Glacio Amp": 0.0, "Havoc Amp": 0.0,

            # Bonus Damage
            "Heavy Bon": 0.0, "Skill Bon": 0.0, "Lib Bon": 0.0, "Echo Bon": 0.0,
            "All DMG": 0.0, "Outro Bon": 0.0, "Basic Bon": 0.0,

            # Bonus Amplifications
            "Heavy Amp": 0.0, "Skill Amp": 0.0, "Lib Amp": 0.0, "Echo Amp": 0.0,
            "All Amp": 0.0, "Outro Amp": 0.0, "Basic Amp": 0.0,

            # General Shreds
            "Gen_Def Shred": 0.0, "Gen_Res Shred": 0.0,

            # Elemental Shreds
            "Havoc Def Shred": 0.0, "Havoc Res Shred": 0.0,
            "Spectro Def Shred": 0.0, "Spectro Res Shred": 0.0,
            "Electro Def Shred": 0.0, "Electro Res Shred": 0.0,
            "Aero Def Shred": 0.0, "Aero Res Shred": 0.0,
            "Fusion Def Shred": 0.0, "Fusion Res Shred": 0.0,
            "Glacio Def Shred": 0.0, "Glacio Res Shred": 0.0,

            # Type Shreds
            "Heavy Def Shred": 0.0, "Heavy Res Shred": 0.0,
            "Skill Def Shred": 0.0, "Skill Res Shred": 0.0,
            "Lib Def Shred": 0.0, "Lib Res Shred": 0.0,
            "Basic Def Shred": 0.0, "Basic Res Shred": 0.0,
            "Outro Def Shred": 0.0, "Outro Res Shred": 0.0,
        }

        # Call the parent class's constructor with the character's name, element, base stats, and JSON path
        super().__init__("Danjin", "Havoc", Danjin_base_stats, Danjin.json_path)
        # Initialize the weapon attack value
        self.weapon_atk = 0
        # Load the character's moves
        self.load_moves()
        self.next_forced_move = None
        self.name = "Danjin" 

        # Moves only usable when Danjin is NOT the active unit
        self.swap_conditional_moves = [
            "Basic: Execution 2 3",
            "Basic: Execution 2"
        ]

        # Moves that force a swap when picked
        self.forced_swap_moves = [
            "Skill: Camine Gleam (1) (Swap)",
            "Skill: Crimson Erosion (2) (Swap)",
            "Skill: Sanguine Pulse (3) (Swap)",
            "Forte: Chaoscleave (50%) (Swap)",
            "Forte: Chaoscleave (100%) (Swap)"
        ]
        
       
        

    def can_use_move(self, move_name, resources, history, global_history=None):
        # Grab last 4 unit-local moves
        recent_history = history[-4:] if history else []
        recent_moves = [entry[0] for entry in recent_history]

        # Grab last 3 global moves
        sorted_global_history = global_history[-10:] if global_history else []

        # Block all dodge/counter moves
        if "Dodge" in move_name:
            return False, "Dodge moves are disabled"
        if "Counter" in move_name:
            return False, "Counter moves are disabled"

        # Forbidden moves (expand if needed)
        if move_name in []:
            return False, "Move is forbidden"

        # === Execution checks: use GLOBAL history ===
        exec_flags = self.get_execution_flags(resources, sorted_global_history)

        if move_name in ["Skill: Sanguine Pulse (3)", "Skill: Sanguine Pulse (3) (Swap)"] and not exec_flags["can_use_SanguinePulse"]:
            return False, f"Execution prerequisite not met (global moves {sorted_global_history})"

        if move_name in ["Skill: Crimson Erosion (2)", "Skill: Crimson Erosion (2) (Swap)"] and not exec_flags["can_use_CrimsonErosion"]:
            return False, f"Execution prerequisite not met (global moves {sorted_global_history})"

        # === Lockout handling (local still fine) ===
        always_allowed_skills = {"Skill: Camine Gleam (1)", "Skill: Camine Gleam (1) (Swap)"}
        skills_locked = not (exec_flags["can_use_SanguinePulse"] or exec_flags["can_use_CrimsonErosion"])
        if move_name.startswith("Skill:") and skills_locked and move_name not in always_allowed_skills:
            return False, "Skills locked - fallback to basic attacks"

        # === Resource check ===
        if move_name not in self.moves:
            return False, "Unknown move"
        move = self.moves[move_name]

        if "Forte" in move_name:
            if "50%" in move_name and resources["Forte"] < 20.5:
                return False, "Not enough Forte for Chaoscleave 50%"
            if "100%" in move_name and resources["Forte"] < 41:
                return False, "Not enough Forte for Chaoscleave 100%"

        for res in ["Forte", "Resonance", "Concerto"]:
            cost = move.get(res, 0) or 0
            if cost < 0 and resources[res] < abs(cost):
                return False, f"Not enough {res}"

        return True, "move allowed"


    def get_execution_flags(self, resources, history):
        """history = last few moves, ideally GLOBAL for strict checks"""

        # Check if any unit ever used Marcato
        has_marcato = any(entry[1] == "Liberation: Marcato" for entry in history)

        if has_marcato:
            filtered = [entry for entry in history if entry[1] != "Liberation: Marcato"]
        else:
            filtered = list(history)

        # FIX: extract move names only
        history_names = [entry[1] for entry in filtered][-5:]
        forte = resources.get("Forte", 0)

        can_use_crimson = False
        can_use_sanguine = False

        # Crimson: must follow Execution 1/2 or Vindiction
        if history_names and history_names[-1] in ["Basic: Execution 1 2", "Intro: Vindiction", "Basic: Execution 2"]:
            can_use_crimson = True

        # Sanguine: must follow Execution 2 3 or Execution 1 2 3
        if history_names and history_names[-1] in ["Basic: Execution 1 2 3", "Basic: Execution 2 3"]:
            can_use_sanguine = True

        # Forte thresholds
        can_use_chaoscleave_50 = forte >= 20.5
        can_use_chaoscleave_100 = forte >= 41

        return {
            "can_use_CrimsonErosion": can_use_crimson,
            "can_use_SanguinePulse": can_use_sanguine,
            "can_use_Chaoscleave_50": can_use_chaoscleave_50,
            "can_use_Chaoscleave_100": can_use_chaoscleave_100,
        }




    def process_move_effects(self, move_name, current_frame):
        super().process_move_effects(move_name, current_frame)  # includes update_buffs
    
        # Apply new buff if the move is the correct one
        if move_name in ['Skill: Crimson Erosion (2)', 'Skill: Crimson Erosion (2) (Swap)']:
            self.queued_buff = {
                "buff_name": "Crimson Erosion Bonus",
                "stats": {"All DMG": 20},
                "duration_frames": 720,  # 12 seconds at 60fps
                "scope": "global",
                "max_stacks": 1
            }

        if move_name == "Skill: Sanguine Pulse (3)":
            self.add_buff(
                buff_name="Sanguine Pulse: Heavy Bonus",
                buff_stats={"Heavy Bon": 30},
                duration_frames=300,  # 5s * 60fps
                current_frame=current_frame,
                max_stacks=1
            )

        if move_name == "Outro: Duality":
            self.queued_buff = {
                "buff_name": "Danjin Outro Havoc Amp",
                "stats": {"Havoc Amp": 23},
                "duration_frames": 840, # 14 secs
                "scope": "next"
            }


    Danjin_Buffs = [
    {
        "buff_name": "Crimson Erosion Bonus",
        "trigger": "Skill: Crimson",
        "stats": {"All DMG": 20},
        "duration_frames": 720,  # 12s
        "scope": "global",
        "max_stacks": 1
    },
    {
        "buff_name": "Sanguine Pulse: Heavy Bonus",
        "trigger": "Skill: Sanguine Pulse (3)",
        "stats": {"Heavy Bon": 30},
        "duration_frames": 300,  # 5s
        "scope": "self",
        "max_stacks": 1
    },
    {
        "buff_name": "Danjin Outro Havoc Amp",
        "trigger": "Outro: Duality",
        "stats": {"Havoc Amp": 23},
        "duration_frames": 840,  # 14s
        "scope": "next",
        "max_stacks": 1
    }
]
