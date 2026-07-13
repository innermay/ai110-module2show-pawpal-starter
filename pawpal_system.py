"""PawPal+ core models and scheduling algorithms.

This module defines the four core classes for the PawPal+ pet-care
scheduling application: Owner, Pet, Task, and Scheduler. It contains both
the data models and the implemented scheduling logic, including recurring
task creation, owner-availability checks (preferred care hours plus
unavailable-time blocks, both of which may cross midnight), task conflict
detection, and daily schedule generation.

Design assumptions (shared across all classes):

* Times are datetime.time objects and dates are datetime.date objects
  (not strings). For display, format a time with
  time_value.strftime("%H:%M") and a date with date_value.isoformat().
* Priority values must be one of: "low", "medium", or "high".
* Pet names are treated as unique within a single Owner.
* A task is treated as a duplicate within a single Pet only when the pet,
  the title (ignoring capitalization), and the due date all match. Recurring
  tasks may therefore share a title as long as their due dates differ.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, timedelta


@dataclass
class Task:
    """Represents a single pet-care activity such as feeding, walking,
    medication, grooming, or an appointment."""

    title: str
    description: str
    # pet_name identifies the owning Pet. It is kept on the Task itself
    # (even though Tasks live inside a Pet) because the Scheduler works
    # with flat lists of tasks and must still know which pet each belongs to.
    pet_name: str
    duration_minutes: int
    priority: str  # one of: "low", "medium", "high"
    preferred_time: time
    due_date: date
    frequency: str
    completed: bool = False
    scheduled_time: time | None = None  # set once the task is scheduled
    skipped_reason: str | None = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False

    def reschedule(self, new_time: time) -> None:
        """Change the scheduled time of this task."""
        self.scheduled_time = new_time

    def is_recurring(self) -> bool:
        """Return True if this task repeats daily or weekly."""
        return self.frequency.lower() in ("daily", "weekly")

    def create_next_occurrence(self) -> Task | None:
        """Create the next occurrence of a recurring task.

        Returns a brand-new Task due one day later (daily) or seven days
        later (weekly). Returns None for a "once" task. The completed task
        is never modified or reused.
        """
        frequency = self.frequency.lower()
        if frequency == "daily":
            next_due_date = self.due_date + timedelta(days=1)
        elif frequency == "weekly":
            next_due_date = self.due_date + timedelta(days=7)
        else:
            return None

        return Task(
            title=self.title,
            description=self.description,
            pet_name=self.pet_name,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
            due_date=next_due_date,
            frequency=self.frequency,
            completed=False,
            scheduled_time=None,
            skipped_reason=None,
        )


@dataclass
class Pet:
    """Stores information about one pet and manages the care tasks
    assigned to that pet.

    A task is treated as a duplicate only when the title (ignoring
    capitalization) and the due date both match, so a recurring task can
    reuse its title on a different date. Pass a due date to find_task to
    locate one specific occurrence.
    """

    name: str
    species: str
    breed: str
    age: int
    sex: str
    activity_level: str
    medical_conditions: list[str] = field(default_factory=list)
    dietary_restrictions: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet, ensuring its pet_name matches."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> bool:
        """Remove a task by title; return True if removed, else False."""
        for task in self.tasks:
            if task.title.lower() == task_title.lower():
                self.tasks.remove(task)
                return True
        return False

    def get_tasks(self) -> list[Task]:
        """Return a copy of all tasks assigned to this pet."""
        return list(self.tasks)

    def get_incomplete_tasks(self) -> list[Task]:
        """Return only the tasks that are not yet completed."""
        return [task for task in self.tasks if not task.completed]

    def find_task(
        self, task_title: str, due_date: date | None = None
    ) -> Task | None:
        """Find a task by title (ignoring capitalization), or None if not found.

        When due_date is given, both the title and the due date must match.
        When due_date is None, return the first task with the matching title.
        """
        for task in self.tasks:
            if task.title.lower() == task_title.lower():
                if due_date is None or task.due_date == due_date:
                    return task
        return None


class Owner:
    """Stores the owner's information, pets, care preferences,
    preferred care hours, and unavailable time blocks.

    Pet names are treated as unique within a single Owner, so names can
    be used to find or remove a pet. Preferred care hours use
    datetime.time objects.
    """

    def __init__(
        self,
        name: str,
        preferred_start_time: time,
        preferred_end_time: time,
        pets: list[Pet] | None = None,
        unavailable_time_blocks: list[tuple[time, time]] | None = None,
        care_preferences: dict[str, str] | None = None,
    ) -> None:
        """Create an owner with care preferences and an optional list of pets."""
        self.name: str = name
        self.preferred_start_time: time = preferred_start_time
        self.preferred_end_time: time = preferred_end_time
        self.pets: list[Pet] = pets if pets is not None else []
        self.unavailable_time_blocks: list[tuple[time, time]] = (
            unavailable_time_blocks if unavailable_time_blocks is not None else []
        )
        self.care_preferences: dict[str, str] = (
            care_preferences if care_preferences is not None else {}
        )

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name; return True if removed, else False."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                self.pets.remove(pet)
                return True
        return False

    def get_pet(self, pet_name: str) -> Pet | None:
        """Find and return a pet by its name, or None if not found."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet
        return None

    def add_unavailable_time(self, start_time: time, end_time: time) -> None:
        """Add a time block during which the owner is unavailable."""
        self.unavailable_time_blocks.append((start_time, end_time))

    def remove_unavailable_time(self, start_time: time, end_time: time) -> None:
        """Remove a previously added unavailable time block."""
        block = (start_time, end_time)
        if block in self.unavailable_time_blocks:
            self.unavailable_time_blocks.remove(block)

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks combined across all of this owner's pets."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


# ---------------------------------------------------------------------------
# Small time helpers used by the Scheduler. A full day has 1440 minutes, so
# working in "minutes after midnight" keeps the math simple and readable.
# ---------------------------------------------------------------------------
MINUTES_PER_DAY = 1440


def _time_to_minutes(value: time) -> int:
    """Convert a datetime.time into minutes after midnight (0-1439)."""
    return value.hour * 60 + value.minute


def _add_minutes(value: time, minutes: int) -> time:
    """Return the time that is a number of minutes after the given time.

    Wraps around midnight, so adding 60 minutes to 11:30 PM gives 12:30 AM.
    """
    total = (_time_to_minutes(value) + minutes) % MINUTES_PER_DAY
    return time(total // 60, total % 60)


def _intervals_overlap(
    a_start: int, a_end: int, b_start: int, b_end: int
) -> bool:
    """Return True if two minute-based intervals overlap.

    Intervals are half-open, so two intervals that only touch at a boundary
    (one ends exactly where the other begins) do not count as overlapping.
    """
    return a_start < b_end and b_start < a_end


class Scheduler:
    """Collects and organizes tasks, checks the owner's availability,
    detects conflicts, and creates a daily pet-care plan."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that plans care for a single owner."""
        self.owner: Owner = owner
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.conflict_warnings: list[str] = []

    def get_all_tasks(self) -> list[Task]:
        """Gather all tasks by delegating to Owner.get_all_tasks()."""
        return self.owner.get_all_tasks()

    def filter_tasks(
        self,
        date: date | None = None,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Return tasks matching the given filters (only non-None ones apply)."""
        tasks = self.get_all_tasks()
        if date is not None:
            tasks = [task for task in tasks if task.due_date == date]
        if pet_name is not None:
            tasks = [task for task in tasks if task.pet_name.lower() == pet_name.lower()]
        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]
        return tasks

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by scheduled_time, falling back to preferred_time."""
        return sorted(tasks, key=lambda task: task.scheduled_time or task.preferred_time)

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by priority: high, then medium, then low."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda task: priority_order.get(task.priority.lower(), 3))

    def is_owner_available(self, start_time: time, end_time: time) -> bool:
        """Return True only when the owner is free for the whole task interval.

        Two conditions must both hold:

        1. The entire task fits inside the owner's preferred care window.
        2. The task does not overlap any unavailable-time block.

        The task interval, the preferred window, and any unavailable block may
        each cross midnight. We never store a "crosses_midnight" flag; a range
        is overnight when its end time is earlier than its start time, and we
        then extend its end by a full day (1440 minutes) so the math stays
        simple.

        If the preferred start and end times are equal, the preferred window is
        treated as the whole day (no preferred-hours restriction); the
        unavailable-time blocks are still checked.
        """
        # Turn the proposed interval into minutes. If it ends at or before it
        # starts, it wraps past midnight, so extend the end by a full day.
        task_start = _time_to_minutes(start_time)
        task_end = _time_to_minutes(end_time)
        if task_end <= task_start:
            task_end += MINUTES_PER_DAY

        # Check 1: the whole task must fit inside the preferred care window.
        window_start = _time_to_minutes(self.owner.preferred_start_time)
        window_end = _time_to_minutes(self.owner.preferred_end_time)
        if window_start != window_end:  # equal times mean "all day": no limit
            # Normalize an overnight window into one straight interval that
            # runs past midnight (e.g. 1320..1800 for 10:00 PM to 6:00 AM).
            if window_end <= window_start:
                window_end += MINUTES_PER_DAY
            # The task fits when a shifted copy of the window fully contains it.
            fits_in_window = False
            for shift in (-MINUTES_PER_DAY, 0, MINUTES_PER_DAY):
                if window_start + shift <= task_start and task_end <= window_end + shift:
                    fits_in_window = True
                    break
            if not fits_in_window:
                return False

        # Check 2: the task must not overlap any unavailable-time block.
        for block_start_time, block_end_time in self.owner.unavailable_time_blocks:
            block_start = _time_to_minutes(block_start_time)
            block_end = _time_to_minutes(block_end_time)
            # Normalize an overnight block into one straight interval that
            # runs past midnight (e.g. 1320..1860 for 10:00 PM to 7:00 AM).
            if block_end <= block_start:
                block_end += MINUTES_PER_DAY

            # Compare against yesterday's, today's, and tomorrow's copies of
            # the block so an early-morning task still matches an overnight
            # block that began the previous day.
            for shift in (-MINUTES_PER_DAY, 0, MINUTES_PER_DAY):
                if _intervals_overlap(
                    task_start, task_end, block_start + shift, block_end + shift
                ):
                    return False
        return True

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warning messages for task pairs whose times overlap.

        Only tasks on the same due date are compared, and each pair is checked
        once. Tasks that merely touch at a boundary do not conflict. This
        method compares task against task only; owner availability is handled
        separately. Never raises; returns an empty list when there are none.

        A task's end is its start plus its duration in minutes, without any
        modulo, so a task that crosses midnight (for example 11:30 PM for 60
        minutes) keeps a straight interval like 1410..1470. To catch overlaps
        that span midnight, one task's interval is compared against shifted
        copies of the other (minus a day, no shift, plus a day); a single
        overlap in any copy counts as one conflict for that pair.
        """
        warnings: list[str] = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                task_a = tasks[i]
                task_b = tasks[j]
                if task_a.due_date != task_b.due_date:
                    continue

                a_start = _time_to_minutes(task_a.scheduled_time or task_a.preferred_time)
                a_end = a_start + task_a.duration_minutes
                b_start = _time_to_minutes(task_b.scheduled_time or task_b.preferred_time)
                b_end = b_start + task_b.duration_minutes

                # Compare against yesterday's, today's, and tomorrow's copies of
                # task B so a midnight-crossing overlap is still recognized.
                # Report each pair at most once.
                for shift in (-MINUTES_PER_DAY, 0, MINUTES_PER_DAY):
                    if _intervals_overlap(a_start, a_end, b_start + shift, b_end + shift):
                        warnings.append(
                            f"Conflict: '{task_a.title}' for {task_a.pet_name} "
                            f"overlaps with '{task_b.title}' for {task_b.pet_name}."
                        )
                        break
        return warnings

    def generate_daily_schedule(self, date: date) -> list[Task]:
        """Build the daily care plan for the given date.

        Tasks during unavailable periods are skipped with a reason. Conflicting
        tasks stay in the schedule and produce warning messages instead.
        """
        # Start fresh every call so re-running never accumulates stale data.
        self.scheduled_tasks = []
        self.skipped_tasks = []
        self.conflict_warnings = []

        todays_tasks = self.filter_tasks(date=date, completed=False)
        todays_tasks = self.sort_by_time(todays_tasks)

        for task in todays_tasks:
            start_time = task.scheduled_time or task.preferred_time
            end_time = _add_minutes(start_time, task.duration_minutes)

            if self.is_owner_available(start_time, end_time):
                task.scheduled_time = start_time
                task.skipped_reason = None
                self.scheduled_tasks.append(task)
            else:
                task.skipped_reason = (
                    "Owner is unavailable during this task's time."
                )
                self.skipped_tasks.append(task)

        self.conflict_warnings = self.detect_conflicts(self.scheduled_tasks)
        return list(self.scheduled_tasks)

    def create_recurring_task(self, task: Task) -> Task | None:
        """Create and store the next occurrence of a recurring task."""
        next_task = task.create_next_occurrence()
        if next_task is None:
            return None
        pet = self.owner.get_pet(task.pet_name)
        if pet is None:
            return None
        pet.add_task(next_task)
        return next_task

    def mark_task_complete(self, task: Task) -> Task | None:
        """Mark a task complete and, if recurring, create its next occurrence."""
        task.mark_complete()
        if task.is_recurring():
            return self.create_recurring_task(task)
        return None

    def explain_task_placement(self, task: Task) -> str:
        """Return a short explanation of why a task was scheduled or skipped."""
        if task.skipped_reason is not None:
            return f"Skipped: {task.skipped_reason}"
        if task.scheduled_time is not None:
            time_text = task.scheduled_time.strftime("%I:%M %p")
            return f"Scheduled at {time_text} because the owner was available."
        return "Not scheduled yet."

    def get_skipped_tasks(self) -> list[Task]:
        """Return a copy of the tasks that could not be scheduled."""
        return list(self.skipped_tasks)
