class Weapon:
    def __init__(self, name, main_stat, sub_stats=None):
        self.name = name
        self.main_stat = main_stat
        self.sub_stats = sub_stats or {}
        self.active_buffs = {}
        self.queued_buff = None
        self.pending_buff = None
        self.stats = {}  # optional, mirrors resonator stats if needed

    def equip_to(self, resonator):
        return resonator

    def add_buff(self, buff_name, buff_stats, duration_frames=None, current_frame=0, max_stacks=1, stacks_to_add=1):
        """Works exactly like Resonator.add_buff, with expire_frame, stacks, base_stats, and stats."""
        if buff_name in self.active_buffs:
            existing_buff = self.active_buffs[buff_name]
            old_stacks = existing_buff['stacks']
            new_stacks = min(old_stacks + stacks_to_add, max_stacks)

            base_stats = existing_buff.get('base_stats', buff_stats)
            refreshed_stats = {k: v * new_stacks for k, v in base_stats.items()}

            # Remove old stats
            for stat, val in existing_buff['stats'].items():
                self.stats[stat] = self.stats.get(stat, 0) - val

            # Apply new stats
            for stat, val in refreshed_stats.items():
                self.stats[stat] = self.stats.get(stat, 0) + val

            existing_buff.update({
                'stats': refreshed_stats,
                'stacks': new_stacks,
                'expire_frame': current_frame + duration_frames if duration_frames else None
            })

        else:
            scaled_stats = {k: v * stacks_to_add for k, v in buff_stats.items()}
            self.active_buffs[buff_name] = {
                'stats': scaled_stats,
                'base_stats': buff_stats,
                'expire_frame': current_frame + duration_frames if duration_frames else None,
                'stacks': stacks_to_add
            }
            for stat, val in scaled_stats.items():
                self.stats[stat] = self.stats.get(stat, 0) + val

    def remove_buff(self, buff_name, stacks_to_remove=1, current_frame=0):
        """Works like Resonator.remove_buff, scales stats, handles stacks, deletes if depleted."""
        if buff_name in self.active_buffs:
            buff = self.active_buffs[buff_name]
            current_stacks = buff.get('stacks', 1)

            if current_stacks > stacks_to_remove:
                # Reverse current stats first
                for stat, val in buff['stats'].items():
                    self.stats[stat] = self.stats.get(stat, 0) - val

                # Reduce stacks
                new_stack_count = current_stacks - stacks_to_remove
                buff['stacks'] = new_stack_count
                buff['stats'] = {k: v * new_stack_count for k, v in buff['base_stats'].items()}

                # Re-apply new scaled stats
                for stat, val in buff['stats'].items():
                    self.stats[stat] = self.stats.get(stat, 0) + val
            else:
                # Reverse full effect
                for stat, val in buff['stats'].items():
                    self.stats[stat] = self.stats.get(stat, 0) - val
                del self.active_buffs[buff_name]

    def get_all_stacks(self):
        return {buff_name: buff.get("stacks", 0) for buff_name, buff in self.active_buffs.items()}

    def reset(self):
        self.active_buffs.clear()
        self.stats.clear()

    def queue_to_pending(self):
        if self.queued_buff:
            self.pending_buff = self.queued_buff.copy()
            self.queued_buff = None
