from resonators.BaseResonator import Resonator
import os

class Shorekeeper(Resonator):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "Shorekeeper.json"))

    def __init__(self):
        Shorekeeper_base_stats = {
            "Char_HP": 16713, "HP%": 12.0, "DEF%": 0.0, "Char_DEF": 1100,
            "ER": 100.0, "Crit Rate": 5.0, "Crit DMG": 150, "Healing Bonus": 12.0,
            "Healing": 0.0, "Energy Recharge": 0.0, "Shield Strength": 0.0,
            "Char_ATK": 288, "Weapon ATK": 0.0, "ATK%": 0.0, "Resonance Cost": 125,
            "Spectro DMG": 0.0, "Electro DMG": 0.0, "Aero DMG": 0.0,
            "Fusion DMG": 0.0, "Glacio DMG": 0.0, "Havoc DMG": 0.0,
            "Spectro Amp": 0.0, "Electro Amp": 0.0, "Aero Amp": 0.0,
            "Fusion Amp": 0.0, "Glacio Amp": 0.0, "Havoc Amp": 0.0,
            "Heavy Bon": 0.0, "Skill Bon": 0.0, "Lib Bon": 0.0, "Echo Bon": 0.0,
            "All DMG": 0.0, "Outro Bon": 0.0, "Basic Bon": 0.0,
            "Heavy Amp": 0.0, "Skill Amp": 0.0, "Lib Amp": 0.0, "Echo Amp": 0.0,
            "All Amp": 0.0, "Outro Amp": 0.0, "Basic Amp": 0.0,
            "Gen_Def Shred": 0.0, "Gen_Res Shred": 0.0,
            "Spectro Def Shred": 0.0, "Spectro Res Shred": 0.0,
            "Electro Def Shred": 0.0, "Electro Res Shred": 0.0,
            "Aero Def Shred": 0.0, "Aero Res Shred": 0.0,
            "Fusion Def Shred": 0.0, "Fusion Res Shred": 0.0,
            "Glacio Def Shred": 0.0, "Glacio Res Shred": 0.0,
            "Heavy Def Shred": 0.0, "Heavy Res Shred": 0.0,
            "Skill Def Shred": 0.0, "Skill Res Shred": 0.0,
            "Lib Def Shred": 0.0, "Lib Res Shred": 0.0,
            "Basic Def Shred": 0.0, "Basic Res Shred": 0.0,
            "Outro Def Shred": 0.0, "Outro Res Shred": 0.0,
        }

        super().__init__("Shorekeeper", "Spectro", Shorekeeper_base_stats, Shorekeeper.json_path)
        self.weapon_atk = 0
        self.load_moves()
        self.name = "Shorekeeper"

        # Stellarealm logic
        self.stellarealm_stage = None  # None → "Outer" → "Inner" → "Supernal"
        self.discernment_available = False
        self.stellarealm_start_frame = None

        self.swap_conditional_moves = [
            "Basic: Origin Calculus 1 (Swap)",
            "Basic: Origin Calculus 1 2 3 4 (Swap)",
            "Basic: Origin Calculus 1 2 (Swap)",
            "Basic: Origin Calculus 1 2 3 (Swap)",
        ]

        self.forced_swap_moves = [
            "Skill: Chaos Theory (Swap)",
            "Basic: Origin Calculus 1 (Swap)",
            "Basic: Origin Calculus 1 2 (Swap)",
            "Basic: Origin Calculus 1 2 3 (Swap)",
            "Basic: Origin Calculus 1 2 3 4 (Swap)",
            "Basic: Origin Calculus (Mid-Air) (Swap)",
            "Forte: Transmutation (Swap)",
            "Forte: Illation (Swap)",
        ]

    def can_use_move(self, move_name, resources, history, global_history = None):
        # Block all dodge moves
        if "Dodge" in move_name:
            return False, "Dodge moves are disabled"
        
        if "Counter" in move_name:
            return False, "Counter moves are disabled"

        if move_name in []:
            return False, "move is forbidden"

        if move_name == "Intro 2: Discernment" and not self.discernment_available:
            return False, "Discernment not available"

        if move_name not in self.moves:
            return False, "Unknown move"

        move = self.moves[move_name]
        for res in ["Forte", "Resonance", "Concerto"]:
            cost = move.get(res, 0) or 0
            if cost < 0 and resources[res] < abs(cost):
                return False, f"Not enough {res}"

        return True, "move allowed"

    def get_execution_flags(self, resources, history):
        return {
            "can_use_Discernment": self.discernment_available
        }

    def process_move_effects(self, move_name, current_frame):
        super().process_move_effects(move_name, current_frame)

        move_data = self.moves.get(move_name, {})

        # === Stellarealm timeout ===
        if self.stellarealm_start_frame is not None and current_frame - self.stellarealm_start_frame >= 1800:
            # print(f"[DEBUG] Stellarealm expired after 30s at frame {current_frame}")
            self.stellarealm_stage = None
            self.discernment_available = False
            self.stellarealm_start_frame = None


        # === Stellarealm evolution ===
        if move_name == "Liberation: End Loop":
            # print(f"[DEBUG] Shorekeeper generated Outer Stellarealm")
            self.stellarealm_stage = "Outer"
            self.stellarealm_start_frame = current_frame

        if "Intro" in move_name:
            if self.stellarealm_stage == "Outer":
                # print(f"[DEBUG] Shorekeeper evolved Outer → Inner")
                self.stellarealm_stage = "Inner"
                self.queued_buff = {
                    "buff_name": "Stellarealm Crit Rate",
                    "stats": {"Crit Rate": 12.5},
                    "duration_frames": 1800,
                    "scope": "global"
                }

            elif self.stellarealm_stage == "Inner":
                # print(f"[DEBUG] Shorekeeper evolved Inner → Supernal")
                self.stellarealm_stage = "Supernal"
                self.discernment_available = True
                self.queued_buff = {
                    "buff_name": "Stellarealm Crit DMG",
                    "stats": {"Crit DMG": 25.0},
                    "duration_frames": 1800,
                    "scope": "global"
                }

        if move_name == "Intro 2: Discernment":
            # print(f"[DEBUG] Shorekeeper consumed Discernment")
            self.discernment_available = False

        if move_name == "Outro: Binary Butterfly":
            # print("Outro trigger from SK for 15% AMP")
            self.queued_buff = {
                "buff_name": "Stellarealm Amp",
                "stats": {"All Amp": 15.0},
                "duration_frames": 1800,
                "scope": "global"
            }

    Shorekeeper_Buffs = [
    {
        "buff_name": "Stellarealm Crit Rate",
        "trigger": "Liberation: End Loop",
        "stats": {"Crit Rate": 12.5},
        "duration_frames": 1800,  # 30s
        "scope": "global",
        "max_stacks": 1
    },
    {
        "buff_name": "Stellarealm Crit DMG",
        "trigger": "Liberation: End Loop",
        "stats": {"Crit DMG": 25.0},
        "duration_frames": 1800,  # 30s
        "scope": "global",
        "max_stacks": 1
    },
    {
        "buff_name": "Stellarealm AMP",
        "trigger": "Outro: Binary Butterfly",
        "stats": {"All Amp": 15.0},
        "duration_frames": 1800,  # 30s
        "scope": "global",
        "max_stacks": 1
    }
]
