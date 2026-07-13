"""PawPal+ core class skeletons.

This module defines the four core classes for the PawPal+ pet-care
scheduling application: Owner, Pet, Task, and Scheduler. Only the
structure (attributes and method signatures) is defined here. The
actual scheduling logic is not implemented yet.

Design assumptions (shared across all classes):

* Time strings use 24-hour "HH:MM" format, e.g. "08:00" or "14:30".
* Date strings use "YYYY-MM-DD" format, e.g. "2026-07-13".
* Priority values must be one of: "low", "medium", or "high".
* Pet names are treated as unique within a single Owner.
* Task titles are treated as unique within a single Pet.
"""

from __future__ import annotations

from dataclasses import dataclass, field


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
    preferred_time: str  # 24-hour "HH:MM", e.g. "08:00"
    due_date: str  # "YYYY-MM-DD", e.g. "2026-07-13"
    frequency: str
    completed: bool = False
    scheduled_time: str | None = None  # 24-hour "HH:MM" once scheduled
    skipped_reason: str | None = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        raise NotImplementedError

    def reschedule(self, new_time: str) -> None:
        """Change the scheduled time of this task."""
        raise NotImplementedError

    def is_recurring(self) -> bool:
        """Return True if this task repeats on a schedule."""
        raise NotImplementedError

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
        """Add a care task to this pet."""
        raise NotImplementedError

    def remove_task(self, task_title: str) -> None:
        """Remove a task from this pet by its title."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return all tasks assigned to this pet."""
        raise NotImplementedError

    def get_incomplete_tasks(self) -> list[Task]:
        """Return only the tasks that are not yet completed."""
        raise NotImplementedError

    def find_task(self, task_title: str) -> Task | None:
        """Find and return a task by its title, or None if not found."""
        raise NotImplementedError


class Owner:
    """Stores the owner's information, pets, care preferences,
    preferred care hours, and unavailable time blocks.

    Pet names are treated as unique within a single Owner, so names can
    be used to find or remove a pet. Preferred care hours use 24-hour
    "HH:MM" time strings.
    """

    def __init__(
        self,
        name: str,
        preferred_start_time: str,
        preferred_end_time: str,
        pets: list[Pet] | None = None,
        unavailable_time_blocks: list[tuple[str, str]] | None = None,
        care_preferences: dict[str, str] | None = None,
    ) -> None:
        """Create an owner with care preferences and an optional list of pets."""
        self.name: str = name
        self.preferred_start_time: str = preferred_start_time
        self.preferred_end_time: str = preferred_end_time
        self.pets: list[Pet] = pets if pets is not None else []
        self.unavailable_time_blocks: list[tuple[str, str]] = (
            unavailable_time_blocks if unavailable_time_blocks is not None else []
        )
        self.care_preferences: dict[str, str] = (
            care_preferences if care_preferences is not None else {}
        )

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet from this owner by its name."""
        raise NotImplementedError

    def get_pet(self, pet_name: str) -> Pet | None:
        """Find and return a pet by its name, or None if not found."""
        raise NotImplementedError

    def add_unavailable_time(self, start_time: str, end_time: str) -> None:
        """Add a time block during which the owner is unavailable."""
        raise NotImplementedError

    def remove_unavailable_time(self, start_time: str, end_time: str) -> None:
        """Remove a previously added unavailable time block."""
        raise NotImplementedError

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across all of this owner's pets."""
        raise NotImplementedError


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
        """Gather all tasks from the owner's pets.

        During implementation this should delegate to
        ``Owner.get_all_tasks()`` rather than repeating the
        task-collection logic here.
        """
        raise NotImplementedError

    def filter_tasks(
        self,
        date: str | None = None,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Return tasks filtered by date, pet name, and/or completion status."""
        raise NotImplementedError

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return the given tasks sorted by their scheduled/preferred time."""
        raise NotImplementedError

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return the given tasks sorted by priority."""
        raise NotImplementedError

    def is_owner_available(self, start_time: str, end_time: str) -> bool:
        """Return True if the owner is available during the given time range."""
        raise NotImplementedError

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Detect overlapping or conflicting tasks and return warnings."""
        raise NotImplementedError

    def generate_daily_schedule(self, date: str) -> list[Task]:
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
