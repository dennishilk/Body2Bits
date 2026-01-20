import time
import sys
import argparse
import re

from board import WiiBalanceBoard
from motion import MotionDetector, MotionEvent
from state import StateMachine, AlarmState
from sound import AlarmSound
import config


TICK_HZ = 30
DT = 1.0 / TICK_HZ


# -----------------------------
# Time parsing helpers
# -----------------------------
def parse_delay(value: str) -> float:
    """
    Parse combined time strings like:
    - 10s
    - 5m
    - 2h
    - 8h10m
    - 1h30m
    - 45m20s
    """
    value = value.strip().lower()

    pattern = re.compile(r"(\d+)([hms])")
    matches = pattern.findall(value)

    if not matches:
        raise ValueError(
            "Invalid time format. Use formats like 10s, 5m, 2h, or 8h10m."
        )

    total_seconds = 0

    for amount, unit in matches:
        amount = int(amount)
        if unit == "h":
            total_seconds += amount * 3600
        elif unit == "m":
            total_seconds += amount * 60
        elif unit == "s":
            total_seconds += amount

    return total_seconds


def wait_before_alarm(delay_sec: float):
    print(f"Alarm scheduled in {int(delay_sec)} seconds.")
    try:
        while delay_sec > 0:
            mins, secs = divmod(int(delay_sec), 60)
            sys.stdout.write(
                f"\rStarting in {mins:02d}:{secs:02d} ..."
            )
            sys.stdout.flush()
            time.sleep(1)
            delay_sec -= 1
        print("\n")
    except KeyboardInterrupt:
        print("\nAborted before alarm.")
        sys.exit(0)


# -----------------------------
# UI helpers
# -----------------------------
def clear():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def render(sm: StateMachine, last_event, weight_kg: float):
    clear()

    print("\n\n\n")
    print("        === ALARM FROM HELL 😈 ===\n")

    if sm.state == AlarmState.PANIC:
        print("\n\n")
        print("            GET UP.\n")
        print("            GET ON")
        print("            THE BOARD.\n\n")

    elif sm.state == AlarmState.COMPLIANCE:
        print("\n\n")
        print("            SQUATS\n")
        print(f"            {sm.ctx.squats_done} / {sm.required_squats}\n\n")

    elif sm.state == AlarmState.SILENCE:
        print("\n\n")
        print("            DO NOT MOVE.\n")
        print(f"            {sm.ctx.still_seconds:.1f} s\n\n")

    elif sm.state == AlarmState.DONE:
        print("\n\n")
        print("            GOOD.\n\n")

    if last_event and last_event != MotionEvent.NONE:
        print(f"            EVENT: {last_event.name}")

    print(sm.status())


# -----------------------------
# Main
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="Alarm from Hell")
    parser.add_argument(
        "--in",
        dest="delay",
        help="Start alarm after delay (e.g. 10s, 2m, 8h10m)",
    )

    args = parser.parse_args()

    if args.delay:
        delay_sec = parse_delay(args.delay)
        wait_before_alarm(delay_sec)

    # ---- REAL ALARM STARTS HERE ----

    board = WiiBalanceBoard()
    detector = MotionDetector()
    sound = AlarmSound()

    sm = StateMachine(
        required_squats=config.REQUIRED_SQUATS,
        required_still_time=config.REQUIRED_STILL_TIME_SEC,
    )

    print("Connecting to Wii Balance Board...")
    board.connect()
    print("Connected.\n")

    alarm_triggered = False
    last_render = time.time()
    last_event = None

    try:
        for sample in board.read_samples():
            now = time.time()

            if not alarm_triggered:
                sm.trigger_alarm()
                alarm_triggered = True

            weight_kg = config.raw_to_kg(sample["total"])

            # Sound control
            if sm.state in (AlarmState.PANIC, AlarmState.COMPLIANCE):
                sound.start(sm.ctx.escalation_level)
            elif sm.state == AlarmState.SILENCE:
                sound.start(max(0, sm.ctx.escalation_level - 1))
            else:
                sound.stop()

            # Board presence
            if weight_kg < config.MIN_WEIGHT_KG:
                sm.board_left()
                last_event = None
            else:
                if sm.state == AlarmState.PANIC:
                    sm.weight_detected()

                event = detector.update(weight_kg, now)
                last_event = event

                if event in (MotionEvent.SQUAT, MotionEvent.STOMP):
                    sm.squat_detected()
                elif event == MotionEvent.STILLNESS:
                    sm.stillness_tick(DT)

            if sm.state == AlarmState.SILENCE:
                sm.stillness_tick(DT)

            if now - last_render >= 0.1:
                render(sm, last_event, weight_kg)
                last_render = now

            if sm.state == AlarmState.DONE:
                sound.stop()
                break

            time.sleep(DT)

    except KeyboardInterrupt:
        sound.stop()
        clear()
        print("Aborted.")
    finally:
        board.close()


if __name__ == "__main__":
    main()
