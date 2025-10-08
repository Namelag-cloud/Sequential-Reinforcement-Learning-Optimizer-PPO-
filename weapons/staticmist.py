from weapons.baseweapon import Weapon

class StaticMist(Weapon):
    def __init__(self):
        super().__init__(
            name="Static Mist",
            main_stat=587,
            sub_stats={
                "Crit Rate": 24.3,
                "ER": 12.8
            }
        )
        self.buff_name = "Static Mist Outro ATK Buff"
        self.buff_duration = 840  # 14 seconds × 60 fps
        self.queued_buff = None

    def check_outro_trigger(self, last_action, current_frame, resonator):
        if not last_action or not resonator:
            return

        # Check if this specific weapon instance is the one equipped on the resonator
        if getattr(resonator, "weapon", None) is not self:
            return

        if last_action.get("trigger") == "Outro":
            # print(f"[DEBUG - Static Mist] Outro triggered by {resonator.name} at frame {current_frame}, queuing buff")
            self.queued_buff = {
                "buff_name": self.buff_name,
                "stats": {"ATK%": 10.0},
                "duration_frames": self.buff_duration,
                "scope": "next"
            }

    def process_move_effects(self, current_frame, last_action=None, resonator=None):
        self.check_outro_trigger(last_action, current_frame, resonator)

    def get_active_weapon_buffs(self):
        return {
            "ATK%": 10.0
        } if self.buff_name in self.active_buffs else {}

    def update_buffs(self, current_frame, resonator):
        buffs_to_remove = []
        for buff_name, buff in self.active_buffs.items():
            if current_frame - buff["start_frame"] >= buff["duration"]:
                buffs_to_remove.append(buff_name)
        for buff_name in buffs_to_remove:
            del self.active_buffs[buff_name]

    
    StaticMist_Buffs = [
        {
            "buff_name": "Static Mist Outro ATK Buff",
            "stat": {"ATK%": 0.10},   # 10% ATK
            "duration": 840,          # 14s × 60fps
            "scope": "next",          # applies to next unit
            "max_stacks": 1
        }
    ]