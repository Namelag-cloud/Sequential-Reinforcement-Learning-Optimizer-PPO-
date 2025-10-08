from resonators.BaseResonator import Resonator
import os

class Mortefi(Resonator):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "Mortefi.json"))

    def __init__(self):
        mortefi_base_stats = {
            "Char_HP": 10025, "HP%": 0.0, "DEF%": 0.0, "Char_DEF": 1137,
            "ER": 100.0, "Crit Rate": 5.0, "Crit DMG": 150, "Healing Bonus": 0.0,
            "Healing": 0.0, "Energy Recharge": 0.0, "Shield Strength": 0.0,
            "Char_ATK": 250, "Weapon ATK": 0.0, "ATK%": 12.0, "Resonance Cost": 125,
            "Spectro DMG": 0.0, "Electro DMG": 0.0, "Aero DMG": 0.0,
            "Fusion DMG": 12.0, "Glacio DMG": 0.0, "Havoc DMG": 0.0,
            "Spectro Amp": 0.0, "Electro Amp": 0.0, "Aero Amp": 0.0,
            "Fusion Amp": 0.0, "Glacio Amp": 0.0, "Havoc Amp": 0.0,
            "Heavy Bon": 0.0, "Skill Bon": 0.0, "Lib Bon": 0.0,
            "All DMG": 0.0, "Outro Bon": 0.0, "Basic Bon": 0.0, "Echo Bon": 0.0,
            "Heavy Amp": 0.0, "Skill Amp": 0.0, "Lib Amp": 0.0, "Echo Amp": 0.0,
            "All Amp": 0.0, "Outro Amp": 0.0, "Basic Amp": 0.0,
            "Gen_Def Shred": 0.0, "Gen_Res Shred": 0.0,
            "Havoc Def Shred": 0.0, "Havoc Res Shred": 0.0,
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

        super().__init__("Mortefi", "Fusion", mortefi_base_stats, Mortefi.json_path)
        self.weapon_atk = 0
        self.load_moves()
        self.next_forced_move = None
        self.name = "Mortefi"
        self.cord_attack_ready = False
        self.last_cord_attack_frame = -9999  # just to avoid instant reactivation
        self.cord_attack_cooldown_frames = 21  # 0.35s at 60fps
        
        self.swap_conditional_moves = [
            "Basic: Impromptu Show 4 (Halfway Cancel)",
            "Basic: Impromptu Show 4 (Cancel)",
            "Basic: Impromptu Show 4 (Swap)",

        ]

        self.forced_swap_moves = [
            "Forte: Fury Fogue (Swap)",
            "Skill: Passionate Variation (Swap)",
            "Basic: Impromptu Show 1 2 (Swap)",
            "Basic: Impromptu Show 4 (Swap)"
        ]


    def can_use_move(self, move_name, resources, history, global_history = None):
        # Block all dodge moves
        if "Dodge" in move_name:
            return False, "Dodge moves are disabled"

         
        if "Counter" in move_name:
            return False, "Counter moves are disabled"

        if move_name not in self.moves:
            return False, "Unknown move"

        move = self.moves[move_name]
        for res in ["Forte", "Resonance", "Concerto"]:
            cost = move.get(res, 0) or 0
            if cost < 0 and resources[res] < abs(cost):
                return False, f"Not enough {res}"

        return True, "move allowed"


    def process_move_effects(self, move_name, current_frame, last_action=None):
        super().process_move_effects(move_name, current_frame)

        if move_name == "Liberation: Violent Finale":
            self.cord_attack_ready = True

        if move_name == "Liberation: Marcato":
            buff_name = "Marcato Stack"
            base_buff = {"Fusion DMG": 1.5}

            if buff_name in self.active_buffs:
                current_stacks = self.active_buffs[buff_name]["stacks"]
                if current_stacks < 50:
                    # print(f"[DEBUG] {self.name} had {current_stacks} Marcato stacks — adding 1 more")
                    self.add_buff(
                        buff_name,
                        buff_stats=base_buff,
                        duration_frames=None,
                        current_frame=current_frame,
                        max_stacks=50,
                        stacks_to_add=1
                    )
            else:
                # print(f"[DEBUG] {self.name} starting Marcato stacks with 1")
                self.add_buff(
                    buff_name,
                    buff_stats=base_buff,
                    duration_frames=None,
                    current_frame=current_frame,
                    max_stacks=50,
                    stacks_to_add=1
                )

        if "Passionate Variation" in move_name:
            # print(f"[DEBUG] {self.name} triggered Passionate Variation at frame {current_frame} — adding Draconic Boost")
            self.add_buff(
                buff_name="Draconic Boost",
                buff_stats={"Skill Bon": 25.0},
                duration_frames=480,  # 8 seconds * 60fps
                current_frame=current_frame
            )

        if "Outro: Rage Transportation" in move_name:
            # print(f"[DEBUG - {self.name}] Queuing Heavy Amp buff due to Outro Skill")
            self.queued_buff = {
                "buff_name": "Mortefi Outro Heavy Amp",
                "stats": {"Heavy Amp": 38.0},
                "duration_frames": 840,  # 14 seconds
                "scope": "next"
            }
      


    def trigger_cord_attack(self, total_hits_to_trigger, current_frame):
        if not self.cord_attack_ready or total_hits_to_trigger <= 0:
            return

        frame_gap = 3  # time between hits (can adjust later if needed)
        for i in range(total_hits_to_trigger):
            frame_for_hit = current_frame + (i * frame_gap)
            
            if hasattr(self, "_use_move_fn"):
                unit_key = getattr(self, "internal_name", self.name)

                dmg, success, _, _ = self._use_move_fn(
                    "Liberation: Marcato", unit_override=unit_key, bypass_cooldown=True
                )

                # if success:
                #     print(f"[CORD ATTACK] {self.name} dealt {dmg} at frame {frame_for_hit}")
                # else:
                #     print(f"[DEBUG] Cord attack failed — use_move returned {success}")
            else:
                print(f"[DEBUG] _use_move_fn is NOT bound.")

        self.last_cord_attack_frame = current_frame



    def bind_use_move(self, use_move_fn):
        self._use_move_fn = use_move_fn


    Mortefi_Buffs = [
    {
        "buff_name": "Marcato Stack",
        "trigger": "Liberation: Marcato",
        "stats": {"Fusion DMG": 1.5},
        "duration_frames": None,
        "scope": "self",
        "max_stacks": 50
    },
    {
        "buff_name": "Draconic Boost",
        "trigger": "Skill: Passionate Variation",
        "stats": {"Skill Bon": 25.0},
        "duration_frames": 480,  # 8s
        "scope": "self",
        "max_stacks": 1
    },
    {
        "buff_name": "Mortefi Outro Heavy Amp",
        "trigger": "Outro: Rage Transportation",
        "stats": {"Heavy Amp": 38.0},
        "duration_frames": 840,  # 14s
        "scope": "next",
        "max_stacks": 1
    }
]
