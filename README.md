# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Running `python3 main.py` produces the output below, which demonstrates both chronological sorting and priority sorting using the Scheduler.

```
Today's Schedule
----------------

08:00 AM - Morning feeding
Pet: Mochi
Duration: 10 minutes
Priority: high
Frequency: daily

10:15 AM - Vet checkup
Pet: Luna
Duration: 45 minutes
Priority: high
Frequency: once

12:00 PM - Litter box cleaning
Pet: Luna
Duration: 15 minutes
Priority: low
Frequency: weekly

06:30 PM - Evening walk
Pet: Mochi
Duration: 30 minutes
Priority: medium
Frequency: daily

Tasks by Priority
-----------------

HIGH - Morning feeding (Mochi)
Time: 08:00 AM
Duration: 10 minutes
Frequency: daily

HIGH - Vet checkup (Luna)
Time: 10:15 AM
Duration: 45 minutes
Frequency: once

MEDIUM - Evening walk (Mochi)
Time: 06:30 PM
Duration: 30 minutes
Frequency: daily

LOW - Litter box cleaning (Luna)
Time: 12:00 PM
Duration: 15 minutes
Frequency: weekly
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

The `Scheduler` organizes a pet owner's tasks into an actionable daily plan. It considers due dates and completion status, respects the owner's preferred care hours and unavailable-time blocks, creates the next occurrence of recurring tasks, and flags conflicts between tasks. The table below documents each implemented scheduling feature and the method(s) responsible for it.

| Feature | Method(s) | Behavior |
|---------|-----------|----------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | Time sorting orders tasks by `scheduled_time` when it is available and otherwise by `preferred_time`. Priority sorting orders tasks high, then medium, then low. |
| Task filtering | `Scheduler.filter_tasks()` | Filters tasks by due date, pet name, and completion status. Only the filters that are not `None` are applied, so any combination can be used. |
| Owner availability | `Scheduler.is_owner_available()` | A task must fit completely inside the owner's preferred care hours and must not overlap any unavailable-time block. Both normal and overnight ranges are supported. Midnight crossing is determined automatically by comparing the start and end times, so no separate `crosses_midnight` attribute is stored. Equal preferred start and end times mean an unrestricted, full-day preferred window. |
| Conflict detection | `Scheduler.detect_conflicts()` | Detects overlapping tasks that share the same due date, using each task's duration to calculate its full time interval. Conflicts that cross midnight are supported. Tasks that only touch at a boundary are not treated as conflicts. Conflicting tasks remain in the schedule and produce warning messages. |
| Recurring tasks | `Task.create_next_occurrence()`, `Scheduler.create_recurring_task()`, `Scheduler.mark_task_complete()` | Completing a daily task creates a new occurrence one day later; completing a weekly task creates a new occurrence seven days later. A one-time task does not create another occurrence. The next occurrence is a brand-new `Task` object that starts out incomplete. |
| Daily schedule generation | `Scheduler.generate_daily_schedule()` | Retrieves the incomplete tasks for one date and sorts them chronologically. Tasks are scheduled when the owner is available, and skipped when they fall outside preferred hours or inside an unavailable block, with a reason recorded for each skipped task. Conflicts among the scheduled tasks are detected. The previous scheduled, skipped, and warning lists are reset before a new plan is generated. |
| Schedule explanations | `Scheduler.explain_task_placement()`, `Scheduler.get_skipped_tasks()` | Explains why a task was scheduled or skipped. Returns the skipped tasks without exposing the original mutable list. |

### Scheduling Tradeoffs

A few deliberate design decisions shape how the scheduler behaves:

- **Conflicts are surfaced, not resolved.** When two tasks overlap, both stay in the schedule and a warning message is shown. PawPal+ does not delete a task or automatically move it to another time; the owner decides what to do.
- **Unavailable tasks are skipped, not relocated.** A task that falls outside the preferred care hours or inside an unavailable block is skipped with an explanation. The scheduler does not search for an alternative open slot to move it into.
- **Exact intervals, no optimization.** The scheduler uses each task's real start time and duration to reason about availability and conflicts, but it does not try to optimize the plan by rearranging tasks or filling open gaps. It reports the plan as-is.
- **Clarity over aggressive refactoring.** The availability logic keeps some repeated calculations visible (for example, converting times to minutes and normalizing overnight ranges). Leaving that code readable was easier to follow — and safer — than refactoring logic that already passes its tests.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

