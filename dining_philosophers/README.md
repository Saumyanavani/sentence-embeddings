# Dining Philosophers — CPSC 5042

## How to run

```bash
# default: 5 philosophers, 3 rounds each
python dining_philosophers.py

# custom: 7 philosophers, 5 rounds each
python dining_philosophers.py 7 5
```

Requires Python 3.9+ (uses built-in `threading` only — no third-party packages).

---

## Synchronization mechanisms

| Mechanism | Purpose |
|-----------|---------|
| `threading.Semaphore(1)` per chopstick | Binary semaphore — only one philosopher may hold a chopstick at a time |
| `threading.Semaphore(n-1)` — "room" | Limits concurrent diners to N-1, breaking circular-wait |
| `threading.Lock` — `print_lock` | Serialises console output so lines don't interleave |

---

## How deadlock is avoided

Classic deadlock arises when every philosopher picks up their left chopstick simultaneously and waits forever for the right one (circular wait).
The **room semaphore** (capacity = N-1) ensures at least one philosopher is always kept out, so the remaining N-1 cannot form a complete circular-wait chain.
Because one seat is always "open," at least one philosopher will always be able to acquire both chopsticks.

## How starvation is minimised

- Random sleep durations for both thinking and eating spread demand evenly across time.
- Each philosopher acquires chopsticks in the same order (left then right), and the room semaphore prevents any permanent exclusion.

---

## Challenges and resolutions

| Challenge | Resolution |
|-----------|-----------|
| Deadlock with naive left-then-right pickup | Added room semaphore capped at N-1 |
| Interleaved print output | Wrapped all print calls with a shared `threading.Lock` |
| Race on `chopstick_owners` display array | Updates are done while the semaphore is held, before/after release, keeping the display consistent |
