from Echoes.Echo import EchoSet


class HavocEclipse(EchoSet):
    def __init__(self, equipped_count):
        super().__init__("Havoc Eclipse", equipped_count)
        self.resonator_stacks = {}
        self.max_stacks = 4
        self.stack_duration = 900  # 15 sec @ 60 fps
        self.buff_name = "Havoc Eclipse 5pc"

    def apply_2pc(self, resonator):
        if self.equipped_count >= 2:
            resonator.add_buff("Havoc Eclipse 2pc", {"Havoc DMG": 10})

            # add_buff is resonator class function here, which updates "active buffs" with buffs as a dict 


    def apply_5pc(self, resonator):
        # Check if the equipped_count is 5
        if self.equipped_count == 5:
            # Check if the resonator has a history
            if resonator.history:
                # Get the last move name from the resonator's history
                last_move_name = resonator.history[-1][0]
                # Get the move data from the resonator's moves
                move_data = resonator.moves.get(last_move_name, {})
                # Get the trigger from the move data
                trigger = move_data.get("Trigger", "")
                # Check if the trigger is "Basic" or "Heavy"
                if trigger in ["Basic", "Heavy"]:
                    # Get the number of hits from the move data
                    hits = int(move_data.get("Hits", 1))
                    # Calculate the havoc_bonus
                    havoc_bonus = min(7.5 * hits, 30)
                    # Add the havoc_bonus to the resonator's buffs
                    resonator.add_buff("Havoc Eclipse 5pc", {"Havoc DMG": havoc_bonus}) # send this to a dict on add_buff on resonator class
                      

    def get_buff_stats(self, resonator, buff_name): 
        buff = self.active_buffs.get(buff_name)
        if buff:
            return buff.get("stats", {})
        return {}


    def check_activation(self, last_action, current_frame, resonator): # fucks with add_Echo_buff function in echo class
        if self.equipped_count < 5:
            return
        if not last_action:
            return


        last_move_name = last_action.get("name", "")
        move_data = resonator.moves.get(last_move_name, {})
        trigger = move_data.get("Trigger", "")

        
        if trigger in ["Basic", "Heavy"]:
            hits = int(move_data.get("Hits", 1))
            

            self.last_stack_frame = current_frame
            res_key = resonator.name
            prev_stack = min(self.resonator_stacks.get(res_key, 0),4)
            new_stack = min(prev_stack + hits, self.max_stacks)
            stacks_to_add = new_stack - prev_stack
            self.resonator_stacks[res_key] = new_stack
            self.add_echo_buff(self.buff_name, {"Havoc DMG": 7.5}, self.stack_duration, current_frame, stacks_to_add)
            

    def remove_buff(self, buff_name, stacks_to_remove=1, current_frame=0):
        if buff_name in self.active_buffs:
            buff = self.active_buffs[buff_name]
            current_stacks = buff.get('stacks', 1)
            if current_stacks > stacks_to_remove:
                new_stack_count = current_stacks - stacks_to_remove
                buff['stacks'] = new_stack_count
                buff['stats'] = {k: v / current_stacks * new_stack_count for k, v in buff['stats'].items()}
            else:
                del self.active_buffs[buff_name]



    def reset(self):
        super().reset()
        self.last_stack_frame = None

    
    HavocEclipse_Buffs = [
        {
            "buff_name": "Havoc Eclipse 2pc",
            "stat": {"Havoc DMG": 10.0},    # +10% Havoc DMG
            "duration": float("inf"),
            "scope": "self",
            "max_stacks": 1
        },
        {
            "buff_name": "Havoc Eclipse 5pc",
            "stat": {"Havoc DMG": 7.5},     # +7.5% Havoc DMG per stack
            "duration": 900,                # 15s * 60fps
            "scope": "self",
            "max_stacks": 4                 # caps at 4 stacks
        }
    ]


class NightmareCrownless:
    def __init__(self):
        self.name = "Echo: Nightmare Crownless"
        self.passive_buff = {
            "buff_name": "Nightmare Passive",
            "stats": {
                "Havoc DMG": 12.0,
                "Basic DMG": 12.0
            }
        }
        self.cooldown = 720  # 12s in frames
        self.max_charges = 3
        self.current_charges = 3
        self.last_used_frames = []
        self.temp_buff_duration = 120  # 2s in frames
        self.last_hit_frame = None
        self.move_name = self.name 

    def equip_to(self, unit, move_data, current_frame):
        """
        Grants the passive buff to the unit and appends the Echo move to move_data.
        """
        # Add the passive buff to the unit
        unit.add_buff(
            self.passive_buff["buff_name"],
            self.passive_buff["stats"],
            duration_frames=float("inf"),
            current_frame=current_frame
        )

        # Append the Echo move to move_data
        unit.moves[self.name] = {
            "Skill": self.name,
            "DMG %": { "ATK": "264.6%" },
            "Time": 1.0,
            "Modifier": "HaEc",
            "Trigger": "EchoSkill",
            "Hits": 1,
            "Forte": 0,
            "Concerto": 0,
            "Resonance": 0,
            "Freeze Timer": 0,
            "Cooldown": 12,
            "Index": 35,
            "Healing": False,
            "Start": ["GR", "AR"],
            "End": ["GR"]
        }

       
        # print(f"[DEBUG] Equipped {self.name} and registered Echo move to {unit.name}.")

    def can_use(self, current_frame):
        """
        Returns whether there's a charge available.
        """
        self._regenerate_charges(current_frame)
        return self.current_charges > 0

    def on_move_used(self, current_frame):
        """
        Call this when the move is used — reduces charge and logs usage.
        """
        self.last_used_frames.append(current_frame)
        self.current_charges = max(0, self.current_charges - 1)
        self.last_hit_frame = current_frame

    def _regenerate_charges(self, current_frame):
        # Only consider used charges that are still on cooldown
        regenerated = 0
        new_last_used = []

        for t in self.last_used_frames:
            if current_frame - t >= self.cooldown:
                # This use is now off cooldown, restore a charge
                if self.current_charges < self.max_charges:
                    self.current_charges += 1
                    regenerated += 1
            else:
                new_last_used.append(t)

        self.last_used_frames = new_last_used

        # if regenerated > 0:
        #     print(f"[DEBUG - {self.name}] Regenerated {regenerated} charge(s) at frame {current_frame}")


    def get_bonus_multiplier(self, current_frame):
        """
        +20% if reused within 2s of last hit.
        """
        if self.last_hit_frame and current_frame - self.last_hit_frame <= self.temp_buff_duration:
            return 1.2
        return 1.0


    def use(self, unit, current_frame):
        if not self.can_use(current_frame):
            # print(f"[DEBUG - {self.name}] Cannot use — no charges available")
            return False, False  # not used, no buff

        # Check bonus condition
        bonus_applied = False
        if self.get_bonus_multiplier(current_frame) > 1.0:
            unit.add_buff(
                "Echo Skill Bonus",
                {"Havoc Echo DMG": 20.0},
                duration_frames=120,  # 2s
                current_frame=current_frame
            )
            bonus_applied = True
        
        self.on_move_used(current_frame)
        # print(f"[DEBUG - {self.name}] Used at frame {current_frame}")

        return True, bonus_applied


    NightmareCrownless_Buffs = [
        {
            "buff_name": "Nightmare Passive",
            "stat": {
                "Havoc DMG": 12.0,
                "Basic DMG": 12.0
            },
            "duration": float("inf"),
            "scope": "self",
            "max_stacks": 1
        },
        {
            "buff_name": "Echo Skill Bonus",
            "stat": {"Havoc Echo DMG": 20.0}, # Only applies if reused within 2s
            "duration": 120,                  # 2s * 60fps
            "scope": "self",
            "max_stacks": 1
        }
    ]