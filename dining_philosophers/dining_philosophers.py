"""
Dining Philosophers — Silberschatz monitor solution
CPSC 5042 — OS Concepts 10th ed., Ch. 7

Synchronization:
  mutex       Semaphore(1)  guards all state[] transitions
  self_sem[i] Semaphore(0)  blocks philosopher i when hungry but unable to eat

Deadlock-free:  all state changes serialised through mutex; circular wait impossible.
Starvation-free: putdown() calls test() on both neighbours so no philosopher is skipped.

Usage: python dining_philosophers.py [num_philosophers] [num_rounds]
"""

import sys
import threading
import time
import random

THINKING = "THINKING"
HUNGRY   = "HUNGRY"
EATING   = "EATING"

# Shared state — initialised in main()
n        = 0
state    = []   # state[i] in {THINKING, HUNGRY, EATING}
mutex    = None # Semaphore(1) — guards state[]
self_sem = []   # self_sem[i] = Semaphore(0); philosopher i blocks here when hungry


def test(i: int) -> None:
    """
    If philosopher i is HUNGRY and neither neighbour is EATING,
    transition i to EATING and unblock self_sem[i].

    Must be called while mutex is held.
    """
    left  = (i - 1) % n
    right = (i + 1) % n
    if state[i] == HUNGRY and state[left] != EATING and state[right] != EATING:
        state[i] = EATING
        self_sem[i].release()


def pickup(i: int) -> None:
    """Philosopher i picks up both chopsticks (blocks if either neighbour is eating)."""
    mutex.acquire()
    state[i] = HUNGRY
    test(i)                 # try to move straight to EATING
    mutex.release()
    self_sem[i].acquire()   # block here if test() didn't grant eating rights


def putdown(i: int) -> None:
    """Philosopher i puts down both chopsticks and wakes eligible neighbours."""
    left  = (i - 1) % n
    right = (i + 1) % n
    mutex.acquire()
    state[i] = THINKING
    test(left)              # wake left neighbour if it can now eat
    test(right)             # wake right neighbour if it can now eat
    mutex.release()


def print_status() -> None:
    """Print philosopher states and chopstick usage. Must be called while print_lock is held."""
    chopstick_in_use = ["in use" if state[i] == EATING or state[(i + 1) % n] == EATING
                        else "free" for i in range(n)]
    print(f"  States    : {[f'P{i}={state[i]}' for i in range(n)]}")
    print(f"  Chopsticks: {[f'C{i}:{chopstick_in_use[i]}' for i in range(n)]}")


def philosopher(phil_id: int, rounds: int, print_lock: threading.Lock) -> None:
    """Thread function for a single philosopher."""
    for _ in range(rounds):
        # THINKING
        with print_lock:
            print(f"Philosopher {phil_id} is THINKING")
        time.sleep(random.uniform(0.5, 1.5))

        # HUNGRY → attempt pickup (may block inside pickup())
        with print_lock:
            print(f"Philosopher {phil_id} is HUNGRY")
        pickup(phil_id)

        # EATING (granted by test() inside pickup)
        with print_lock:
            print(f"Philosopher {phil_id} is EATING")
            print_status()
        time.sleep(random.uniform(0.5, 1.5))

        # Done eating — put down chopsticks, wake neighbours
        putdown(phil_id)

    with print_lock:
        print(f"Philosopher {phil_id} finished all rounds.")


def main() -> None:
    global n, state, mutex, self_sem

    n      = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    if n < 2:
        print("Need at least 2 philosophers.")
        sys.exit(1)

    print(f"\nDining Philosophers — {n} philosophers, {rounds} rounds each\n")

    # Initialise shared state
    state    = [THINKING] * n
    mutex    = threading.Semaphore(1)
    self_sem = [threading.Semaphore(0) for _ in range(n)]

    print_lock = threading.Lock()

    threads = [
        threading.Thread(target=philosopher, args=(i, rounds, print_lock))
        for i in range(n)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print("\nAll philosophers have finished dining.")


if __name__ == "__main__":
    main()
