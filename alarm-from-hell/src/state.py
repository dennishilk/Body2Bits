from enum import Enum, auto
from dataclasses import dataclass


class AlarmState(Enum):
    SLEEP = auto()
    PANIC = auto()
    COMPLIANCE = auto()
    SILENCE = auto()
    DONE = auto()


@dataclass
class AlarmContext:
    """
    Mutable context shared across states.
    This holds progress and temporary counters.
    """
    squats_done: int = 0
    still_seconds: float = 0.0
    escalation_level: int = 0


class StateMachine:
    def __init__(self, required_squats: int, required_still_time: float):
        self.state = AlarmState.SLEEP
        self.ctx = AlarmContext()
        self.required_squats = required_squats
        self.required_still_time = required_still_time

    # --- State transitions ---

    def trigger_alarm(self):
        if self.state == AlarmState.SLEEP:
            self.state = AlarmState.PANIC

    def weight_detected(self):
        if self.state == AlarmState.PANIC:
            self.state = AlarmState.COMPLIANCE

    def squat_detected(self):
        if self.state == AlarmState.COMPLIANCE:
            self.ctx.squats_done += 1
            if self.ctx.squats_done >= self.required_squats:
                self.state = AlarmState.SILENCE
                self.ctx.still_seconds = 0.0

    def stillness_tick(self, dt: float):
        """
        Called repeatedly while standing still.
        dt = time delta in seconds.
        """
        if self.state == AlarmState.SILENCE:
            self.ctx.still_seconds += dt
            if self.ctx.still_seconds >= self.required_still_time:
                self.state = AlarmState.DONE

    def movement_detected(self):
        """
        Any significant movement during SILENCE is failure.
        """
        if self.state == AlarmState.SILENCE:
            self.state = AlarmState.COMPLIANCE
            self.ctx.still_seconds = 0.0

    def board_left(self):
        """
        Leaving the board is always punished.
        """
        if self.state in (AlarmState.COMPLIANCE, AlarmState.SILENCE):
            self.state = AlarmState.PANIC
            self.ctx.squats_done = 0
            self.ctx.still_seconds = 0.0
            self.ctx.escalation_level += 1

    # --- Debug / Introspection ---

    def status(self) -> str:
        return (
            f"state={self.state.name} | "
            f"squats={self.ctx.squats_done}/{self.required_squats} | "
            f"still={self.ctx.still_seconds:.1f}/{self.required_still_time}s | "
            f"escalation={self.ctx.escalation_level}"
        )
