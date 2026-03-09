from resonators.BaseResonator import Resonator
from resonators.Danjin import Danjin
from Echoes.HavocEclipse import HavocEclipse
from Echoes.HavocEclipse import NightmareCrownless
from weapons.emeraldofgenesis import EmeraldOfGenesis
from simulations.Monkey import Monke
from resonators.Mortefi import Mortefi
from weapons.staticmist import StaticMist
from Echoes.Moonlit import MoonlitClouds
from Echoes.Moonlit import ImpermanenceHeron
from resonators.Shorekeeper import Shorekeeper
from Echoes.RejuvenatingGlow import RejuvenatingGlow
from Echoes.RejuvenatingGlow import FallacyOfNoReturn
from weapons.stellarsymphony import StellarSymphony
import copy
import time
import numpy as np
import torch
from typing import Dict, List
from math import log








substats = {
    "Crit Rate": 8.6, "Crit DMG": 17.08, "HP": 470, "DEF%": 9.9,
    "ATK%": 8.6, "ATK": 50, "HP%": 0.94, "Lib Bon": 8.6,
    "Heavy Bon": 8.6, "Skill Bon": 8.6, "Basic Bon": 8.6, "ER": 10.8,
}

main_stats = {
    "Crit Rate": 22.2, "Crit DMG": 44.4, "Havoc DMG": 30, "Fusion DMG": 30, "Spectro DMG": 30, "Aero DMG": 30, "Glacio DMG": 30, "Electro DMG": 30,
    "ATK%": 18, "ATK": 350, "HP": 4560
}

def get_total_stats(resonator):
    # Copy the resonator's stats
    stats = resonator.stats.copy()
    # Get the resonator's buff bonus stats
    buff_bonus = resonator.buff_bonus_stats
    # Create a dictionary to store the total stats
    total_stats = {}

    # Handle core stats with buffs added
    # Crit Rate
    total_stats["Crit Rate"] = (
        stats.get("Crit Rate", 0)
        + (substats.get("Crit Rate", 0) * 5)
        + buff_bonus.get("Crit Rate", 0)
    )

    # Crit DMG
    total_stats["Crit DMG"] = (
        stats.get("Crit DMG", 0)
        + main_stats.get("Crit DMG", 0)
        + (substats.get("Crit DMG", 0) * 5)
        + buff_bonus.get("Crit DMG", 0)
    )

    # HP
    total_stats["HP"] = (
        stats.get("Char_HP", 0)
        + main_stats.get("HP", 0)
        + substats.get("HP", 0)
        + buff_bonus.get("HP", 0)
    )

    # HP%
    total_stats["HP%"] = (
        stats.get("HP%", 0)
        + substats.get("HP%", 0)
        + buff_bonus.get("HP%", 0)
    )

    # DEF%
    total_stats["DEF%"] = (
        stats.get("DEF%", 0)
        + substats.get("DEF%", 0)
        + buff_bonus.get("DEF%", 0)
    )

    # DEF
    total_stats["DEF"] = (
        stats.get("Char_DEF", 0)
        + buff_bonus.get("DEF", 0)
    )

    # ATK%
    total_stats["ATK%"] = (
        stats.get("ATK%", 0)
        + (main_stats.get("ATK%", 0) * 2)
        + (substats.get("ATK%", 0) * 4)
        + buff_bonus.get("ATK%", 0)
    )

    # ATK
    total_stats["ATK"] = (
        stats.get("ATK", 0)
        + main_stats.get("ATK", 0)
        + (substats.get("ATK", 0) * 3)
        + buff_bonus.get("ATK", 0)
    )
    
    # ER
    total_stats["ER"] = (
        stats.get("ER", 0)
        + substats.get("ER", 0)
        + buff_bonus.get("ER", 0)
    )

    # Element DMG
    element_key = f"{resonator.element} DMG"
    total_stats[element_key] = (
    stats.get(element_key, 0)
    + (main_stats.get(element_key, 0) * 2)
    + buff_bonus.get(element_key, 0)
    )

    total_stats[element_key + " Amp"] = (
        stats.get(element_key + " Amp", 0)
        + buff_bonus.get(element_key + " Amp", 0)
    )

    # Echo Element DMG
    echo_dmg_key = f"{resonator.element} Echo DMG"
    total_stats[echo_dmg_key] = (
        stats.get(echo_dmg_key, 0)
        + (main_stats.get(echo_dmg_key, 0) * 2)
        + buff_bonus.get(echo_dmg_key, 0)
    )

    # All DMG
    total_stats["All DMG"] = (
        stats.get("All DMG", 0)
        + buff_bonus.get("All DMG", 0)
    )

    for key in [
        "Basic Bon", "Heavy Bon", "Skill Bon", "Lib Bon", "Outro Bon",
        "Healing Bonus", "Healing", "Shield Strength", "Heavy Amp", "Skill Amp" , "Lib Amp", "Echo Amp",
            "All Amp", "Outro Amp", "Basic Amp", 
    ]:
        total_stats[key] = (
            substats.get(key, 0)
            + buff_bonus.get(key, 0)
            + stats.get(key, 0)
        )

    # Defensive shredding bonuses
    shred_types = [
        "Gen", "Havoc", "Fusion", "Spectro", "Electro",
        "Glacio", "Aero", "Basic", "Skill", "Lib", "Heavy", "Outro"
    ]
    for shred in shred_types:
        total_stats[f"{shred} Def Shred"] = buff_bonus.get(f"{shred} Def Shred", 0) + stats.get(f"{shred} Def Shred", 0)
        total_stats[f"{shred} Res Shred"] = buff_bonus.get(f"{shred} Res Shred", 0) + stats.get(f"{shred} Res Shred", 0)

   
    return total_stats


def stat_page(resonator):
    # Get the total stats of the resonator
    stats = get_total_stats(resonator)
    # Get all active buffs of the resonator
    buffs = resonator.get_all_active_buffs()  # returns dict {stat: val}
    # Add the buffs to the stats
    for stat, val in buffs.items():
        stats[stat] = stats.get(stat, 0) + val

    # Get the total base attack of the resonator
    total_base_atk = resonator.stats.get("Char_ATK", 0) + resonator.weapon_atk
    # If the resonator has a weapon, add the weapon's sub stats to the stats
    if resonator.weapon:
        for stat, val in resonator.weapon.sub_stats.items():
            stats[stat] = stats.get(stat, 0) + val
    
    
    # Get the total attack percentage of the resonator
    total_atk_per = 1 + stats.get("ATK%", 0) / 100
    # Get the total flat attack of the resonator
    total_flat_atk = stats.get("ATK", 0)
    # Get the total attack of the resonator
    total_atk = total_base_atk * total_atk_per + total_flat_atk

    total_hp = resonator.stats.get("Char_HP", 0) * (1 + stats.get("HP%", 0) / 100) + stats.get("HP", 0)
    total_def = resonator.stats.get("Char_DEF", 0) * (1 + stats.get("DEF%", 0) / 100) + stats.get("DEF", 0)

    result = {
        "Base Stats": {
            "ATK": resonator.stats.get("Char_ATK", 0),
            "HP": resonator.stats.get("Char_HP", 0),
            "DEF": resonator.stats.get("Char_DEF", 0),
        },
        "Final Stats": {
            "Total ATK": round(total_atk, 1),
            "Total HP": round(total_hp, 1),
            "Total DEF": round(total_def, 1),
            "Crit Rate": round(stats.get("Crit Rate", 0), 1),
            "Crit DMG": round(stats.get("Crit DMG", 0), 1),
            "ER": round(stats.get("ER", 0), 1),
            "Havoc DMG": round(stats.get("Havoc DMG", 0), 1),
            "Fusion DMG": round(stats.get("Fusion DMG", 0), 1),
            "Spectro DMG": round(stats.get("Spectro DMG", 0), 1),
            "Electro DMG": round(stats.get("Electro DMG", 0), 1),
            "Glacio DMG": round(stats.get("Glacio DMG", 0), 1),
            "Aero DMG": round(stats.get("Aero DMG", 0), 1),
            f"{resonator.element} Echo DMG": round(stats.get(f"{resonator.element} Echo DMG", 0), 1),
            "All_DMG": round(stats.get("All DMG", 0), 1),
            "Havoc Amp": round(stats.get("Havoc Amp", 0), 1),
            "Fusion Amp": round(stats.get("Fusion Amp", 0), 1),
            "Spectro Amp": round(stats.get("Spectro Amp", 0), 1),
            "Electro Amp": round(stats.get("Electro Amp", 0), 1),
            "Glacio Amp": round(stats.get("Glacio Amp", 0), 1),
            "Aero Amp": round(stats.get("Aero Amp", 0), 1),
            f"{resonator.element} Echo DMG Amp": round(stats.get(f"{resonator.element} Echo DMG Amp", 0), 1),  
            "All Amp": round(stats.get("All Amp", 0), 1),

            "Skill Bon": round(stats.get("Skill Bon", 0), 1),
            "Heavy Bon": round(stats.get("Heavy Bon", 0), 1),
            "Basic Bon": round(stats.get("Basic Bon", 0), 1),
            "Lib Bon": round(stats.get("Lib Bon", 0), 1),
            "Outro Bon": round(stats.get("Outro Bon", 0), 1),
            "Skill Amp": round(stats.get("Skill Amp", 0), 1),
            "Heavy Amp": round(stats.get("Heavy Amp", 0), 1),
            "Basic Amp": round(stats.get("Basic Amp", 0), 1),
            "Lib Amp": round(stats.get("Lib Amp", 0), 1),
            "Outro Amp": round(stats.get("Outro Amp", 0), 1),


            "HP%": round(stats.get("HP%", 0), 1),
            "DEF%": round(stats.get("DEF%", 0), 1),
            "ATK%": round(stats.get("ATK%", 0), 1),
            "ATK": round(stats.get("ATK", 0), 1),
            "HP": round(stats.get("HP", 0), 1),
            "DEF": round(stats.get("DEF", 0), 1),

            # Defensive modifiers
            "Gen_Def Shred": round(stats.get("Gen_Def Shred", 0), 1),
            "Gen_Res Shred": round(stats.get("Gen_Res Shred", 0), 1),

            "Havoc Def Shred": round(stats.get("Havoc Def Shred", 0), 1),
            "Havoc Res Shred": round(stats.get("Havoc Res Shred", 0), 1),

            "Fusion Def Shred": round(stats.get("Fusion Def Shred", 0), 1),
            "Fusion Res Shred": round(stats.get("Fusion Res Shred", 0), 1),

            "Spectro Def Shred": round(stats.get("Spectro Def Shred", 0), 1),
            "Spectro Res Shred": round(stats.get("Spectro Res Shred", 0), 1),

            "Electro Def Shred": round(stats.get("Electro Def Shred", 0), 1),
            "Electro Res Shred": round(stats.get("Electro Res Shred", 0), 1),

            "Glacio Def Shred": round(stats.get("Glacio Def Shred", 0), 1),
            "Glacio Res Shred": round(stats.get("Glacio Res Shred", 0), 1),

            "Aero Def Shred": round(stats.get("Aero Def Shred", 0), 1),
            "Aero Res Shred": round(stats.get("Aero Res Shred", 0), 1),

            "Basic Def Shred": round(stats.get("Basic Def Shred", 0), 1),
            "Basic Res Shred": round(stats.get("Basic Res Shred", 0), 1),

            "Skill Def Shred": round(stats.get("Skill Def Shred", 0), 1),
            "Skill Res Shred": round(stats.get("Skill Res Shred", 0), 1),

            "Lib Def Shred": round(stats.get("Lib Def Shred", 0), 1),
            "Lib Res Shred": round(stats.get("Lib Res Shred", 0), 1),

            "Heavy Def Shred": round(stats.get("Heavy Def Shred", 0), 1),
            "Heavy Res Shred": round(stats.get("Heavy Res Shred", 0), 1),

            "Outro Def Shred": round(stats.get("Outro Def Shred", 0), 1),
            "Outro Res Shred": round(stats.get("Outro Res Shred", 0), 1),

            # Healing & Utility
            "Healing Bonus": round(stats.get("Healing Bonus", 0), 1),
            "Healing": round(stats.get("Healing", 0), 1),
            "Shield Strength": round(stats.get("Shield Strength", 0), 1),
        }
    }
    
    # print(result)
    return result


def calculate_damage(resonator, stats, enemy):
    final_stats = stats["Final Stats"]
    element_key = f"{resonator.element} DMG"
    elemental_dmg = final_stats.get(element_key, 0)

    damage_results = {}

    for move_data in resonator.moves.values():
        move_name = move_data.get("Skill", "Unknown Skill")
        dmg_info = move_data.get("DMG %", {})

        # Determine scaler and percent
        if isinstance(dmg_info, dict) and len(dmg_info) == 1:
            scaler_type, percent_str = list(dmg_info.items())[0]
            if isinstance(percent_str, str) and percent_str.endswith('%'):
                dmg_percent = float(percent_str.strip('%')) / 100
            else:
                dmg_percent = float(percent_str)
        else:
            # fallback: treat as old-style float or string
            scaler_type = "ATK"
            if isinstance(dmg_info, str) and dmg_info.endswith('%'):
                dmg_percent = float(dmg_info.strip('%')) / 100
            else:
                dmg_percent = float(dmg_info)

        # Choose the correct base stat to scale from
        if scaler_type.upper() == "HP":
            base_stat = final_stats.get("Total HP", 0)
        else:
            base_stat = final_stats.get("Total ATK", 0)

        # Apply base scaling
        dmg = base_stat * dmg_percent

        # Bonus damage %
        trigger_type = move_data.get("Trigger", "").strip()
        specific_bonus = final_stats.get(f"{trigger_type} Bon", 0)
        specific_amp = final_stats.get(f"{trigger_type} Amp", 0)
        element_amp = final_stats.get(f"{element_key} Amp", 0)
        all_amp = final_stats.get("All Amp", 0)
        all_dmg_bonus = final_stats.get("All_DMG", 0)

        # Echo-specific modifiers
        is_echo = move_name.lower().startswith("echo") 
        echo_bonus = 0
        echo_amp = 0
        if is_echo:
            element_echo_key = f"{resonator.element} Echo DMG"
            element_echo_amp_key = f"{resonator.element} Echo Amp"
            echo_bonus = final_stats.get(element_echo_key, 0)
            echo_amp = final_stats.get(element_echo_amp_key, 0)

        # Apply additive % damage bonuses
        total_bonus = all_dmg_bonus + elemental_dmg + specific_bonus
        if is_echo:
            total_bonus += echo_bonus
        dmg *= (1 + total_bonus / 100)

        # Apply average crit multiplier
        crit_rate = final_stats.get("Crit Rate", 0) / 100
        crit_dmg = final_stats.get("Crit DMG", 0) / 100
        avg_crit_multiplier = 1 + crit_rate * (crit_dmg - 1)
        dmg *= avg_crit_multiplier

        # Defense & resistance modifiers
        dmg *= enemy.defense_mod / 100
        dmg *= enemy.resistance_mod / 100

        # Amplification effects
        total_amp = all_amp + specific_amp + element_amp
        if is_echo:
            total_amp += echo_amp
        dmg *= (1 + total_amp / 100)

        damage_results[move_name] = int(round(dmg))

    return damage_results

import math
import time 

class ActionTracker:
    def __init__(self, move_data, resonator1, resonator2=None, resonator3=None, echo=None, stats=None, enemy=None):
        self.best_time = float("inf")
        self.current_state = "GR"
        self.last_forced_swap_move = None

        self.last_swap = {
            "unit_name": None,
            "frame": -9999  # some far back frame
        }
        self.swap_cd_frames = 60  # 1 sec
        
        self.resonator1 = resonator1
        self.resonator2 = resonator2
        self.resonator3 = resonator3
        self.active_unit = "resonator1"
        self.pending_transferred_buffs = {}  # Echo set name to buff dict

        self.resonator_map = {
            "resonator1": self.resonator1,
            "resonator2": self.resonator2,
            "resonator3": self.resonator3,
        }

        self.team = {}
        for slot, unit in self.resonator_map.items():
            if unit is not None:
                # Set internal name directly during team creation
                unit.internal_name = slot

                # Bind use_move automatically if method exists
                if hasattr(unit, "bind_use_move"):
                    unit.bind_use_move(self.use_move)

                self.team[slot] = {
                    "unit": unit,
                    "weapon": getattr(unit, "weapon", None),
                    "echo": echo
                }

        self.cord_attack_units = {}
        for slot_name, data in self.team.items():
            unit = data["unit"]
            if hasattr(unit, "trigger_cord_attack") and hasattr(unit, "cord_attack_cooldown_frames"):
                self.cord_attack_units[slot_name] = {
                    "unit": unit,
                    "ready": False,
                    "last_frame": -9999,
                    "cd_frames": unit.cord_attack_cooldown_frames
                }

        self.moves = {move.get("Skill", "Unknown Skill"): move for move in move_data.values()}
        self.history = {k: [] for k in self.resonator_map}
        self.global_history = []
        self.resources = {
            k: {"Forte": 0, "Resonance": 250, "Concerto": 0, "Time": 0}
            for k in self.resonator_map
        }
        

        self.resource_caps = {
            "Resonance": 300,
            "Concerto": 100,
            "Forte": 41.0,
            "Time": float("inf"),
        }

        self.current_time_frame = 0
        self.echo = echo
        self.echo_active = False
        self.echo_timer = 0
        self.stats = stats
        self.enemy = enemy
        self.damage_log = []
        self.sim_cache = SimCache
        self.execution_stage = 0

        self.rl_index_to_name = {}
        self.rl_name_to_index = {}

        for unit_slot, (unit_name, unit_data) in enumerate(self.team.items()):
            base = unit_slot * 100
            moves = list(unit_data["unit"].moves.values())

            for offset, m in enumerate(moves):
                idx = base + offset
                name = m["Skill"]
                self.rl_index_to_name[idx] = name
                self.rl_name_to_index[name] = idx

            # Fill with PAD
            for offset in range(len(moves), 100):
                idx = base + offset
                self.rl_index_to_name[idx] = "PAD"



        mvps_list = []
        for m in self.moves.values():
            dmg_data = m.get("DMG %")
            time = m.get("Time", 1.0)

            if not dmg_data or not time:
                continue

            if isinstance(dmg_data, dict):
                if len(dmg_data) != 1:
                    print(f"[WARN] Unexpected DMG % format: {dmg_data}")
                    continue
                scale_type, value_str = list(dmg_data.items())[0]
                dmg_pct = float(value_str.strip('%'))
            elif isinstance(dmg_data, str):
                dmg_pct = float(dmg_data.strip('%'))
            else:
                dmg_pct = float(dmg_data)

            if "Skill" not in m:
                print("[WARN] Missing 'Skill' key in move:", m)
                continue

            mvps = dmg_pct / (time + 1e-6)
            mvps_list.append((m["Skill"], mvps))

        self.avg_mvps = sum(v for _, v in mvps_list) / len(mvps_list) if mvps_list else 0
        self.top_mvps_skill = max(mvps_list, key=lambda x: x[1])[0] if mvps_list else None
        self.last_setup_move_index = None
        self.best_sequence = []
        self.best_damage = 0
        self.episode_best_sequences = []
        self.total_episode_reward = 0
        self.liberation_windows = {}
        self.move_queue = []
        self.cooldowns = {}  # {unit_name: {move_name: cd_end_frame}}
        for unit_name, data in self.team.items():
            unit = data["unit"]
            self.cooldowns[unit_name] = {}
            for move_name, move_data in unit.moves.items():
                base_name = move_name.split(" (")[0]
                # initially all available, cd_end = 0
                if move_data.get("Cooldown", 0) > 0:
                    self.cooldowns[unit_name][base_name] = 0


    def get_valid_action_mask(self):
        total_mask_size = len(self.rl_index_to_name)
        mask = np.zeros(total_mask_size, dtype=bool)

        # --- Allowed units (active + swappable) ---
        allowed_units = {self.active_unit}
        for other_unit_name in self.team.keys():
            if other_unit_name != self.active_unit and self.can_swap_to(other_unit_name):
                allowed_units.add(other_unit_name)

        # --- Unit/move restrictions ---
        units_to_mask = set()
        swap_conditional_masked_moves = set()

        # Block moves from a unit if a forced-swap move was used
        if getattr(self, "last_forced_swap_move", None):
            move_owner = self.get_move_owner(self.last_forced_swap_move)
            if move_owner:
                units_to_mask.add(move_owner)

        # Block other swap-conditional moves from same unit if one was already used
        for unit_name, unit_data in self.team.items():
            unit = unit_data["unit"]
            if getattr(self, f"{unit_name}_swap_conditional_used", False):
                swap_conditional_masked_moves.update(getattr(unit, "swap_conditional_moves", []))

        debug_mask = []

        # --- Build mask ---
        for idx, move_name in self.rl_index_to_name.items():
            # Hard-banned moves
            if move_name in {"PAD", "Liberation: Marcato"}:
                continue

            owner_name = self.get_move_owner(move_name)
            if owner_name is None or owner_name not in allowed_units:
                continue

            unit = self.team[owner_name]["unit"]

            # Ban intros/outros
            if move_name.startswith("Intro") or move_name.startswith("Outro"):
                continue

            # Mask entire unit if forced-swap is active
            if owner_name in units_to_mask:
                mask[idx] = False
                debug_mask.append((idx, move_name, False))
                continue

            # Mask other swap-conditional moves if already used
            if move_name in swap_conditional_masked_moves:
                mask[idx] = False
                debug_mask.append((idx, move_name, False))
                continue

            # Mask if swap-conditional but not active
            if move_name in getattr(unit, "swap_conditional_moves", []):
                if owner_name == self.active_unit and not getattr(self, f"{owner_name}_swap_conditional_active", False):
                    mask[idx] = False
                    debug_mask.append((idx, move_name, False))
                    continue

            # Final legality check
            allowed, _ = self.can_use_move(move_name, unit_override=owner_name, source="mask")

            # Mask if on cooldown
            if allowed and self.is_on_cooldown(move_name, unit_override=owner_name):
                allowed = False

            mask[idx] = allowed
            debug_mask.append((idx, move_name, allowed))

        # Debug print
        # print("\n[MASK DEBUG]")
        # for idx, move_name, allowed in debug_mask:
        #     print(f"  idx={idx:<2} | {move_name:<35} | allowed={allowed}")

        return mask



    def perform_move(self, move_ref, unit_override=None, bypass_cooldown=False):
        """
        Execute a move. move_ref can be a move name (str) or move Index (int)
        """
        if isinstance(move_ref, int):
            move = next((m for m in self.moves.values() if m.get("Index") == move_ref), None)
            if not move:
                return 0, False, None, None
            move_name = move["Skill"]
        else:
            move_name = move_ref
            if move_name not in self.moves:
                return 0, False, None, None

        # Step 1: Execute the move (handles swaps and active_unit updates)
        result = self.use_move(move_name, unit_override=unit_override, bypass_cooldown=bypass_cooldown)

        # Step 2: Determine actual unit
        unit_name = unit_override or self.active_unit
        unit = self.team[unit_name]["unit"]

        # Step 3: Mark swap-conditional moves
        if move_name in getattr(unit, "swap_conditional_moves", []):
            setattr(self, f"{unit_name}_swap_conditional_used", True)

        # Step 4: Record forced-swap move
        if move_name in getattr(unit, "forced_swap_moves", []):
            self.last_forced_swap_move = move_name

        # Step 5: Clear swap flags for other units if swapped
        for other_unit_name in self.team.keys():
            if other_unit_name != self.active_unit:
                # Swap-conditional reset for the unit that is swapped out
                setattr(self, f"{other_unit_name}_swap_conditional_used", False)
                # If forced-swap was on the swapped-out unit, clear it
                if self.last_forced_swap_move and self.get_move_owner(self.last_forced_swap_move) == other_unit_name:
                    self.last_forced_swap_move = None

        return result

    


    def get_move_owner(self, move_name):
        for uname, udata in self.team.items():
            unit = udata["unit"]
            if move_name in getattr(unit, "moves", {}):
                return uname
        return None


    def queue_move(self, move_name, unit_override=None, bypass_cooldown=False):
        if not hasattr(self, 'move_queue'):
            self.move_queue = []
        
        # Append to queue (if you want to keep the queue for flow/order)
        self.move_queue.append({
            "move_name": move_name,
            "unit_override": unit_override,
            "bypass_cooldown": bypass_cooldown
        })
        
        # Immediately perform the move and apply damage
        dmg, success, before_stats, after_stats = self.use_move(
            move_name,
            unit_override=unit_override,
            bypass_cooldown=bypass_cooldown
        )
        
        return dmg, success

    def get_outro_move(self, unit_name):
        unit_data = self.team.get(unit_name)
        if not unit_data:
            return None
        unit = unit_data.get("unit")
        for move_name, move_data in unit.moves.items():
            if move_data.get("Trigger") == "Outro":
                return move_name
        return None

    def get_intro_move(self, unit_name):
        unit_data = self.team.get(unit_name)
        if not unit_data:
            return None
        unit = unit_data.get("unit")
        for move_name, move_data in unit.moves.items():
            if move_data.get("Trigger") == "Intro":
                return move_name
        return None

    def swap_unit(self, new_unit_name, move_name=None): # temp move_name fallback param, have to remove entirely at some point
        if not self.can_swap_to(new_unit_name):
            print(f"[SWAP BLOCKED] Can't swap back to {new_unit_name} yet. Swap cooldown in effect.")
            return False

        current_frame = self.current_time_frame
        old_unit = self.active_unit
        self.last_swap = {
            "unit_name": old_unit,
            "frame": current_frame
        }


        # --- Buff cleanup: remove "Amp" buffs except Stellarealm Amp ---
        old_unit_obj = self.team[old_unit]["unit"]
        for buff_name in list(old_unit_obj.active_buffs.keys()):
            if "Amp" in buff_name and buff_name != "Stellarealm Amp":
                old_unit_obj.remove_buff(buff_name, stacks_to_remove=9999, current_frame=current_frame)
                # print(f"[BUFF REMOVED] {buff_name} from {old_unit} on swap")

        # Pull Concerto directly from the old unit's resources
        concerto_value = self.resources[old_unit]["Concerto"]

        # Outro/Intro logic if Concerto is full
        if concerto_value >= self.resource_caps.get("Concerto", 100):
            outro_move = self.get_outro_move(old_unit)
            if outro_move:
                self.queue_move(outro_move, unit_override=old_unit, bypass_cooldown=True)
                # print(f"[OUTRO] Queued outro for {old_unit}: {outro_move}")

        self.active_unit = new_unit_name

        if concerto_value >= self.resource_caps.get("Concerto", 100):
            intro_move = self.get_intro_move(new_unit_name)
            unit_obj = self.team[new_unit_name]["unit"]

            # Conditional override for Shorekeeper
            if (new_unit_name == "resonator3" and 
                intro_move == "Intro: Enlightenment" and
                getattr(unit_obj, "discernment_available", False)):  # only override if flag is True
                intro_move = "Intro 2: Discernment"

            if intro_move:
                self.queue_move(intro_move, unit_override=new_unit_name, bypass_cooldown=True)
                # print(f"[INTRO] Queued intro for {new_unit_name}: {intro_move}")

            
        return True



    def can_swap_to(self, new_unit_name):

        if new_unit_name != self.last_swap["unit_name"]:
            return True

        frames_since = self.current_time_frame - self.last_swap["frame"]
        return frames_since >= self.swap_cd_frames



    def _execute_move(self, move_name, unit_name, bypass_cooldown=False):
        unit_data = self.team.get(unit_name)
        if not unit_data:
            return 0, False, {}, {}

        unit = unit_data.get("unit")
        stats = self.stats.get(unit_name)
        enemy = self.enemy

        move = unit.moves.get(move_name, {})
        move_duration = move.get("Time", 0)
        index = move.get("Index")

        # Snapshot before stats
        before_stats = stat_page(unit)

        # Condition 1: move not in unit.moves
        if move_name not in unit.moves:
            print(f"[BLOCKED] {move_name} not in {unit_name}'s moves")
            return 0, False, before_stats, before_stats

        # Condition 2: move is on cooldown (and we’re not bypassing)
        if not bypass_cooldown and self.is_on_cooldown(move_name, unit_name):
            print(f"[BLOCKED] {move_name} is on cooldown for {unit_name}")
            return 0, False, before_stats, before_stats

        can_use, reason = self.can_use_move(move_name, unit_override=unit_name)
        if not can_use:
            print(f"[USE_MOVE] {move_name} was rejected for {unit_name}: {reason}")
            return 0, False, before_stats, before_stats

        self.current_time_frame += int(move_duration * 60)
        current_frame = self.current_time_frame

        self.history[unit_name].append((move_name, current_frame, index))
        self.global_history.append((unit_name, move_name, current_frame, index))
        unit.history = self.history[unit_name]
        last_action = self.get_last_action()
        
        # Apply pending buffs 
        for buff_name, buff in list(self.pending_transferred_buffs.items()):
            scope = buff.get("scope", "next")

            if scope == "global":
                for teammate_data in self.team.values():
                    target_unit = teammate_data.get("unit")
                    if target_unit:
                        target_unit.add_buff(
                            buff["buff_name"],
                            buff["stats"],
                            duration_frames=buff["duration_frames"],
                            current_frame=self.current_time_frame
                        )
                        

            elif scope == "next":
                if unit:
                    unit.add_buff(
                        buff["buff_name"],
                        buff["stats"],
                        duration_frames=buff["duration_frames"],
                        current_frame=self.current_time_frame
                    )
                  

            # Remove from pending after applying
            self.pending_transferred_buffs.pop(buff_name)

        # === Teamwide Reactive Layer ===
        active_unit = self.resonator_map[self.active_unit]
        active_weapon = getattr(active_unit, "weapon", None)
        active_echo = getattr(active_unit, "echo_set", None)

        # === Heron Outro Check ===
        trigger = move.get("Trigger", "")
        if trigger == "Outro" and hasattr(active_unit, "heron_echo_instance"):
            active_unit.heron_echo_instance.on_outro(active_unit, self.current_time_frame)


        # Let active unit respond to the move they just did
        if active_unit:
            active_unit.process_move_effects(move_name, current_frame)

        # Weapon effects — only for active unit
        if active_weapon:
            active_weapon.process_move_effects(current_frame, last_action, active_unit)

        # Echo reaction — only if echo set matches and conditions met
        if active_echo:
            active_echo.check_activation(last_action, current_frame, active_unit)


        # === Passive reactions from teammates (if any needed later) ===
        for teammate_name, teammate_data in self.team.items():
            teammate_unit = teammate_data.get("unit")

            # Only process teammates other than active unit
            if teammate_unit and teammate_unit != active_unit:
                teammate_unit.process_move_effects(move_name, current_frame)

        # === Echo special handling === gotta encapsulate this sometime
        if move_name.startswith("Echo") and hasattr(unit, "main_echo"):
            used = unit.main_echo.use(unit, current_frame)  # returns True/False if bonus applies

            # Calculate Echo damage externally
            damage_output = calculate_damage(unit, stat_page(unit), enemy)
            dmg = damage_output.get(unit.main_echo.move_name, 0)


            after_stats = stat_page(unit)
            return dmg, True, before_stats, after_stats



        # === Standard Move ===

        # Resource Gain
        for res in ["Forte", "Resonance", "Concerto", "Time"]:
            gain = move.get(res, 0) or 0
            self.resources[unit_name][res] += gain
            cap = self.resource_caps.get(res, float("inf"))
            self.resources[unit_name][res] = min(max(self.resources[unit_name][res], 0), cap)        

        # Process any additional effects (weapons, echoes, buffs, etc.)
        self.process_move_effects(self.current_time_frame, move, unit_name)
       

        # Forte dump reset
        if "Forte" in move_name:
            self.resources[unit_name]["Forte"] = 0

        # Cooldown Application
        # After the move is successfully performed
        base_name = move_name.split(" (")[0]
        duration = self.resonator_map[unit_name].moves.get(move_name, {}).get("Cooldown", 0)
        if duration > 0:
            self.cooldowns[unit_name][base_name] = self.current_time_frame + int(duration * 60)



        if "Liberation" in move_name:
            self.liberation_windows[unit_name] = {
                "start": current_frame,
                "end": current_frame + int(move_duration * 60)
            }


        # Update stats and damage calc
        self.stats[unit_name] = stat_page(unit)
        after_stats = self.stats[unit_name]

        dmg = 0
        if move_name != "Echo" and unit and enemy:
            damage_output = calculate_damage(unit, self.stats[unit_name], enemy)
            if move_name in damage_output:
                dmg = damage_output[move_name]
                self.damage_log.append({
                    "unit": unit_name,
                    "move": move_name,
                    "frame": current_frame,
                    "damage": dmg
                })
                enemy.take_damage(dmg)

        return dmg, True, before_stats, after_stats

    
    def process_move_effects(self, current_frame, last_action, unit_name):
        unit = self.team[unit_name]["unit"]
        # --- Weapon effects ---
        weapon = getattr(unit, "weapon", None)
        if weapon and hasattr(weapon, "try_restore_concerto"):
            restore = weapon.try_restore_concerto(current_frame, last_action, unit_name)

            if restore > 0:
                before_val = self.resources[unit_name]["Concerto"]
                self.resources[unit_name]["Concerto"] += restore
                cap = self.resource_caps.get("Concerto", float("inf"))
                self.resources[unit_name]["Concerto"] = min(self.resources[unit_name]["Concerto"], cap)
                after_val = self.resources[unit_name]["Concerto"]





    def use_move(self, move_name, return_stats=False, unit_override=None, bypass_cooldown = False):

        if unit_override is None:
            move_owner = self.get_move_owner(move_name)
            if move_owner and move_owner != self.active_unit:
                swapped = self.swap_unit(move_owner)
                if not swapped:
                    if return_stats:
                        return 0, False, {}, {}
                    return 0, False, {}, {}

        unit_name = unit_override or self.active_unit
        unit_data = self.team.get(unit_name)
        # print("Move name is", move_name)


        if not unit_data:
            print(f"[ERROR] Unit '{unit_name}' not found in team. Available keys: {list(self.team.keys())}")
            if return_stats:
                return 0, False, {}, {}
            return 0, False, {}, {}

        unit = unit_data.get("unit")
        move = unit.moves.get(move_name, {})
        move_duration = move.get("Time", 0)


        # Update echo timer
        self.update_echo(move_duration)

        # === Execute main move ===
        dmg, success, before_stats, after_stats = self._execute_move(move_name, unit_name, bypass_cooldown=bypass_cooldown)
        # if not success:
        #     print(f"[DEBUG] _execute_move failed for {unit_name} using {move_name} at frame {self.current_time_frame}")

        # === Cord Attack Trigger ===
        trigger = move.get("Trigger", "")
        if trigger in ["Basic", "Heavy"]:
            move_hits = move.get("Hits", 1)
            move_duration_sec = move_duration  # Already in seconds

            for slot_name, data in self.cord_attack_units.items():
                cord_unit = data["unit"]
                cord_move = data.get("move_name", "Liberation: Marcato")
                cd_frames = data.get("cd_frames", 0)

                # Cap the number of cord hits
                max_possible_cord_hits = min(move_hits, math.floor(move_hits / move_duration_sec)) if move_duration_sec > 0 else move_hits
                if trigger == "Heavy":
                    max_possible_cord_hits *= 2

                if not getattr(cord_unit, "cord_attack_ready", False):
                    continue

                # Apply cooldown logic — only count as many cord hits as fit in time since last_frame
                last_frame = data.get("last_frame", 0)
                elapsed_frames = self.current_time_frame - last_frame
                max_hits_due_to_cd = elapsed_frames // cd_frames if cd_frames > 0 else max_possible_cord_hits

                total_triggers = min(max_possible_cord_hits, max_hits_due_to_cd)

                if total_triggers > 0 and hasattr(cord_unit, "trigger_cord_attack"):
                    # print(f"[DEBUG] Triggering {total_triggers} cord hits from {cord_unit.name}")
                    cord_unit.trigger_cord_attack(total_triggers, self.current_time_frame)
                    data["last_frame"] = self.current_time_frame
                # print(f"[CORD LOGIC] {cord_unit.name} for move '{move_name}' — move_hits={move_hits}, move_duration={move_duration_sec}s, cd={cd_frames}f, last_frame={last_frame}, current_frame={self.current_time_frame}, total_triggers={total_triggers}")



        # === Store buffs from all team members ===
        for name, data in self.team.items():
            unit = data["unit"]

            # Echo Buff
            echo_set = getattr(unit, "echo_set", None)
            if echo_set and getattr(echo_set, "queued_buff", None):
                buff = echo_set.queued_buff
                buff_name = buff.get("buff_name", f"Unnamed Echo Buff ({unit.name})")
                buff["source_move"] = move_name
                buff["source_frame"] = self.current_time_frame
                self.pending_transferred_buffs[buff_name] = buff
                echo_set.queued_buff = None
            
            # Main cost Buff
            main_echo = getattr(unit, "main_echo", None)
            if main_echo and getattr(main_echo, "queued_buff", None):
                buff = main_echo.queued_buff
                buff_name = buff.get("buff_name", f"Unnamed Main Cost Buff ({unit.name})")
                buff["source_move"] = move_name
                buff["source_frame"] = self.current_time_frame
                self.pending_transferred_buffs[buff_name] = buff
                main_echo.queued_buff = None

            # Weapon Buff
            weapon = getattr(unit, "weapon", None)
            if weapon and getattr(weapon, "queued_buff", None):
                buff = weapon.queued_buff
                buff_name = buff.get("buff_name", f"Unnamed Weapon Buff ({unit.name})")
                buff["source_move"] = move_name
                buff["source_frame"] = self.current_time_frame
                self.pending_transferred_buffs[buff_name] = buff
                weapon.queued_buff = None

            # Unit Buff
            if getattr(unit, "queued_buff", None):
                buff = unit.queued_buff
                buff_name = buff.get("buff_name", f"Unnamed Unit Buff ({unit.name})")
                buff["source_move"] = move_name
                buff["source_frame"] = self.current_time_frame
                self.pending_transferred_buffs[buff_name] = buff
                unit.queued_buff = None


        # print(dmg)
        self.current_state = move.get("End")
        return dmg, success, before_stats, after_stats




    def estimate_buff_impact(self, unit_name, before_stats, after_stats, damage, move_name):
        deltas = {}
        slopes = {}
        active_buff_contribs = {}

        unit = self.team[unit_name]["unit"]

        # --- 1. Reward for queued (pending) buffs directly ---
        for buff_name, buff in list(self.pending_transferred_buffs.items()):
            if buff.get("source_move") == move_name:
                # Flat reward of 2.5 for queuing buffs
                active_buff_contribs[move_name] = active_buff_contribs.get(move_name, 0) + 2.5

        # --- 2. Handle stat deltas for active buffs ---
        for top_key in before_stats:
            before_nested = before_stats[top_key]
            after_nested = after_stats[top_key]

            for stat_key, b_val in before_nested.items():
                a_val = after_nested.get(stat_key, 0)
                if isinstance(b_val, (int, float)) and isinstance(a_val, (int, float)):
                    delta = a_val - b_val
                    if abs(delta) > 1e-6:
                        deltas[stat_key] = delta

                        # Normalize slope into [1, 5]
                        raw_slope = damage / (abs(delta) + 1e-6)
                        slope_score = max(1.0, min(5.0, raw_slope / 1000))

                        slopes[stat_key] = slope_score
                        active_buff_contribs[move_name] = (
                            active_buff_contribs.get(move_name, 0) + slope_score
                        )

        return {
            "unit": unit_name,
            "stat_deltas": deltas,
            "slopes": slopes,
            "active_buff_contribs": active_buff_contribs,
            "move_name": move_name,
            "estimated_damage": damage
        }


    def get_total_damage(self, unit_name=None):
        if unit_name:
            return sum(entry["damage"] for entry in self.damage_log if entry.get("unit") == unit_name)
        return sum(entry["damage"] for entry in self.damage_log)



    def _get_stack_and_time(self, active_buffs: Dict[str, dict], current_frame: int, buff_order: List[dict]):
        """
        Returns stack counts and remaining time for buffs in a fixed order.
        - buff_order: list of dicts with keys {"buff_name", "stat_key"}
        - active_buffs: dict keyed by buff_name
        """
        stack_counts = []
        time_lefts = []

        for entry in buff_order:
            buff_name = entry.get("buff_name")
            if buff_name and buff_name in active_buffs:
                buff_data = active_buffs[buff_name]
                stacks = buff_data.get("stacks", 0)
                expire_fr = buff_data.get("expire_frame")
                remaining = max(0, expire_fr - current_frame) if expire_fr is not None else -1
            else:
                stacks = 0
                remaining = 0

            stack_counts.append(int(stacks))
            time_lefts.append(int(remaining))

        return stack_counts, time_lefts


    MAX_RESONATOR_BUFFS = 80
    MAX_WEAPON_BUFFS    = 20
    MAX_ECHO_BUFFS      = 30

    def _get_buff_catalog_names(self, source, suffix="_Buffs"):
        """
        Generic catalog reader:
        - Look for attributes ending with suffix (e.g. Weapon_Buffs, Echo_Buffs, Resonator_Buffs).
        - Return a list of {buff_name, stat_key} dicts.
        - Fallback: active_buffs keys (buff_name only, no stat_key).
        """
        for attr_name in dir(source):
            if attr_name.endswith(suffix):
                catalog = getattr(source, attr_name)
                if isinstance(catalog, list):
                    entries = []
                    for entry in catalog:
                        if isinstance(entry, dict):
                            buff_name = entry.get("buff_name") or entry.get("name")
                            stats = entry.get("stat", {}) or {}
                            if buff_name:
                                for stat_key in stats.keys() or [None]:
                                    entries.append({
                                        "buff_name": buff_name,
                                        "stat_key": stat_key
                                    })
                    if entries:
                        return entries
        # fallback
        if hasattr(source, "active_buffs") and isinstance(source.active_buffs, dict):
            return [
                {"buff_name": name, "stat_key": None}
                for name in source.active_buffs.keys()
            ]
        return []


    def _build_buff_order(self, category: str, unit) -> list:
        """
        Build a fixed-length buff order list for the given category.
        category ∈ {"resonator", "weapon", "echo", "main_echo"}.
        Each entry is a dict with {buff_name, stat_key}.
        """
        if category == "resonator":
            base_entries = self._get_buff_catalog_names(unit, "_Buffs")
            max_len = self.MAX_RESONATOR_BUFFS

        elif category == "weapon":
            if getattr(unit, "weapon", None):
                base_entries = self._get_buff_catalog_names(unit.weapon, "_Buffs")
            else:
                base_entries = []
            max_len = self.MAX_WEAPON_BUFFS

        elif category == "echo":
            if getattr(unit, "echo_set", None):
                base_entries = self._get_buff_catalog_names(unit.echo_set, "_Buffs")
            else:
                base_entries = []
            max_len = self.MAX_ECHO_BUFFS

        else:
            base_entries = []
            max_len = 0

        # truncate or pad
        base_entries = base_entries[:max_len]
        while len(base_entries) < max_len:
            base_entries.append({"buff_name": None, "stat_key": None})

        return base_entries




    def can_use_move(self, move_name, unit_override=None, source="exec"):
        unit_name = unit_override or self.get_move_owner(move_name) 
        # print(f"[CAN_USE_MOVE DEBUG] move='{move_name}' | source='{source}' | unit_override='{unit_override}' | actual_owner='{unit_name}'")
        unit_data = self.team.get(unit_name)
        if not unit_data or "unit" not in unit_data:
            return False, f"{unit_name} is not defined"

        unit = unit_data["unit"]
        history = self.history.get(unit_name, [])
        resources = self.resources.get(unit_name, {})

        # 1. Unit-specific logic
        if hasattr(unit, "can_use_move"):
            can_use, reason = unit.can_use_move(move_name, resources=resources, history=history, global_history = self.global_history)
            if not can_use:
                # print(f"[DEBUG-SP] Checking {move_name} for {unit_name}")
                # print(f"   history(last3)={history[-3:]}")
                return False, reason

        # 2. Echo move charge (special case)
        if move_name == "Echo: Nightmare Crownless":
            echo = getattr(unit, "main_echo", None)
            if echo is None:
                return False, "No main echo equipped"
            if echo.current_charges <= 0:
                return False, "No charges left for Nightmare: Crownless"

        # 3. Movement state chaining check
        move_data = self.moves.get(move_name)
        if not move_data:
            move_data = unit.moves.get(move_name)

        if not move_data:
            return False, f"Move data for '{move_name}' not found (check team/unit.moves)"


        start_states = move_data.get("Start", ["GR"])  # Default to GR if missing
        current_state = getattr(self, "current_state", ["GR"])
        if isinstance(current_state, str):
            current_state = [current_state]

        if not any(state in start_states for state in current_state):
            return False, f"Cannot use {move_name} from {current_state}. Needs: {start_states}"

        return True, "Move is usable"




    def update_echo(self, delta_frames):
        # Define a method to update the echo
        if self.echo_active:
            # If the echo is active, update the echo timer
            self.echo_timer -= delta_frames
            if self.echo_timer <= 0:
                # If the echo timer is less than or equal to 0, set the echo to inactive
                self.echo_active = False
                

    def get_last_action(self, global_scope=False):
        if global_scope:
            # Flatten everything
            all_actions = [
                (unit, move_name, frame, index)
                for unit, actions in self.history.items()
                for (move_name, frame, index) in actions
            ]

            if not all_actions:
                return None

            # Pick most recent by frame
            unit, last_move_name, _, last_index = max(all_actions, key=lambda x: x[2])
            move_data = self.moves.get(last_move_name, {})

            return {
                "unit": unit,
                "name": last_move_name,
                "trigger": move_data.get("Trigger", ""),
                "hits": int(move_data.get("Hits", 1)),
                "index": last_index,
                "Healing": int(move_data.get("Healing", False)),
            }

        else:
            unit_name = self.active_unit
            unit_history = self.history.get(unit_name, [])

            if not unit_history:
                return None

            last_move_name, _, last_index = unit_history[-1]
            move_data = self.moves.get(last_move_name, {})
        

            return {
                "unit": unit_name,
                "name": last_move_name,
                "trigger": move_data.get("Trigger", ""),
                "hits": int(move_data.get("Hits", 1)),
                "index": last_index,
                "Healing": int(move_data.get("Healing", False)),
            }

    def is_on_cooldown(self, move_name, unit_override=None):
        unit_name = unit_override or self.active_unit
        base_name = move_name.split(" (")[0]  # normalize move name
        self.cooldowns.setdefault(unit_name, {})

        # Fetch cooldown from unit moves JSON
        unit_moves = self.resonator_map[unit_name].moves
        move_data = unit_moves.get(move_name) or unit_moves.get(base_name)
        duration = move_data.get("Cooldown", 0) if move_data else 0


        cd_end = self.cooldowns[unit_name].get(base_name, 0)
        on_cd = self.current_time_frame < cd_end

        # DEBUG
        # print(f"[DEBUG] FIRST CHECK] unit='{unit_name}', move='{base_name}', "
        #     f"cd_end={cd_end}, current_time={self.current_time_frame}, on_cd={on_cd}, duration={duration}")

        return on_cd



    def get_state(self):
        """
        Build flattened state tuple:
            state = (
                per_unit_features (3 * F),
                global_features (G),
                action_mask (A)
            )
        Returns:
            tuple[float]
        """

        # --- Helper: token maps (elements + move types + heal) ---
        ELEMENTS = ["Ae", "El", "Fu", "Gl", "Ha", "Sp"]   # element tokens
        MOVE_TYPES = ["No", "Sk", "He", "Rl", "Ou", "In", "Ec"]  # move type tokens
        EXTRA_TOKENS = ["Hl", "Hp"]  # healing token (as you used in example)
        # Build total token list and index maps (longest-first to parse greedy)
        TOKEN_LIST = sorted(ELEMENTS + MOVE_TYPES + EXTRA_TOKENS, key=lambda s: -len(s))
        TOKEN_TO_IDX = {t: i for i, t in enumerate(TOKEN_LIST)}
        N_ELEMENT = len(ELEMENTS)
        N_TYPE = len(MOVE_TYPES)
        MOD_VEC_LEN = N_ELEMENT + N_TYPE + len(EXTRA_TOKENS)  # final modifier vector length

        def parse_modifier(mod_str):
            """
            Greedy parse of modifier string into:
                element_vec (len N_ELEMENT), type_vec (len N_TYPE), extra_vec (len extra)
            Supports modifiers like "SkFu", "InSkSpHl", etc.
            Returns flattened tuple (element_vec + type_vec + extra_vec)
            """
            elem_vec = [0] * N_ELEMENT
            type_vec = [0] * N_TYPE
            extra_vec = [0] * len(EXTRA_TOKENS)

            if not mod_str:
                return tuple(elem_vec + type_vec + extra_vec)

            s = mod_str.strip()
            i = 0
            # greedy scan left-to-right matching tokens in TOKEN_LIST
            while i < len(s):
                matched = False
                for tok in TOKEN_LIST:
                    if s.startswith(tok, i):
                        matched = True
                        if tok in ELEMENTS:
                            elem_vec[ELEMENTS.index(tok)] = 1
                        elif tok in MOVE_TYPES:
                            type_vec[MOVE_TYPES.index(tok)] = 1
                        elif tok in EXTRA_TOKENS:
                            extra_vec[EXTRA_TOKENS.index(tok)] = 1
                        # print(f"[DEBUG] Matched token {tok} in '{mod_str}' at {i}")
                        i += len(tok)
                        break
                if not matched:
                    # print(f"[DEBUG] Unrecognized char '{s[i]}' in '{mod_str}' at {i}")
                    # fallback: skip one char to avoid infinite loop (handles unexpected chars)
                    i += 1

            vec = tuple(elem_vec + type_vec + extra_vec)
            # print(f"[DEBUG] Final vector for '{mod_str}': {vec}")
            return vec

        # === Cooldowns (Global 300-aligned) + parallel modifier encodings per move ===
        cooldowns_tuple = []
        modifiers_for_all_moves = []  # flattened list of per-move modifier vectors (for all units)
        for unit_slot, (unit_name, unit_data) in enumerate(self.team.items()):
            moves = list(unit_data["unit"].moves.values())

            # real moves first
            for m in moves:
                move_name = m.get("Skill")
                cd_end = self.cooldowns.get(unit_name, {}).get(move_name, 0)
                remaining_cd = max(0, cd_end - self.current_time_frame)
                cooldowns_tuple.append(remaining_cd)


                # parse modifier for this move and store flattened vector
                mod_str = m.get("Modifier", "") or ""
                mod_vec = parse_modifier(mod_str)
                modifiers_for_all_moves.extend(mod_vec)

            # pad moves and modifiers up to 100 moves per unit
            real_count = len(moves)
            pad_count = 100 - real_count
            for _ in range(pad_count):
                cooldowns_tuple.append(0)
                modifiers_for_all_moves.extend((0,) * MOD_VEC_LEN)

        cooldowns_tuple = tuple(cooldowns_tuple)  # fixed 300-wide
        modifiers_for_all_moves = tuple(modifiers_for_all_moves)  # fixed 300 * MOD_VEC_LEN wide

        unit_features = []

        # === Per-Unit Features ===
        # We'll need an offset to fetch per-unit modifiers aligned with cooldowns (100 moves each)
        for unit_slot, (unit_name, unit_data) in enumerate(self.team.items()):
            unit = unit_data["unit"]

            # --- Last Action (per unit) ---
            last_action = self.get_last_action(global_scope=False)
            if last_action is None:
                last_action_vec = (-1, 0, 0, 0) + (0,) * MOD_VEC_LEN
            else:
                trigger_map = {"Basic": 0, "Skill": 1, "Heavy": 2,
                            "Lib": 3, "Intro": 4, "Outro": 5, "EchoSkill": 6}
                trigger_id = trigger_map.get(last_action.get("trigger"), -1)
                # encode modifier of last action
                last_mod_vec = parse_modifier(last_action.get("Modifier", "") or "")
                last_action_vec = (
                    last_action.get("index", -1),
                    trigger_id,
                    last_action.get("hits", 0),
                    1.0 if last_action.get("Healing", False) else 0.0,
                    *last_mod_vec
                )

            # --- Recent History (last 3 moves for this unit) ---
            unit_history = self.history.get(unit_name, [])
            index_tuple = tuple(entry[2] for entry in unit_history[-3:][::-1])
            index_tuple = index_tuple + (-1,) * (3 - len(index_tuple))

            # === Echo Buffs ===
            if getattr(unit, "echo_set", None):
                echo_order = self._build_buff_order("echo", unit)
                echo_stack_counts, echo_time_lefts = self._get_stack_and_time(
                    active_buffs=unit.echo_set.active_buffs,
                    current_frame=self.current_time_frame,
                    buff_order=echo_order
                )
                echo_stats = unit.echo_set.get_active_echo_bonuses()
            else:
                echo_order = [{"buff_name": None, "stat_key": None}] * self.MAX_ECHO_BUFFS
                echo_stack_counts, echo_time_lefts = [0]*self.MAX_ECHO_BUFFS, [0]*self.MAX_ECHO_BUFFS
                echo_stats = {}

            # === Weapon Buffs ===
            if getattr(unit, "weapon", None):
                unit.weapon.process_move_effects(self.current_time_frame, last_action, unit)
                unit.weapon.update_buffs(self.current_time_frame, unit)
                weapon_order = self._build_buff_order("weapon", unit)
                weapon_stack_counts, weapon_time_lefts = self._get_stack_and_time(
                    active_buffs=unit.weapon.active_buffs,
                    current_frame=self.current_time_frame,
                    buff_order=weapon_order
                )
                weapon_stats = unit.weapon.get_active_weapon_buffs()
            else:
                weapon_order = [{"buff_name": None, "stat_key": None}] * self.MAX_WEAPON_BUFFS
                weapon_stack_counts, weapon_time_lefts = [0]*self.MAX_WEAPON_BUFFS, [0]*self.MAX_WEAPON_BUFFS
                weapon_stats = {}

            # === Resonator Buffs ===
            res_order = self._build_buff_order("resonator", unit)
            resonator_stack_counts, resonator_time_lefts = self._get_stack_and_time(
                active_buffs=unit.active_buffs,
                current_frame=self.current_time_frame,
                buff_order=res_order
            )
            resonator_stats = unit.get_active_resonator_bonuses()

            # === Full stat recompute (optional) ===
            self.stats = stat_page(unit)

            # === Stat Tuples ===
            weapon_stat_tuple = tuple(
                float(weapon_stats.get(entry["stat_key"], 0.0)) if entry["stat_key"] else 0.0
                for entry in weapon_order
            )
            echo_stat_tuple = tuple(
                float(echo_stats.get(entry["stat_key"], 0.0)) if entry["stat_key"] else 0.0
                for entry in echo_order
            )
            resonator_stat_tuple = tuple(
                float(resonator_stats.get(entry["stat_key"], 0.0)) if entry["stat_key"] else 0.0
                for entry in res_order
            )

            # === Stack + Time Tuples ===
            weapon_stack_tuple    = tuple(weapon_stack_counts)
            weapon_time_tuple     = tuple(weapon_time_lefts)
            echo_stack_tuple      = tuple(echo_stack_counts)
            echo_time_tuple       = tuple(echo_time_lefts)
            resonator_stack_tuple = tuple(resonator_stack_counts)
            resonator_time_tuple  = tuple(resonator_time_lefts)

            # === Resources ===
            unit_res = self.resources[unit_name]  # note: use per-unit resources (was self.active_unit before)

            # === Per-unit slice of modifiers aligned with this unit's moves ===
            # each unit has 100 slots of moves; compute offset in modifiers_for_all_moves
            move_slot_offset = unit_slot * 100 * MOD_VEC_LEN
            per_unit_modifiers = modifiers_for_all_moves[move_slot_offset: move_slot_offset + (100 * MOD_VEC_LEN)]

            # === Unit State (all flat tuples, no nesting) ===
            unit_state = (
                *last_action_vec,
                *index_tuple,
                float(unit_res["Forte"]),
                float(unit_res["Resonance"]),
                float(unit_res["Concerto"]),
                *cooldowns_tuple[unit_slot*100:(unit_slot+1)*100],
                *per_unit_modifiers,
                *weapon_stat_tuple,
                *echo_stat_tuple,
                *resonator_stat_tuple,
                *echo_stack_tuple,
                *echo_time_tuple,
                *weapon_stack_tuple,
                *weapon_time_tuple,
                *resonator_stack_tuple,
                *resonator_time_tuple,
            )

            unit_features.extend(unit_state)

        # === Global Features ===
        global_last_action = self.get_last_action(global_scope=True)
        if global_last_action is None:
            global_last_action_vec = (-1, 0, 0, 0) + (0,) * MOD_VEC_LEN
        else:
            trigger_map = {"Basic": 0, "Skill": 1, "Heavy": 2,
                        "Lib": 3, "Intro": 4, "Outro": 5, "EchoSkill": 6}
            trigger_id = trigger_map.get(global_last_action.get("trigger"), -1)
            global_mod_vec = parse_modifier(global_last_action.get("Modifier", "") or "")
            global_last_action_vec = (
                global_last_action.get("index", -1),
                trigger_id,
                global_last_action.get("hits", 0),
                1.0 if global_last_action.get("Healing", False) else 0.0,
                *global_mod_vec
            )

        enemy_current_hp = self.enemy.current_hp if self.enemy else 0.0
        enemy_max_hp     = self.enemy.max_hp if self.enemy else 1.0
        enemy_hp_percent = float(enemy_current_hp) / max(float(enemy_max_hp), 1.0)

        # normalize using whatever range the enemy was defined with
        hp_min, hp_max = self.enemy.hp_range if self.enemy else (1, 1)
        enemy_max_hp_norm = (enemy_max_hp - hp_min) / max(hp_max - hp_min, 1)

        global_features = (
            self.current_time_frame,
            enemy_hp_percent,
            enemy_max_hp_norm,
            *global_last_action_vec,
        )


        #  === Action Mask ===
        action_mask = self.get_valid_action_mask().astype(np.float32)

        # === Final State Array ===
        state = np.array(unit_features + list(global_features) + list(action_mask), dtype=np.float32)
        return state


    def reset(self):
        # Core trackers
        self.current_state = "GR"
        self.enemy.reset()
        self.current_time_frame = 0
        self.execution_stage = 0
        self.echo_timer = 0
        self.damage_log.clear()
        self.global_history = []
        self.move_queue.clear()
        self.episode_best_sequence = []
        self.episode_reward = 0
        self.episode_best_damage = 0
        self.total_episode_reward = 0
        self.episode_min_time = float("inf")
        self.last_setup_move_index = None
        self.liberation_windows.clear()

        # Last swap reset
        self.last_swap = {"unit_name": None, "frame": -9999}

        # Reset per-unit history and resources
        self.history = {k: [] for k in self.resonator_map}
        self.resources = {
            k: {"Forte": 0, "Resonance": 250, "Concerto": 0, "Time": 0}
            for k in self.resonator_map
        }

        # Reset cooldowns
        self.cooldowns = {}
        for unit_name, data in self.team.items():
            unit = data["unit"]
            self.cooldowns[unit_name] = {}
            for move_name, move_data in unit.moves.items():
                if move_data.get("Cooldown", 0) > 0:
                    self.cooldowns[unit_name][move_name] = 0

        # Reset buffs and states on units, weapons, echoes
        for slot, data in self.team.items():
            unit = data["unit"]
            if hasattr(unit, "reset"):
                unit.reset()
              # Explicitly reset execution flags if they exist
            if hasattr(unit, "discernment_available"):
                unit.discernment_available = False
            if hasattr(unit, "can_use_crimson"):
                unit.can_use_crimson = False
            if hasattr(unit, "can_use_sanguine"):
                unit.can_use_sanguine = False
            if hasattr(unit, "can_use_chaoscleave_50"):
                unit.can_use_chaoscleave_50 = False
            if hasattr(unit, "can_use_chaoscleave_100"):
                unit.can_use_chaoscleave_100 = False

            if getattr(unit, "weapon", None):
                unit.weapon.reset()
            if getattr(unit, "echo_set", None):
                unit.echo_set.reset()

        # Start with resonator1 as active
        self.active_unit = "resonator1"

        # Initial obs + action mask
        initial_state = self.get_state()
        action_mask = self.get_valid_action_mask()
        return initial_state, {"action_mask": action_mask}


    def get_total_dmg_pct(self, move):
        dmg_dict = move.get("DMG %", {})
        total = 0.0
        for _, val in dmg_dict.items():
            try:
                total += float(val.strip('%'))
            except Exception:
                continue
        return total


    def step(self, move_name, active_unit=None):
        """
        Team-play step function with reward shaping.
        Caps applied to reward components and per-step reward so they cannot explode;
        time_bonus (termination) remains uncapped so it can still dominate.
        """
        # ---- tuning constants (adjustable) ----
        COMPONENT_CAP = 50.0       # max abs value for any individual reward component
        STEP_CAP = 50.0            # max abs value for the per-step normalized reward
        EFFICIENCY_BONUS_CAP = 5000.0
        # ----------------------------------------

        epsilon = 1e-6
        max_frames = 10_800
        forte_cap = 41
        alpha_damage = 3.0
        beta_forte = 1.2
        beta_resonance = 1.5
        gamma_concerto = 0.4
        lambda_rank = 4.0

        # Buff/resonance weighting (tunable)
        BUFF_CONTRIB_WEIGHT = 35.0    # primary priority (highest)
        BUFF_SLOPE_WEIGHT = 38.0      # slightly higher than contrib
        RESONANCE_WEIGHT = 30.0       # big, but slightly below buff weights

        reward_components = {}

        # Determine acting unit
        unit_name = self.get_move_owner(move_name) or active_unit or self.active_unit
        unit = self.team[unit_name]["unit"]
        resonance_cap = getattr(unit, "stats", {}).get("Resonance Cost", 100)

        # Lookup move
        move = self.moves.get(move_name)
        if not move:
            move_index = self.rl_name_to_index.get(move_name, -1)
            info = {
                "reward": -0.5,
                "move_index": move_index,
                "move_name": move_name,
                "rank": -1,
                "action_mask": self.get_valid_action_mask()
            }
            return self.get_state(), -0.5, False, False, info

        # === Legal moves & scoring ===
        legal_scored_moves = []
        chosen_move = None
        for m in self.moves.values():
            if not self.can_use_move(m["Skill"]):
                continue
            score = self.score_move(m)
            legal_scored_moves.append((m, score))
            if m["Skill"] == move_name:
                chosen_move = m

        if not chosen_move:
            move_index = self.rl_name_to_index.get(move_name, -1)
            info = {
                "reward": -1.0,
                "move_index": move_index,
                "move_name": move_name,
                "rank": -1,
                "action_mask": self.get_valid_action_mask()
            }
            return self.get_state(), -1.0, False, False, info

        # Rank-based reward
        legal_scored_moves.sort(key=lambda x: x[1], reverse=True)
        rank = next(i for i, (m, s) in enumerate(legal_scored_moves) if m == chosen_move)
        num_legal_moves = len(legal_scored_moves)
        rank_reward = 1.0 - (rank / (num_legal_moves - 1 + epsilon))
        raw_rank = lambda_rank * rank_reward
        # keep existing mild squish for rank so it doesn't explode
        reward_components["rank"] = (raw_rank / (abs(raw_rank) + 30))


        # Repeat penalty (you may tune this down if it's too harsh)
        repeat_count = 1 if self.global_history and self.global_history[-1][1] == move["Skill"] else 0
        repeat_penalty = 1000 * (repeat_count)
        reward_components["repeat_penalty"] = -repeat_penalty

        # Capture before resources
        before_forte = self.resources[unit_name]["Forte"]
        before_concerto = self.resources[unit_name]["Concerto"]
        before_resonance = self.resources[unit_name]["Resonance"]

        # reward_Echo = 0
        # if  in move_name:
        #     reward_Echo += 50

        # === Execute move ===
        damage, success, before_stats, after_stats = self.perform_move(move_name)
        if not success:
            move_index = self.rl_name_to_index.get(move_name, -1)
            info = {
                "reward": -2.0,
                "move_index": move_index,
                "move_name": move_name,
                "rank": rank,
                "action_mask": self.get_valid_action_mask()
            }
            return self.get_state(), -2.0, False, False, info

        # Capture after resources
        after_forte = self.resources[unit_name]["Forte"]
        after_concerto = self.resources[unit_name]["Concerto"]
        after_resonance = self.resources[unit_name]["Resonance"]

        # === Reward signals (baseline) ===
        time = move.get("Time", 1.0) or epsilon
        total_dmg_pct = sum(float(v.strip('%')) / 100 for v in move.get("DMG %", {}).values())
        damage_per_time = total_dmg_pct / time
        raw_value = alpha_damage * damage_per_time
        # keep damage/time as a small bounded signal 
        reward_components["damage/time"] = (raw_value / (abs(raw_value) + 50))

        # --- Trigger bonus factor ---
        trigger_bonus = 0.0
        for buff in getattr(unit, "Buffs", []):
            # Reset _applied if buff expired
            if "_applied" in buff and buff.get("duration_frames") is not None:
                start_frame = buff.get("start_frame", 0)
                if self.current_time_frame >= start_frame + buff["duration_frames"]:
                    buff["_applied"] = False

            # Only apply bonus if move matches trigger and not already applied
            if move_name == buff.get("trigger") and not buff.get("_applied", False):
                early_factor = max(0.5, 1.0 - self.current_time_frame / 10800)
                trigger_bonus += 40.0 * early_factor  # tune magnitude
                buff["_applied"] = True  # mark as applied
                buff.setdefault("start_frame", self.current_time_frame)  # store when triggered


        # Forte efficiency
        forte_delta = after_forte - before_forte
        if forte_delta > 0:
            forte_score = max(0, min(forte_cap - before_forte, forte_delta))
        elif forte_delta < 0:
            forte_score = 2.5 * min(before_forte, abs(forte_delta))
        else:
            forte_score = 0.0
        reward_components["forte"] = beta_forte * forte_score

        # Resonance logic 
        resonance_delta = after_resonance - before_resonance
        if resonance_delta < 0:
            resonance_score_raw = 100.0 * min(before_resonance, abs(resonance_delta))
        elif resonance_delta > 0:
            resonance_score_raw = 0.2 * min(resonance_cap, after_resonance)
        else:
            resonance_score_raw = 0.0

        # Concerto efficiency
        concerto_delta = after_concerto - before_concerto
        if concerto_delta > 0:
            concerto_score = max(0, min(100 - before_concerto, concerto_delta))
        elif concerto_delta < 0:
            concerto_score = 2.0 * min(before_concerto, abs(concerto_delta))
        else:
            concerto_score = 0.0
        reward_components["concerto"] = gamma_concerto * concerto_score

        # Off-CD incentive 
        reward_components["off_cd"] = 0.5 if not self.is_on_cooldown(move_name, unit_override=unit_name) else 0.0

        # Buff raw metrics 
        if before_stats and after_stats:
            buff_info = self.estimate_buff_impact(unit_name, before_stats, after_stats, damage, move_name)
            slope_raw = sum(buff_info["slopes"].values())
            contrib_raw = sum(buff_info["active_buff_contribs"].values())
        else:
            slope_raw = 0.0
            contrib_raw = 0.0

        # -------------------------
        # Normalize & weight buffs and resonance (moving max to keep scaling stable)
        # initialize moving-max trackers if missing
        if not hasattr(self, "_max_buff_contrib"):
            self._max_buff_contrib = max(contrib_raw, 1.0)
        if not hasattr(self, "_max_buff_slope"):
            self._max_buff_slope = max(slope_raw, 1.0)
        if not hasattr(self, "_max_resonance"):
            self._max_resonance = max(resonance_score_raw, 1.0)

        # update moving-max (slow decay so single spikes don't permanently dominate)
        decay = 0.999 
        self._max_buff_contrib = max(self._max_buff_contrib * decay, contrib_raw, 1.0)
        self._max_buff_slope = max(self._max_buff_slope * decay, slope_raw, 1.0)
        self._max_resonance = max(self._max_resonance * decay, resonance_score_raw, 1.0)

        # normalized in [0, ~1] (safe)
        contrib_norm = contrib_raw / (self._max_buff_contrib + 1e-9)
        slope_norm = slope_raw / (self._max_buff_slope + 1e-9)
        resonance_norm = resonance_score_raw / (self._max_resonance + 1e-9)

        # decay factor by episode progress (makes late-game buff-only farming less attractive)
        progress_factor = 1.0 - (min(self.current_time_frame, max_frames) / float(max_frames)) * 0.5
        # small clamp
        progress_factor = max(0.5, progress_factor)

        # compute weighted buff/resonance contributions (dominant)
        buff_contrib_value = contrib_norm * BUFF_CONTRIB_WEIGHT * progress_factor
        buff_slope_value = slope_norm * BUFF_SLOPE_WEIGHT * progress_factor
        resonance_value = resonance_norm * RESONANCE_WEIGHT * progress_factor

        reward_components["buff_contrib"] = buff_contrib_value
        reward_components["buff_slope"] = buff_slope_value
        reward_components["resonance"] = resonance_value

        # -------------------------
        # Category chain logic (keep your version intact)
        DEBUG = False

        history = getattr(unit, "history", [])
        if DEBUG: print(f"[DEBUG] Raw history for {unit.name}: {history}")

        if len(history) <= 1:
            reward_components["category_chain"] = 0.0
            if DEBUG: print(f"[DEBUG] History too short for {unit.name}, skipping category_chain reward")
        else:
            filtered_history = [entry for entry in history if entry[0] != "Liberation: Marcato"]
            if DEBUG: print(f"[DEBUG] Filtered 'Marcato' history for {unit.name}: {filtered_history}")

            last_moves = [entry[0] for entry in filtered_history[-5:]]
            if DEBUG: print(f"[DEBUG] Last 5 moves for {unit.name}: {last_moves}")

            if not hasattr(unit, "_move_categories"):
                unit._move_categories = {"builder": [], "spender": [], "setup": []}
                for m_name, m_data in unit.moves.items():
                    f_val = m_data.get("Forte", 0)
                    if f_val > 0:
                        unit._move_categories["builder"].append(m_name)
                    elif f_val < 0:
                        unit._move_categories["spender"].append(m_name)
                    else:
                        unit._move_categories["setup"].append(m_name)

            cat_sequence = []
            for m in last_moves:
                for cat, moves_list in unit._move_categories.items():
                    if m in moves_list:
                        cat_sequence.append(cat)
                        break

            # Remove consecutive duplicates
            cat_sequence = [cat_sequence[i] for i in range(len(cat_sequence)) if i == 0 or cat_sequence[i] != cat_sequence[i-1]]

            # Reward calculation (future-looking chain scan)
            reward_points = 0.0
            i = 0
            while i < len(cat_sequence):
                if cat_sequence[i] == "setup":
                    next_two = cat_sequence[i+1:i+3]
                    if next_two == ["builder", "spender"]:
                        reward_points += 10.0
                        i += 3
                    elif next_two[:1] == ["builder"]:
                        reward_points = max(reward_points, 5.0)
                        i += 2
                    else:
                        reward_points -= 20.0
                        i += 1
                else:
                    i += 1

            reward_components["category_chain"] = reward_points

        # -------------------------
        # Cap each individual component to avoid blowups
        for k, v in list(reward_components.items()):
            reward_components[k] = max(min(float(v), COMPONENT_CAP), -COMPONENT_CAP)
            if DEBUG: print(f"[DEBUG] Capped reward component {k}: {reward_components[k]}")

        terminated = self.enemy.current_hp <= 0
        truncated = self.current_time_frame >= max_frames

        # Initialize cumulative episode reward at the start of an episode
        if not hasattr(self, "episode_reward"):
            self.episode_reward = 0.0

        # Step-level reward (capped)
        step_reward = sum(reward_components.values()) + trigger_bonus
        time_factor = (self.current_time_frame + 1) ** 0.5  # normalize by sqrt(time)
        normalized_step_reward = step_reward / time_factor
        normalized_step_reward = max(min(normalized_step_reward, STEP_CAP), -STEP_CAP)
        self.episode_reward += normalized_step_reward

        # Reward percentages (optional debug)
        total_abs = sum(abs(v) for v in reward_components.values()) + 1e-6
        reward_percentages = {k: 100 * v / total_abs for k, v in reward_components.items()}

        # Update episode bests if terminated or truncated
        if terminated or truncated:
            total_damage = min(self.get_total_damage(), 3_200_000)
            episode_sequence = [entry[1] for entry in self.global_history]
            used_echo = any("Echo" in move for move in episode_sequence)
            total_time = self.current_time_frame or 1

            final_reward = self.episode_reward
            reset_episode_reward = False

            # Compute DPS
            dps = total_damage / (total_time / 60) if total_time > 0 else 0

            if terminated:
                # Reward based on DPS directly (sublinear scaling)
                dps_reward = (dps ** 0.9)
                self.episode_reward += dps_reward
                final_reward = self.episode_reward

            # Update global bests if enemy died
            if terminated:
                if not hasattr(self, "global_min_time"):
                    self.global_min_time = float("inf")
                    self.global_best_damage = 0
                    self.global_best_sequence = []
                    self.global_best_reward = -float("inf")

                is_better = total_damage > self.global_best_damage or (
                    total_damage == self.global_best_damage and total_time < self.global_min_time
                )

                if is_better:
                    self.global_min_time = total_time
                    self.global_best_damage = total_damage
                    self.global_best_sequence = list(episode_sequence)
                    self.global_best_reward = self.episode_reward
                    self.global_best_used_echo = used_echo

                    print(f"[NEW GLOBAL BEST]")
                    print(f"  Time (frames): {self.global_min_time}")
                    print(f"  Damage: {self.global_best_damage}")
                    print(f"  DPS: {dps:.2f}")
                    print(f"  Episode Reward: {self.global_best_reward:.2f}")
                    print(f"  Sequence: {' -> '.join(self.global_best_sequence)}")
                    print(f"  Used Echo: {self.global_best_used_echo}")

            print(f"[EPISODE END] Time (frames): {total_time}, Damage: {total_damage}, "
                f"DPS: {dps:.2f}, Reward: {self.episode_reward:.2f}, Used Echo: {used_echo}")

            reset_episode_reward = True
        else:
            final_reward = normalized_step_reward
            reset_episode_reward = False

        # Return info dict
        move_index = self.rl_name_to_index.get(move_name, -1)
        info = {
            "reward": final_reward,
            "move_index": move_index,
            "move_name": move_name,
            "rank": rank,
            "action_mask": self.get_valid_action_mask()
        }

        # Reset episode reward if needed
        if reset_episode_reward:
            self.episode_reward = 0.0

        return self.get_state(), final_reward, terminated, truncated, info



    def score_move(self, move, unit_name=None):
        """
        Heuristic scoring for ranking legal moves before execution.
        Uses expected deltas from the move + current resources of the acting unit.
        """
        epsilon = 1e-6
        unit_name = unit_name or self.active_unit

        # --- Time / Damage ---
        time = move.get("Time", 1.0) or epsilon
        dmg_dict = move.get("DMG %", {})
        total_dmg_pct = 0.0
        for v in dmg_dict.values():
            try:
                total_dmg_pct += float(str(v).strip('%')) / 100.0
            except Exception:
                pass
        damage_per_time = total_dmg_pct / time

        # --- Current resources (per-unit) ---
        res = self.resources.get(unit_name, {})
        forte_before = float(res.get("Forte", 0.0))
        concerto_before = float(res.get("Concerto", 0.0))
        resonance_before = float(res.get("Resonance", 0.0))

        # --- Expected deltas from move definition ---
        forte_delta = float(move.get("Forte", 0.0))
        concerto_delta = float(move.get("Concerto", 0.0))
        resonance_delta = float(move.get("Resonance", 0.0))

        # --- Forte scoring (builder/spender with cap/shortfall) ---
        forte_cap = 41.0
        if forte_delta > 0:
            # Gains that would overflow cap are wasted/penalized
            effective_gain = max(0.0, min(forte_cap - forte_before, forte_delta))
            overflow = max(0.0, (forte_before + forte_delta) - forte_cap)
            forte_score = 1.5 * effective_gain - 5.0 * overflow
        elif forte_delta < 0:
            spend = abs(forte_delta)
            if forte_before >= spend:
                forte_score = 2.5 * spend
            else:
                shortfall = spend - forte_before
                # Big penalty for attempting an unaffordable spender
                forte_score = -10.0 - 5.0 * shortfall
        else:
            forte_score = 0.0

        # --- Concerto scoring (keep simple, avoid going past 100) ---
        if concerto_delta > 0:
            conc_score = min(100.0 - concerto_before, concerto_delta)
        elif concerto_delta < 0:
            conc_score = 1.0 * min(concerto_before, abs(concerto_delta))
        else:
            conc_score = 0.0

        # --- Resonance scoring (unit-specific cap; spending is valuable) ---
        unit_obj = self.team[unit_name]["unit"]
        resonance_cap = getattr(getattr(unit_obj, "stats", {}), "get", lambda *_: None)("Resonance Cost") \
                        or getattr(unit_obj, "stats", {}).get("Resonance Cost", 100.0)

        if resonance_delta < 0:
            spend = abs(resonance_delta)
            if resonance_before >= spend:
                res_score = 5.0 * spend
            else:
                shortfall = spend - resonance_before
                res_score = -10.0 - 5.0 * shortfall
        elif resonance_delta > 0:
            # Small reward for gaining, scaled by how full the pool will be
            post = min(resonance_cap, resonance_before + resonance_delta)
            res_score = 0.2 * post
        else:
            res_score = 0.0

        # --- Final score (weights are heuristic; align with step() emphasis) ---
        score = (5.0 * damage_per_time) + forte_score + conc_score + (1.5 * res_score)
        return score






#----------------Brute-Forcing----------------# 

    def clone_state(self):
        # Use deepcopy to avoid reference issues
        cloned = ActionTracker(
            move_data=copy.deepcopy(self.moves),
            echo=copy.deepcopy(self.echo),
            resonator=copy.deepcopy(self.resonator),
            stats=copy.deepcopy(self.stats),
            enemy=copy.deepcopy(self.enemy),
        )
        # Copy basic states
        cloned.history = list(self.history)
        cloned.resources = dict(self.resources)
        cloned.resource_caps = dict(self.resource_caps)
        cloned.cooldowns = dict(self.cooldowns)
        cloned.current_time_frame = self.current_time_frame
        cloned.echo_active = self.echo_active
        cloned.echo_timer = self.echo_timer
        cloned.damage_log = list(self.damage_log)
        return cloned

    def brute_force_search(self, max_depth=1):
        best_sequence = []
        best_damage = -float('inf')

        def dfs(sequence, sim_state):
            nonlocal best_sequence, best_damage

            if len(sequence) == max_depth:
                total_dmg = sim_state.get_total_damage()
                if total_dmg > best_damage:
                    best_damage = total_dmg
                    best_sequence = sequence[:]
                return

            for move_name in sim_state.moves:
                if sim_state.is_on_cooldown(move_name):
                    continue

                can_use, _ = sim_state.can_use_move(move_name)
                if not can_use:
                    continue

                next_sequence = tuple(sequence + [move_name])

                # Use SimCache instead of raw dict
                if self.sim_cache.has(next_sequence):
                    next_state = self.sim_cache.get(next_sequence)
                else:
                    next_state = sim_state.clone_state()
                    next_state.use_move(move_name)
                    self.sim_cache.set(next_sequence, next_state)

                dfs(sequence + [move_name], next_state)

        dfs([], self.clone_state())
        return best_sequence, best_damage

    def clone(self):
        return copy.deepcopy(self)



# ------------ Heuristic Core ------------ #
    def choose_move(self):
        possible_moves = [m for m in self.moves.values()]

        def score_sequence(seq):
            temp_sim = self.clone()
            total_damage = 0
            total_concerto = 0
            start_time = temp_sim.current_time_frame

            for move in seq:
                if not temp_sim.can_use_move(move["Skill"])[0]:
                    return float("-inf")  # Invalid path
                temp_sim.use_move(move["Skill"])
                total_damage += move.get("Damage", 0)
                total_concerto += move.get("Concerto", 0)

            time_spent = (temp_sim.current_time_frame - start_time) / 60
            if time_spent == 0:
                return float("-inf")  # Avoid divide-by-zero
            return (total_damage + 0.5 * total_concerto) / time_spent

        best_move = None
        best_score = float("-inf")

       
        return best_move

   
 

    def get_cache_state(self):
        # Return a CachedSimState object containing the total damage, stats, resonator buffs, cooldowns, current time frame, weapon state, echo state, resources, and history of the current simulation
        return CachedSimState(
            total_damage=self.get_total_damage(),
            stats=self.stats, 
            resonator_buffs=self.resonator.get_active_buffs(),
            cooldowns=self.cooldowns,
            frame=self.current_time_frame,
            weapon_state=self.resonator.weapon.get_state(),
            echo_state=self.echo.get_state(),
            resources=self.resources,
            history=self.history
        )


class CachedSimState:
    # Initialize the CachedSimState class with the given parameters
    def __init__(self, total_damage, stats, resonator_buffs, cooldowns, frame, weapon_state, echo_state, resources, history, score=0):
        self.total_damage = total_damage
        self.stats = stats
        self.resonator_buffs = resonator_buffs
        self.cooldowns = cooldowns
        self.frame = frame
        self.weapon_state = weapon_state
        self.echo_state = echo_state
        self.resources = resources
        self.history = history
        self.score = score

    # Define the equality operator for the CachedSimState class
    def __eq__(self, other):
        # Return True if all attributes of the two CachedSimState objects are equal
        return (
            self.stats == other.stats and
            self.resonator_buffs == other.resonator_buffs and
            self.cooldowns == other.cooldowns and
            self.frame == other.frame and
            self.weapon_state == other.weapon_state and
            self.echo_state == other.echo_state and
            self.resources == other.resources and
            self.history == other.history
        )

    # Define the hash function for the CachedSimState class
    def __hash__(self):
        # Use tuple of hashable components. For dicts or lists, convert to frozenset or tuple of items
        return hash((
            tuple(sorted(self.stats.items())) if isinstance(self.stats, dict) else self.stats,
            tuple(sorted(self.resonator_buffs.items())) if isinstance(self.resonator_buffs, dict) else self.resonator_buffs,
            tuple(sorted(self.cooldowns.items())) if isinstance(self.cooldowns, dict) else self.cooldowns,
            self.frame,
            tuple(sorted(self.weapon_state.items())) if isinstance(self.weapon_state, dict) else self.weapon_state,
            tuple(sorted(self.echo_state.items())) if isinstance(self.echo_state, dict) else self.echo_state,
            tuple(sorted(self.resources.items())) if isinstance(self.resources, dict) else self.resources,
            tuple(self.history) if isinstance(self.history, list) else self.history
        ))



class SimCache:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key, None)

    def has(self, key):
        return key in self.cache

    def set(self, key, cached_state: CachedSimState):
        # Only set if new or better score
        if key not in self.cache or cached_state.score > self.cache[key].score:
            self.cache[key] = cached_state





def build_demo_team():
    # Create and equip resonators
    danjin = Danjin()
    mortefi = Mortefi()
    shorekeeper = Shorekeeper()

    # Weapons
    danjin.equip(EmeraldOfGenesis())
    mortefi.equip(StaticMist())
    shorekeeper.equip(StellarSymphony())

    # Echo sets
    danjin.equip_echo(HavocEclipse(equipped_count=5))
    mortefi.equip_echo(MoonlitClouds(equipped_count=5))
    shorekeeper.equip_echo(RejuvenatingGlow(equipped_count=5))

    # Main echoes
    move_data = {**danjin.moves, **mortefi.moves, **shorekeeper.moves}

    nightmare = NightmareCrownless()
    nightmare.equip_to(danjin, move_data, current_frame=0)
    danjin.main_echo = nightmare

    fallacy = FallacyOfNoReturn()
    fallacy.equip_to(shorekeeper, move_data, current_frame=0)
    shorekeeper.main_echo = fallacy

    heron = ImpermanenceHeron()
    heron.equip_to(mortefi, move_data, current_frame=0)
    mortefi.main_echo = heron

    # Enemy + stats
    enemy = Monke()
    stats = {
        "resonator1": stat_page(danjin),
        "resonator2": stat_page(mortefi),
        "resonator3": stat_page(shorekeeper),
    }

    # Final move data merge
    move_data = {**danjin.moves, **mortefi.moves, **shorekeeper.moves}

    # Return tracker
    return ActionTracker(
        move_data=move_data,
        resonator1=danjin,
        resonator2=mortefi,
        resonator3=shorekeeper,
        echo=None,
        stats=stats,
        enemy=enemy,
    )


if __name__ == "__main__":
    sim = build_demo_team()
    # sim.perform_move("Basic: Origin Calculus 1 2 3 4")
    # sim.perform_move("Forte: Illation (Cancel)")
    # sim.perform_move("Basic: Origin Calculus 1 2 3 4")
    # sim.perform_move("Forte: Illation (Cancel)")
    # sim.perform_move("Basic: Origin Calculus 1 2 3 4")
    # sim.perform_move("Forte: Illation (Cancel)")
    # sim.perform_move("Basic: Origin Calculus 1 2 3 4")
    # sim.perform_move("Forte: Illation (Cancel)")
    # sim.perform_move("Basic: Execution 1 2 3")
    # sim.perform_move("Skill: Sanguine Pulse (3)")
    # sim.perform_move("Basic: Execution 1 2 3")
    # sim.perform_move("Skill: Sanguine Pulse (3)")
    # sim.perform_move("Basic: Execution 1 2 3")
    # sim.perform_move("Skill: Sanguine Pulse (3)")
    # sim.get_valid_action_mask()
    # sim.perform_move("Skill: Chaos Theory")
    # sim.perform_move("Basic: Origin Calculus 1 2 3 4")
    # sim.perform_move("Forte: Illation (Cancel)")
    # sim.get_valid_action_mask()
    
    print(sim.enemy.current_hp)
    # sim.perform_move("Basic: Impromptu Show 4 (Swap)")
    # sim.perform_move("Basic: Origin Calculus 1 2 3 4 (Swap)")
    # sim.perform_move("Basic: Impromptu Show 4 (Swap)")
    # sim.perform_move("Basic: Execution 2")
    # sim.perform_move("Skill: Crimson Erosion (2) (Swap)")
    # sim.perform_move("Basic: Impromptu Show 4 (Swap)")
    # sim.get_valid_action_mask()
    # sim.perform_move("Basic: Origin Calculus 1 2 3 4 (Swap)")
    # # sim.perform_move("Skill: Chaos Theory (Cancel)")
    # # sim.perform_move("Echo: Fallacy Of No Return (Tap)")
    # # sim.perform_move("Liberation: End Loop")
    # sim.perform_move("Basic: Impromptu Show 4 (Swap)")
    # sim.perform_move("Liberation: Violent Finale")
    # sim.step("Skill: Camine Gleam (1) (Swap)")
    # sim.get_valid_action_mask()
    # sim.step("Basic: Origin Calculus 1 2 3 4 (Swap)")
    # sim.get_valid_action_mask()
    # sim.step("Basic: Execution 2 3")
    sim.get_valid_action_mask()
    # sim.perform_move("Forte: Fury Fogue")
    # sim.perform_move("Echo: Impermanence Heron (Tap)")
    # sim.perform_move("Skill: Crimson Erosion (2)")
    # sim.perform_move("Basic: Execution 1 2 3")
    # sim.perform_move("Skill: Sanguine Pulse (3)")
    # sim.perform_move("Basic: Origin Calculus 1 2 3 4 (Swap)")
    # sim.perform_move("Forte: Chaoscleave + Scatterbloom (100%)")
    # sim.perform_move("Basic: Execution 1 2")
    # sim.perform_move("Skill: Crimson Erosion (2)")
    # sim.perform_move("Basic: Execution 1 2 3")
    # sim.perform_move("Skill: Sanguine Pulse (3)")
    # sim.perform_move("Basic: Execution 1 2")
    # sim.perform_move("Skill: Crimson Erosion (2)")
    # sim.perform_move("Basic: Execution 1 2 3")
    # sim.perform_move("Skill: Sanguine Pulse (3)")
    # sim.perform_move("Forte: Chaoscleave + Scatterbloom (100%)")
    # sim.perform_move("Echo: Nightmare Crownless")
    # sim.perform_move("Echo: Nightmare Crownless")
    # sim.perform_move("Basic: Origin Calculus 1 2 3 4")
    
    # --- Manual simulation sequence for testing ---
    sim.reset()
    # sim.step("Liberation: End Loop")
    # sim.step("Echo: Fallacy Of No Return (Tap)")
    # sim.step("Basic: Execution 1 2 3")
    # sim.step("Skill: Sanguine Pulse (3)")
    # sim.step("Basic: Execution 1 2 3")
    # sim.step("Skill: Sanguine Pulse (3)")
    # sim.step("Basic: Execution 1 2 3")
    # sim.step("Skill: Sanguine Pulse (3)")
    # sim.step("Forte: Chaoscleave + Scatterbloom (100%)")

    # Raw sequence (copy-paste directly)
    print(sim.enemy.current_hp)
    raw_sequence = """
   [Sequence] Basic: Execution 1 2 3 -> Echo: Fallacy Of No Return (Tap) -> Basic: Execution 1 2 3 -> Liberation: End Loop -> Basic: Impromptu Show 4 (Cancel) -> Skill: Passionate Variation -> Forte: Fury Fogue (Swap) -> Skill: Chaos Theory -> Skill: Camine Gleam (1)
    """

    # Parse into clean list of moves
    test_sequence = [
        move.strip()
        for move in raw_sequence.replace("[Sequence]", "").split("->")
        if move.strip()
    ]

    # Run the parsed sequence
    for move in test_sequence:
        state, reward, terminated, truncated, info = sim.step(move)
        print(f"Move: {move}")
        print(f"  Reward: {reward:.4f}")
        print(f"  Enemy HP: {sim.enemy.current_hp}")
        print(f"  Terminated: {terminated}, Truncated: {truncated}")
        print("-" * 50)

    # Optional: check best sequence discovered so far
    if hasattr(sim, "best_sequence"):
        print(f"Current best sequence: {' -> '.join(sim.best_sequence)}")



    print(sim.enemy.current_hp)

   

#     # Assuming sim is your ActionTracker instance with 1 unit already setup
#     # action_index = [17, 16, 16, 7, 30, 51, 30, 14, 5, 30, 60, 50, 60, 40, 65, 42, 26, 20, 23, 66, 4, 16, 6, 11, 35, 35, 50]  

#     # print(sim.rl_index_to_name)
#     # for idx in action_index:
#     #     move_name = sim.rl_index_to_name.get(idx, "???")
#     #     print(move_name, "MAN")
#     #     state, reward, terminated, truncated, info = sim.step(move_name)  # pass name, not idx
#     #     print(f"Action {idx} -> {move_name} | Reward: {reward:.2f} | Terminated: {terminated}")


