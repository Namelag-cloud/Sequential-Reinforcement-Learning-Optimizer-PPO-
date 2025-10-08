from json import load 
import json
import math

class Resonator:
    def __init__(self, name, element, base_stats, json_path=None,):
        # Initialize the character with a name, element, base stats, and optional json path
        self.name = name
        self.element = element
        self.moves = {}
        # Create an empty dictionary for moves
        self.base_stats = base_stats
        # Set the base stats to the given base stats
        self.stats = base_stats.copy()
        # Create a copy of the base stats for the current stats
        self.weapon = None
        # Set the weapon to None
        self.weapon_atk = 0
        # Set the weapon attack to 0
        self.json_path = json_path
        # Set the json path to the given json path
        self.active_buffs = {}
        # Create an empty dictionary for active buffs
        self.echo_set = None  
        # Set the echo set to None
        self.main_echo = None
        self.buff_bonus_stats = {}
        # Create an empty dictionary for buff bonus stats
        self.history = []
        self.queued_buff = None

    def equip_echo(self, echo_instance):
        # Assigns the echo_instance to the echo_set attribute
        self.echo_set = echo_instance
        # Calls the apply_2pc method of the echo_instance, passing self as an argument
        echo_instance.apply_2pc(self)
        # Goes to Echo class for 2pc application
        # Calls the apply_5pc method of the echo_instance, passing self as an argument
        echo_instance.apply_5pc(self)
        # Goes to Echo class for 5pc activation

    def get_stat(self, stat_name):
        # Get the total stats of the character
        total_stats = self.get_total_stats()
        # Get the sum of the stat bonuses from all active buffs
        buff_bonus = sum(buff['stats'].get(stat_name, 0) for buff in self.active_buffs.values())
        # Return the total stat value for the given stat name
        return total_stats.get(stat_name, 0)


    def load_moves(self):
        # Check if the json_path attribute is not empty
        if self.json_path:
            # Open the json file in read mode with utf-8 encoding
            with open(self.json_path, "r", encoding="utf-8") as f:
                # Load the json file into a list
                moves_list = json.load(f)
                # Create a dictionary where the key is the Skill and the value is the move
                self.moves = {move["Skill"]: move for move in moves_list}
                
    def equip(self, weapon):
        # Assign the weapon parameter to the weapon attribute of the object
        self.weapon = weapon
        # Call the equip_to method of the weapon object, passing in the object itself
        weapon.equip_to(self)
        # Assign the main_stat attribute of the weapon object to the weapon_atk attribute of the object
        self.weapon_atk = weapon.main_stat

    def buff_value(self, stat_name):
        # Calculate total stat with buffs applied
        final_stats = stat_page(self) #all substats and mainstats with weapon atk


        # Calculate the total buff bonus for the given stat
        buff_bonus = sum(buff['stats'].get(stat_name, 0) for buff in self.active_buffs.values())
        # Store the buff bonus in the buff_bonus_stats dictionary
        self.buff_bonus_stats[stat_name] = buff_bonus #used in calculate_damage function 
        # Return the buff bonus
        return buff_bonus



    def add_buff(self, buff_name, buff_stats, duration_frames=None, current_frame=0, max_stacks=1, stacks_to_add=1):
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


    def get_all_stacks(self):
        stacks = {buff_name: buff.get("stacks", 0) for buff_name, buff in self.active_buffs.items()}
        return stacks

            


    def remove_buff(self, buff_name, stacks_to_remove=1, current_frame=0):
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




    def update_buffs(self, current_frame):
        expired = []
        for name, buff in self.active_buffs.items():
            expire_frame = buff.get('expire_frame')
            if expire_frame is not None and current_frame >= expire_frame:
                expired.append(name)

        for name in expired:
            self.remove_buff(name)



    
    def get_all_active_buffs(self):
        all_buffs = {}

        # Pull EchoSet buffs
        if self.echo_set:
            for name, buff in self.echo_set.active_buffs.items():
                for stat, value in buff['stats'].items():
                    all_buffs[stat] = all_buffs.get(stat, 0) + value

        return all_buffs


    def get_active_resonator_bonuses(self):
        total_bonuses = {}
        for buff_data in self.active_buffs.values():
            for stat, value in buff_data.get("stats", {}).items():
                total_bonuses[stat] = total_bonuses.get(stat, 0) + value
        return total_bonuses


    def reset(self):
        """
        Resets the resonator's state, clears temporary buffs, and re-applies permanent buffs.
        """
        self.history.clear()
        self.buff_bonus_stats.clear()
        self.stats = self.base_stats.copy()  # reset stats to base, before buffs

        # Extract permanent buffs before wiping
        permanent_buffs = {
            name: buff.copy()
            for name, buff in self.active_buffs.items()
            if buff.get("expire_frame") is None or math.isinf(buff.get("expire_frame", 0))
        }   

        # Clear all active buffs
        self.active_buffs.clear()

        # Reapply permanent buffs
        for name, buff in permanent_buffs.items():
            # reset stacks and stats just in case
            self.active_buffs[name] = {
                "stats": buff["stats"].copy(),
                "base_stats": buff["base_stats"].copy(),
                "expire_frame": None,
                "stacks": buff.get("stacks", 1)
            }
            # apply the stats to self.stats
            for stat, val in buff["stats"].items():
                self.stats[stat] = self.stats.get(stat, 0) + val

        # Reset echoes
        if self.echo_set:
            self.echo_set.reset()
            # Reapply any permanent echo buffs if needed
            for name, buff in self.echo_set.active_buffs.items():
                if buff.get("expire_frame") is None or math.isinf(buff.get("expire_frame", 0)):
                    for stat, val in buff["stats"].items():
                        self.stats[stat] = self.stats.get(stat, 0) + val



    def process_move_effects(self, move_name, current_frame):
        # Default resonators do nothing special
        self.update_buffs(current_frame)

    def gain_energy(self, amount):
        if "Energy Recharge" not in self.stats:
            self.stats["Energy Recharge"] = 0
        self.stats["Energy Recharge"] += amount
        # print(f"[DEBUG - {self.name}] Gained {amount} Energy. Current Energy: {self.stats['Energy Recharge']}")

            
        

            