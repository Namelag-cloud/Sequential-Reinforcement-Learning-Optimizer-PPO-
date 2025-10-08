from weapons.baseweapon import Weapon

class StellarSymphony(Weapon):
    def __init__(self):
        super().__init__(
            name="Stellar Symphony",
            main_stat=412,
            sub_stats={
                "HP%": 12.0,
                "ER": 77.0
            }
        )
        self.buff_name = "Stellar Symphony ATK Buff"
        self.buff_duration = 1800  # 30s * 60fps
        self.lib_buff_cd = 1200    # 20s
        self.last_lib_trigger_frame = -self.lib_buff_cd
        self.queued_buff = None  # Buff queued for teamwide delivery

    def process_move_effects(self, current_frame, last_action=None, resonator=None):
        self.check_healing_skill_trigger(last_action, current_frame, resonator)


    def try_restore_concerto(self, current_frame, last_action, owner_name):
        if not isinstance(last_action, dict):
            return 0

        move_name = last_action.get("Skill", "")

        if "Liberation" in move_name:
            diff = current_frame - self.last_lib_trigger_frame
            if diff >= self.lib_buff_cd:
                self.last_lib_trigger_frame = current_frame
                return 8
        return 0


    def check_healing_skill_trigger(self, last_action, current_frame, resonator):
        if not last_action:
            return
        if not isinstance(getattr(resonator, "weapon", None), StellarSymphony):
            return

        if last_action.get("trigger", "") == "Skill" and last_action.get("Healing", False):
            # print(f"[DEBUG - Stellar Symphony] Healing Skill used by {resonator.name} — queuing global ATK buff")
            self.queued_buff = {
                "buff_name": self.buff_name,
                "stats": {"ATK%": 14.0},
                "duration_frames": self.buff_duration,
                "scope": "global"
            }

    def get_active_weapon_buffs(self):
        total_buff_stats = {}
        for name, buff in self.active_buffs.items():
            if name == self.buff_name:
                total_buff_stats["ATK%"] = total_buff_stats.get("ATK%", 0) + 14.0
        return total_buff_stats

    def update_buffs(self, current_frame, resonator):
        buffs_to_remove = []
        for buff_name, buff in self.active_buffs.items():
            if current_frame - buff["start_frame"] >= buff["duration"]:
                buffs_to_remove.append(buff_name)
        for buff_name in buffs_to_remove:
            del self.active_buffs[buff_name]

    StellarSymphony_Buffs = [
        {
            "buff_name": "Stellar Symphony ATK Buff",
            "stat": {"ATK%": 0.14},   # 14% ATK
            "duration": 1800,         # 30s × 60fps
            "scope": "global",        # affects whole team
            "max_stacks": 1
        }
    ]