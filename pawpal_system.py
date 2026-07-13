"""PawPal+ core class skeletons.

This module defines the four core classes for the PawPal+ pet-care
scheduling application: Owner, Pet, Task, and Scheduler. Only the
structure (attributes and method signatures) is defined here. The
actual scheduling logic is not implemented yet.

Design assumptions (shared across all classes):

* Times are datetime.time objects and dates are datetime.date objects
  (not strings). For display, format a time with
  time_value.strftime("%H:%M") and a date with date_value.isoformat().
* Priority values must be one of: "low", "medium", or "high".
* Pet names are treated as unique within a single Owner.
* Task titles are treated as unique within a single Pet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time


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

    def create_next_occurrence(self) -> Task:
        """Create the next occurrence of a recurring task."""
        raise NotImplementedError


@dataclass
class Pet:
    """Stores information about one pet and manages the care tasks
    assigned to that pet.

    Task titles are treated as unique within a single Pet, so titles can
    be used to find or remove a task.
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

    def find_task(self, task_title: str) -> Task | None:
        """Find and return a task by its title, or None if not found."""
        for task in self.tasks:
            if task.title.lower() == task_title.lower():
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
        """Return True if the owner is available during the given time range."""
        # NOTE: An unavailable block whose end_time is earlier than its
        # start_time crosses midnight (an overnight block). That case will
        # be handled during the algorithmic phase (Phase 4).
        raise NotImplementedError

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Detect overlapping or conflicting tasks and return warnings."""
        raise NotImplementedError

    def generate_daily_schedule(self, date: date) -> list[Task]:
        """Build and return an organized daily care plan for the given date."""
        raise NotImplementedError

    def create_recurring_task(self, task: Task) -> Task:
        """Create the next occurrence of a recurring task."""
        raise NotImplementedError

    def explain_task_placement(self, task: Task) -> str:
        """Return a short explanation of why a task was scheduled or skipped."""
        raise NotImplementedError

    def get_skipped_tasks(self) -> list[Task]:
        """Return the tasks that could not be scheduled."""
        raise NotImplementedError
