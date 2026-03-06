"""
Dining Philosophers Problem
CPSC 5042 - Computer Systems Principles II

Solution uses:
  - threading.Semaphore (value=1) per chopstick — acts as a binary semaphore/mutex
  - A global semaphore that limits concurrent diners to (N-1) to prevent deadlock

Deadlock prevention:
  Allowing at most N-1 philosophers to attempt eating simultaneously guarantees
  that at least one philosopher can always acquire both chopsticks, breaking the
  circular-wait condition.

Starvation mitigation:
  Random think/eat durations spread access fairly over time.

Usage:
  python dining_philosophers.py [num_philosophers] [num_rounds]

  num_philosophers : number of philosophers (default 5)
  num_rounds       : how many eat/think cycles each philosopher completes (default 3)
"""

import sys
import threading
import time
import random

# ── State labels ──────────────────────────────────────────────────────────────
THINKING = "thinking"
HUNGRY   = "hungry"
EATING   = "eating"


def print_status(states: list[str], chopstick_owners: list[int], n: int) -> None:
    """Print a snapshot of all philosopher states and chopstick usage."""
    chopstick_str = []
    for i in range(n):
        owner = chopstick_owners[i]
        chopstick_str.append(f"C{i}:Phil{owner}" if owner != -1 else f"C{i}:free")
    print(f"  States : {[f'P{i}={states[i][:3].upper()}' for i in range(n)]}")
    print(f"  Sticks : {chopstick_str}")


def philosopher(
    phil_id: int,
    n: int,
    chopsticks: list[threading.Semaphore],
    room: threading.Semaphore,
    states: list[str],
    chopstick_owners: list[int],
    print_lock: threading.Lock,
    rounds: int,
) -> None:
    """
    Thread function for a single philosopher.

    Chopstick indices:
      left  = phil_id
      right = (phil_id + 1) % n
    """
    left  = phil_id
    right = (phil_id + 1) % n

    for _ in range(rounds):
        # ── THINKING ──────────────────────────────────────────────────────────
        states[phil_id] = THINKING
        with print_lock:
            print(f"Philosopher {phil_id} is THINKING")
        time.sleep(random.uniform(0.5, 1.5))

        # ── HUNGRY — enter the room (at most N-1 philosophers allowed in) ─────
        states[phil_id] = HUNGRY
        with print_lock:
            print(f"Philosopher {phil_id} is HUNGRY")
            print_status(states, chopstick_owners, n)

        room.acquire()                    # blocks if N-1 already inside

        # ── Pick up chopsticks (always left then right) ───────────────────────
        chopsticks[left].acquire()
        chopstick_owners[left] = phil_id

        chopsticks[right].acquire()
        chopstick_owners[right] = phil_id

        # ── EATING ────────────────────────────────────────────────────────────
        states[phil_id] = EATING
        with print_lock:
            print(f"Philosopher {phil_id} is EATING")
            print_status(states, chopstick_owners, n)
        time.sleep(random.uniform(0.5, 1.5))

        # ── Put down chopsticks ───────────────────────────────────────────────
        chopstick_owners[left]  = -1
        chopstick_owners[right] = -1
        chopsticks[left].release()
        chopsticks[right].release()

        room.release()                    # leave the room

    states[phil_id] = THINKING           # finished all rounds
    with print_lock:
        print(f"Philosopher {phil_id} finished all rounds.")


def main() -> None:
    # ── Parse arguments ───────────────────────────────────────────────────────
    n      = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    if n < 2:
        print("Need at least 2 philosophers.")
        sys.exit(1)

    print(f"\nDining Philosophers — {n} philosophers, {rounds} rounds each\n")

    # ── Shared state ──────────────────────────────────────────────────────────
    # One binary semaphore per chopstick
    chopsticks      = [threading.Semaphore(1) for _ in range(n)]
    # Room semaphore: allows at most (n-1) philosophers to attempt eating
    room            = threading.Semaphore(n - 1)
    states          = [THINKING] * n
    chopstick_owners = [-1] * n          # -1 means chopstick is free
    print_lock      = threading.Lock()

    # ── Create and start threads ──────────────────────────────────────────────
    threads = [
        threading.Thread(
            target=philosopher,
            args=(i, n, chopsticks, room, states, chopstick_owners, print_lock, rounds),
            daemon=True,
        )
        for i in range(n)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("\nAll philosophers have finished dining.")


if __name__ == "__main__":
    main()
