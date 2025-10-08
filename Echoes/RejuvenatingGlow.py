from Echoes.Echo import EchoSet

class RejuvenatingGlow(EchoSet):
    def __init__(self, equipped_count):
        super().__init__("Rejuvenating Glow", equipped_count)
        self.buff_name = "Rejuvenating Glow 5pc"
        self.stack_duration = 1800  # 30s * 60fps
        self.max_stacks = 1
        self.queued_teamwide_buff = None

    def apply_2pc(self, resonator):
        if self.equipped_count >= 2:
            resonator.add_buff("Rejuvenating Glow 2pc", {"Healing Bonus": 10.0})

    def apply_5pc(self, resonator):
        # Logic handled in check_activation on healing move
        pass

    def check_activation(self, move_data, current_frame, resonator):
        if self.equipped_count < 5:
            return

        if not isinstance(getattr(resonator, "echo_set", None), self.__class__):
            return

        if move_data and move_data.get("Healing", False):
            # print(f"[DEBUG - {self.name}] Queuing ATK buff from {resonator.name} after healing: {move_data.get('Skill', 'Unknown')}")
            self.queued_buff = {
                "buff_name": self.buff_name,
                "stats": {"ATK%": 15.0},
                "duration_frames": self.stack_duration,
                "scope": "global"
            }

    RejuvenatingGlow_Buffs = [
        {
            "buff_name": "Rejuvenating Glow 2pc",
            "stat": {"Healing Bonus": 0.10},  # +10% Healing Bonus
            "duration": float("inf"),        # permanent as long as equipped
            "scope": "self",
            "max_stacks": 1
        },
        {
            "buff_name": "Rejuvenating Glow 5pc",
            "stat": {"ATK%": 0.15},          # +15% ATK
            "duration": 1800,                # 30s * 60fps
            "scope": "global",
            "max_stacks": 1
        }
    ]


    def reset(self):
        super().reset()
        self.queued_teamwide_buff = None


class FallacyOfNoReturn:
    def __init__(self):
        self.name = "Echo: Fallacy Of No Return"
        self.cooldown = 1200  # 20s in frames
        self.last_used_frame = -float("inf")
        self.buff_duration = 1200  # 20s in frames
        self.hold_stamina_cost = 30
        self.tap_stamina_cost = 10
        self.move_name = f"{self.name} (Tap)"
        self.move_hold = f"{self.name} (Hold)"
        self.passive_buff = {
            "buff_name": "Fallacy Passive",
            "stats": { "Energy Regen": 10.0 }
        }
        self.queued_buff = None

    def equip_to(self, unit, move_data, current_frame):
        unit.add_buff(
            self.passive_buff["buff_name"],
            self.passive_buff["stats"],
            duration_frames=float("inf"),
            current_frame=current_frame
        )

        unit.moves[self.move_name] = {
            "Skill": self.move_name,
            "DMG %": {"HP": "1.58%"},
            "Time": 0.0,
            "Modifier": "SpEc",
            "Trigger": "EchoSkill",
            "Hits": 1,
            "Forte": 0,
            "Concerto": 0,
            "Resonance": 0,
            "Freeze Timer": 0,
            "Cooldown": 20,
            "Healing": False,
            "Echo": True,
            "Stamina Cost": self.tap_stamina_cost,
            "Index": 65,
            "Start": ["GR", "AR"],
            "End": ["AR", "GR"],
        }

        unit.moves[self.move_hold] = {
            "Skill": self.move_hold,
            "DMG %": {"HP": "19.82%"},
            "Time": 3.5,
            "Modifier": "SpEc",
            "Trigger": "EchoSkill",
            "Hits": 1,
            "Forte": 0,
            "Concerto": 0,
            "Resonance": 0,
            "Freeze Timer": 0,
            "Cooldown": 20,
            "Healing": False,
            "Echo": True,
            "Stamina Cost": self.hold_stamina_cost,
            "Index": 64,
            "Start": ["GR", "AR"],
            "End": ["AR", "GR"],
        }

        # print(f"[DEBUG - {self.name}] Equipped to {unit.name}, registered Tap and Hold variants")

    def can_use(self, current_frame: int) -> bool:
        return (current_frame - self.last_used_frame) >= self.cooldown

    def use(self, unit, current_frame: int, is_hold: bool = False) -> bool:
        if not self.can_use(current_frame):
            # print(f"[DEBUG - {self.name}] Cannot use — still on cooldown at frame {current_frame}")
            return False

        self.last_used_frame = current_frame
        stamina_cost = self.hold_stamina_cost if is_hold else self.tap_stamina_cost
        move_type = "Hold" if is_hold else "Tap"

        # Properly queue the buff instead of applying it
        self.queued_buff = {
            "buff_name": "Fallacy Team Buff",
            "stats": {"ATK%": 10.0},
            "duration_frames": self.buff_duration,
            "scope": "global"
        }

        # print(f"[DEBUG - {self.name}] {move_type} used at frame {current_frame} — Queued +10% ATK to team")
        # print(f"[DEBUG - {self.name}] Stamina cost: {stamina_cost}")

        return True

    FallacyOfNoReturn_Buffs = [
        {
            "buff_name": "Fallacy Passive",
            "stat": {"Energy Regen": 0.10},  # +10% ER
            "duration": float("inf"),
            "scope": "self",
            "max_stacks": 1
        },
        {
            "buff_name": "Fallacy Team Buff",
            "stat": {"ATK%": 0.10},          # +10% ATK
            "duration": 1200,                # 20s * 60fps
            "scope": "global",
            "max_stacks": 1
        }
    ]