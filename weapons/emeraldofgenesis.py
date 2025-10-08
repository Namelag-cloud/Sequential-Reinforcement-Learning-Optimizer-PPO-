from weapons.baseweapon import Weapon

class EmeraldOfGenesis(Weapon):
    def __init__(self):
        super().__init__(
            name="Emerald of Genesis",
            main_stat=588,
            sub_stats={
                "Crit Rate": 24.3,
                "ER": 16.0
            }
        )

    def check_emerald_passive(self, last_action, current_frame, resonator):
        if not last_action or last_action.get("trigger") != "Skill":
            return

        # Apply Emerald Passive buff to weapon itself
        self.add_buff(
            buff_name="Emerald Passive",
            buff_stats={"ATK%": 6},   # base per stack
            duration_frames=600,
            current_frame=current_frame,
            max_stacks=2,
            stacks_to_add=1
        )

        # Also apply to the resonator
        if resonator:
            resonator.add_buff(
                buff_name="Emerald Passive",
                buff_stats={"ATK%": 6},
                duration_frames=600,
                current_frame=current_frame,
                max_stacks=2,
                stacks_to_add=1
            )

    def update_buffs(self, current_frame, resonator):
        # Remove expired buffs from weapon and propagate removal to resonator
        buffs_to_remove = []
        for buff_name, buff in list(self.active_buffs.items()):
            expire_frame = buff.get("expire_frame")
            if expire_frame is not None and current_frame >= expire_frame:
                buffs_to_remove.append(buff_name)

        for buff_name in buffs_to_remove:
            self.remove_buff(buff_name)
            if resonator:
                resonator.remove_buff(buff_name)

    def get_active_weapon_buffs(self):
        # Return total weapon buffs (sum of all stacks)
        total_buff_stats = {}
        for buff_name, buff in self.active_buffs.items():
            for stat, val in buff.get("stats", {}).items():
                total_buff_stats[stat] = total_buff_stats.get(stat, 0) + val
        return total_buff_stats

    def process_move_effects(self, current_frame, last_action=None, resonator=None):
        # Expire old buffs first
        self.update_buffs(current_frame, resonator)
        # Apply Emerald passive if skill triggered
        self.check_emerald_passive(last_action, current_frame, resonator)

    # Catalog for buff order building (optional reference)
    EmeraldOfGenesis_Buffs = [
        {
            "buff_name": "Emerald Passive",
            "stat": {"ATK%": 6},  # base per stack
            "duration": 600,      # 10s at 60fps
            "scope": "self",
            "max_stacks": 2
        }
    ]
