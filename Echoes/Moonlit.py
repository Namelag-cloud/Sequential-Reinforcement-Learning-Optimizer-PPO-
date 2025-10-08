from Echoes.Echo import EchoSet

class MoonlitClouds(EchoSet):
    def __init__(self, equipped_count):
        super().__init__("Moonlit Clouds", equipped_count)
        self.buff_name = "Moonlit Clouds 5pc"
        self.stack_duration = 900  # 15s
        self.max_stacks = 1
        self.queued_buff = None  # Buff queued when Outro is triggered

    def apply_2pc(self, resonator):
        if self.equipped_count >= 2:
            resonator.add_buff("Moonlit Clouds 2pc", {"ER": 10})

    def apply_5pc(self, resonator):
        # This method is just here to satisfy interface
        pass

    def check_activation(self, last_action, current_frame, resonator):
        if self.equipped_count < 5 or not last_action:
            return
        
        if not isinstance(getattr(resonator, "echo_set", None), self.__class__):
            return

        trigger = last_action.get("trigger", "")
        if trigger == "Outro":
            # print(f"[DEBUG - {self.name}] Queuing buff due to Outro from {resonator.name}")
            self.queued_buff = {
                "buff_name": self.buff_name,
                "stats": {"ATK%": 22.5},
                "duration_frames": self.stack_duration,
                "scope": "next"
            }

    def reset(self):
        super().reset()
        self.queued_buff = None
    
    MoonlitClouds_Buffs = [
        {
            "buff_name": "Moonlit Clouds 2pc",
            "stat": {"ER": 0.10},            # +10% Energy Regen
            "duration": float("inf"),
            "scope": "self",
            "max_stacks": 1
        },
        {
            "buff_name": "Moonlit Clouds 5pc",
            "stat": {"ATK%": 22.5},          # +22.5% ATK
            "duration": 900,                 # 15s * 60fps
            "scope": "next",                 # goes to the next unit after Outro
            "max_stacks": 1
        }
    ]



class ImpermanenceHeron:
    def __init__(self):
        self.name = "Echo: Impermanence Heron"
        self.cooldown = 1200  # 20s in frames
        self.buff_window = 900  # 15s in frames
        self.buff_duration = 900  # 15s duration
        self.energy_restore = 10

        self.move_tap = f"{self.name} (Tap)"
        self.move_hold = f"{self.name} (Hold)"
        self.move_name = self.move_tap
        self.queued_buff = None

    def equip_to(self, unit, move_data, current_frame):
        unit.moves[self.move_tap] = {
            "Skill": self.move_tap,
            "DMG %": {"ATK": "310.56%"},
            "Time": 1.2,
            "Modifier": "HaEc",
            "Trigger": "EchoSkill",
            "Hits": 1,
            "Forte": 0,
            "Concerto": 0,
            "Resonance": 0,
            "Freeze Timer": 0,
            "Cooldown": 20,
            "Healing": False,
            "Echo": True,
            "Start": ["GR", "AR"],
            "End": ["GR"],
            "Stamina Cost": 0,
            "Index": 66
        }

        unit.moves[self.move_hold] = {
            "Skill": self.move_hold,
            "DMG %": {"ATK": "55.73%"},
            "Time": 0.5,
            "Modifier": "HaEc",
            "Trigger": "EchoSkill",
            "Hits": 1,
            "Forte": 0,
            "Concerto": 0,
            "Resonance": 0,
            "Freeze Timer": 0,
            "Cooldown": 20,
            "Healing": False,
            "Echo": True,
            "Start": ["GR", "AR"],
            "End": ["AR", "GR"],
            "Stamina Cost": 5,
            "Index": 67  # last index 

        }

        # Init tracking flags
        unit.heron_echo_instance = self
        unit.heron_tap_used_frame = None
        unit.heron_outro_used_frame = None
        unit.heron_last_used_frame = -float("inf")

        # print(f"[DEBUG - {self.name}] Equipped to {unit.name} with tap/hold variants")

    def can_use(self, current_frame):
        return current_frame - self.last_used_frame() >= self.cooldown

    def last_used_frame(self):
        # used by can_use and logic checker
        return self._last_used_frame if hasattr(self, "_last_used_frame") else -float("inf")

    def use(self, unit, current_frame, is_hold=False):
        if not self.can_use(current_frame):
            # print(f"[DEBUG - {self.name}] Cannot use — on cooldown at frame {current_frame}")
            return False

        # Update last-used state
        self._last_used_frame = current_frame
        unit.heron_last_used_frame = current_frame

        if not is_hold:
            # Tap = energy restore + sets Tap flag
            unit.gain_energy(self.energy_restore)
            unit.heron_tap_used_frame = current_frame
            # print(f"[DEBUG - {self.name}] Tap used at {current_frame}, energy restored and buff window started")

        # else:
        #     print(f"[DEBUG - {self.name}] Hold used at {current_frame}")

        return True

    def on_outro(self, unit, current_frame):
        unit.heron_outro_used_frame = current_frame
        # print(f"[DEBUG - {self.name}] Outro triggered at {current_frame}")
        self.check_buff_eligibility(unit, current_frame)

    def check_buff_eligibility(self, unit, current_frame):
        tap_frame = unit.heron_tap_used_frame
        outro_frame = unit.heron_outro_used_frame
        last_echo_use = unit.heron_last_used_frame

        # All conditions must be true
        if tap_frame is None or outro_frame is None:
            # print(f"[DEBUG - {self.name}] Buff not queued — Tap or Outro frame missing")
            return

        if outro_frame - tap_frame > self.buff_window:
            # print(f"[DEBUG - {self.name}] Buff not queued — Outro used after buff window expired")
            return

        if last_echo_use < tap_frame:
            # print(f"[DEBUG - {self.name}] Buff not queued — Tap not from recent Echo use")
            return

        # Queue the buff
        self.queued_buff = {
            "buff_name": "Impermanence Heron Outro Buff",
            "stats": {"All DMG": 12.0},
            "duration_frames": self.buff_duration,
            "scope": "next"
        }

        # print(f"[DEBUG - {self.name}] Buff queued: +12% All DMG for next unit")

    ImpermanenceHeron_Buffs = [
        {
            "buff_name": "Impermanence Heron Outro Buff",
            "stat": {"All DMG": 12.0},       # +12% All DMG
            "duration": 900,                 # 15s * 60fps
            "scope": "next",
            "max_stacks": 1
        }
    ]