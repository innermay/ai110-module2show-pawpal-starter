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

## ✨ Features

PawPal+ currently supports the following features:

**Pets and owner**

- Add and manage multiple pets
- Store pet details, medical conditions, and dietary restrictions
- Set preferred care hours for the owner
- Set an unavailable sleeping-time block
- Support unavailable and preferred ranges that cross midnight
- Prevent duplicate pet names

**Tasks**

- Add care tasks with duration, priority, preferred time, due date, and frequency
- Edit the duration and priority of incomplete tasks
- Prevent duplicate task titles for the same pet and due date
- Mark tasks complete
- Automatically create the next daily or weekly occurrence when a recurring task is completed

**Scheduling**

- Sort tasks chronologically
- Sort tasks by priority
- View current tasks in added order, preferred-time order, or priority order
- Filter tasks by date, pet, and completion status
- Generate a daily schedule
- Skip tasks that fall outside the owner's available hours
- Explain why each task was scheduled or skipped
- Detect regular and overnight task conflicts
- Keep conflicting tasks in the schedule with clear warning messages

**Data**

- Pets and tasks are stored in `st.session_state` during the active Streamlit session. They are not saved permanently and may reset when the Streamlit session ends or restarts.

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

PawPal+ is verified by an automated test suite in `tests/test_pawpal.py`. The
tests use plain `pytest` assertions and create `Owner`, `Pet`, `Task`, and
`Scheduler` objects directly — no mocks, fixtures, parameterization, or
external testing libraries. A small `make_task()` helper reduces repeated
`Task` construction, and fixed dates are used so results are predictable.

Run the complete test suite from the project root:

```bash
python3 -m pytest
```

For a detailed, per-test listing, add the `-v` flag:

```bash
python3 -m pytest -v
```

### What is covered

The suite verifies the most important scheduling behaviors and edge cases:

| Behavior | Test(s) |
|----------|---------|
| Task status and pet task counts (Phase 2) | `test_mark_complete_changes_task_status`, `test_add_task_increases_pet_task_count` |
| Chronological sorting of out-of-order tasks | `test_sort_by_time_orders_tasks_chronologically` |
| Daily recurrence creates a correct next occurrence | `test_mark_daily_task_complete_creates_next_occurrence` |
| Weekly recurrence advances seven days | `test_weekly_recurrence_advances_seven_days` |
| A one-time task creates no next occurrence | `test_one_time_task_creates_no_next_occurrence` |
| Overlapping tasks produce exactly one warning | `test_overlapping_tasks_produce_one_warning` |
| Boundary-touching tasks do not conflict | `test_touching_tasks_do_not_conflict` |
| Conflicts that cross midnight are detected | `test_overnight_task_conflict_is_detected` |
| Tasks on different dates never conflict | `test_tasks_on_different_dates_do_not_conflict` |
| Available tasks are scheduled | `test_available_task_is_scheduled` |
| Tasks outside preferred hours are skipped | `test_task_outside_preferred_hours_is_skipped` |
| Tasks inside an overnight unavailable block are skipped | `test_task_in_overnight_unavailable_block_is_skipped` |
| Schedule state resets between generated plans | `test_generate_daily_schedule_resets_previous_state` |
| Skipped-task list is returned as a copy | `test_get_skipped_tasks_returns_a_copy` |

### Sample test output

```
============================= test session starts ==============================
platform darwin -- Python 3.13.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/mayrahernandez/Desktop/ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 15 items

tests/test_pawpal.py ...............                                     [100%]

============================== 15 passed in 0.02s ==============================
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

The following steps describe a realistic session with PawPal+ so a reader can follow along without watching a video:

1. The user enters their name and preferred care hours in the **Owner** section.
2. The user reviews or updates the default unavailable sleeping block of **10:00 PM to 7:00 AM** in the **Owner Availability** section.
3. The user adds a **Pet** with details such as name, species, breed, age, sex, activity level, medical conditions, and dietary restrictions.
4. The new pet appears in the **Your Pets** table.
5. The user creates **Tasks** for that pet with a title, description, duration, priority, preferred time, due date, and frequency.
6. The tasks appear in the **Current Tasks** table, where the user can change how the tasks are ordered — added order, preferred-time order, or priority order.
7. If needed, the user can edit an incomplete task's **duration** and **priority** in the **Edit a Task** section.
8. The user selects a date and clicks **Generate schedule**.
9. The `Scheduler` then:
   - Filters the incomplete tasks for the chosen date
   - Sorts them chronologically
   - Checks the owner's preferred care hours
   - Checks the unavailable-time blocks
   - Schedules the tasks the owner is available for
   - Skips unavailable tasks and records a reason for each
   - Displays conflict warnings for overlapping tasks
10. The user can mark a task complete in the **Complete a Task** section.
11. For a daily or weekly task, PawPal+ automatically creates the next occurrence (one day or seven days later). A one-time task does not create another occurrence.
12. Pets and tasks are stored in `st.session_state` during the active Streamlit session. They are not saved permanently and may reset when the Streamlit session ends or restarts.

### CLI Verification Example

Before the backend is used by the Streamlit UI, `main.py` verifies it directly from the terminal. Running `python3 main.py` builds a sample owner, pets, and tasks, then exercises the `Scheduler` end to end so the core logic can be checked without the UI. A concise sample of that output is shown below:

```
Generated Daily Schedule
------------------------

08:00 AM - Play session
Pet: Mochi
Duration: 30 minutes
Priority: medium

08:15 AM - Morning medication
Pet: Luna
Duration: 20 minutes
Priority: high

Conflict Warnings
-----------------

Conflict: 'Play session' for Mochi overlaps with
'Morning medication' for Luna.

Skipped Tasks
-------------

Title: Midnight snack
Pet: Mochi
Preferred time: 02:00 AM
Skipped reason: Owner is unavailable during this task's time.

Recurring Task Demo
-------------------

Original task: Morning feeding
Original completed: True
Original due date: 2026-07-13
New occurrence due date: 2026-07-14
New occurrence completed: False
```

**Screenshot or video** *(optional)*: Screenshots or a short video may also be included, but the written walkthrough and CLI output above are sufficient to understand how PawPal+ works.

