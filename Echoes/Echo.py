class EchoSet:
    def __init__(self, name, equipped_count, max_stacks=1):
        # Initialize the item with a name and equipped count
        self.name = name
        self.equipped_count = equipped_count
        # Initialize an empty dictionary to store active buffs
        self.active_buffs = {}
        self.max_stacks = max_stacks
        self.queued_buff = None
        self.pending_buff = None



    def add_echo_buff(self, buff_name, buff_stats, duration_frames=None, current_frame=0, stacks_to_add=1): # updates active_buffs but in echoclass not resonator
        if buff_name in self.active_buffs:
            existing_buff = self.active_buffs[buff_name]
            old_stacks = existing_buff['stacks']
            new_stacks = min(old_stacks + stacks_to_add, self.max_stacks)

            # Scale from base stats, not compounded stats
            base_stats = existing_buff.get('base_stats', buff_stats)
            refreshed_stats = {k: v * new_stacks for k, v in base_stats.items()}

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

            
    def get_all_stacks(self):
        stacks = {buff_name: buff.get("stacks", 0) for buff_name, buff in self.active_buffs.items()}
        return stacks


    def get_active_echo_bonuses(self):
        total_bonuses = {}
        for buff_data in self.active_buffs.values():
            for stat, value in buff_data.get("stats", {}).items():
                total_bonuses[stat] = total_bonuses.get(stat, 0) + value
        return total_bonuses

    def reset(self):
        self.echo_active = True
        self.echo_timer = 0
        self.active_buffs.clear()
        if hasattr(self, 'resonator_stacks'):
            self.resonator_stacks.clear()


    def queue_to_pending(self):
        if self.queued_buff:
            self.pending_buff = self.queued_buff.copy()
            self.queued_buff = None

  
    