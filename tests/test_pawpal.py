"""Automated tests for PawPal+.

Phase 2 (Step 3) added the first two basic tests. Phase 5 (Step 2) expands
this suite with tests for sorting, recurrence, conflict detection, owner
availability, and scheduler state management.

The tests use plain pytest assertions and create Owner, Pet, Task, and
Scheduler objects directly (no mocks, fixtures, or parameterization).
"""

from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def make_task(
    title: str,
    preferred_time: time,
    due_date: date,
    duration: int = 30,
    priority: str = "medium",
    frequency: str = "once",
    pet_name: str = "Mochi",
) -> Task:
    """Build a Task with sensible defaults to reduce repetition in tests."""
    return Task(
        title=title,
        description="Test task",
        pet_name=pet_name,
        duration_minutes=duration,
        priority=priority,
        preferred_time=preferred_time,
        due_date=due_date,
        frequency=frequency,
    )


def make_pet(name: str = "Mochi") -> Pet:
    """Build a simple Pet for tests that need one."""
    return Pet(
        name=name,
        species="Dog",
        breed="Shiba Inu",
        age=3,
        sex="Female",
        activity_level="high",
    )


# ---------------------------------------------------------------------------
# Phase 2 tests (preserved).
# ---------------------------------------------------------------------------


def test_mark_complete_changes_task_status():
    """Calling mark_complete() should set the task's completed flag to True."""
    # Arrange: create a task that starts out not completed.
    task = Task(
        title="Morning feeding",
        description="Fill the bowl with breakfast kibble.",
        pet_name="Mochi",
        duration_minutes=10,
        priority="high",
        preferred_time=time(8, 0),
        due_date=date.today(),
        frequency="daily",
    )
    assert task.completed is False

    # Act: mark the task as complete.
    task.mark_complete()

    # Assert: the task should now be completed.
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task should grow the pet's task list and set the task's pet_name."""
    # Arrange: create a pet and a task to add to it.
    pet = Pet(
        name="Mochi",
        species="Dog",
        breed="Shiba Inu",
        age=3,
        sex="Female",
        activity_level="high",
    )
    task = Task(
        title="Evening walk",
        description="Take a walk around the neighborhood.",
        pet_name="Mochi",
        duration_minutes=30,
        priority="medium",
        preferred_time=time(18, 30),
        due_date=date.today(),
        frequency="daily",
    )
    task_count_before = len(pet.get_tasks())

    # Act: add the task to the pet.
    pet.add_task(task)

    # Assert: the task count increased by one and the pet_name matches.
    task_count_after = len(pet.get_tasks())
    assert task_count_after == task_count_before + 1
    assert task.pet_name == pet.name


# ---------------------------------------------------------------------------
# Phase 5 required tests.
# ---------------------------------------------------------------------------


def test_sort_by_time_orders_tasks_chronologically():
    """sort_by_time() should return tasks in chronological order."""
    # Arrange: three tasks created out of chronological order.
    due = date(2026, 7, 13)
    owner = Owner("Mayra", time(7, 0), time(21, 0))
    scheduler = Scheduler(owner)
    evening = make_task("Evening walk", time(18, 30), due)
    morning = make_task("Morning feeding", time(8, 0), due)
    noon = make_task("Lunch feeding", time(12, 0), due)
    tasks = [evening, morning, noon]

    # Act: sort the tasks by time.
    result = scheduler.sort_by_time(tasks)

    # Assert: the times come back in ascending order.
    result_times = [task.preferred_time for task in result]
    assert result_times == [time(8, 0), time(12, 0), time(18, 30)]


def test_mark_daily_task_complete_creates_next_occurrence():
    """Completing a daily task should mark it done and create tomorrow's copy."""
    # Arrange: an owner with a pet that has one daily task.
    owner = Owner("Mayra", time(7, 0), time(21, 0))
    pet = make_pet("Mochi")
    owner.add_pet(pet)
    due = date(2026, 7, 13)
    daily_task = make_task(
        "Morning feeding", time(8, 0), due, frequency="daily", pet_name="Mochi"
    )
    pet.add_task(daily_task)
    scheduler = Scheduler(owner)
    task_count_before = len(pet.get_tasks())

    # Act: mark the daily task complete (this should spawn a new occurrence).
    new_task = scheduler.mark_task_complete(daily_task)

    # Assert: original completed, and a fresh incomplete next occurrence exists.
    assert daily_task.completed is True
    assert isinstance(new_task, Task)
    assert new_task is not daily_task
    assert new_task.due_date == date(2026, 7, 14)
    assert new_task.completed is False
    assert new_task.scheduled_time is None
    assert new_task.skipped_reason is None
    assert len(pet.get_tasks()) == task_count_before + 1
    assert new_task in pet.get_tasks()


def test_overlapping_tasks_produce_one_warning():
    """Two overlapping tasks on the same date should yield exactly one warning."""
    # Arrange: task A (8:00-8:30) overlaps task B (8:15-8:35) on the same day.
    due = date(2026, 7, 13)
    owner = Owner("Mayra", time(7, 0), time(21, 0))
    scheduler = Scheduler(owner)
    task_a = make_task("Morning feeding", time(8, 0), due, duration=30)
    task_b = make_task("Morning medication", time(8, 15), due, duration=20)

    # Act: detect conflicts between the two tasks.
    warnings = scheduler.detect_conflicts([task_a, task_b])

    # Assert: exactly one warning that names both tasks.
    assert len(warnings) == 1
    assert "Morning feeding" in warnings[0]
    assert "Morning medication" in warnings[0]


def test_touching_tasks_do_not_conflict():
    """A task ending exactly when another begins should not be a conflict."""
    # Arrange: task A ends at 8:30, task B begins at 8:30 (same day).
    due = date(2026, 7, 13)
    owner = Owner("Mayra", time(7, 0), time(21, 0))
    scheduler = Scheduler(owner)
    task_a = make_task("Morning feeding", time(8, 0), due, duration=30)
    task_b = make_task("Play session", time(8, 30), due, duration=30)

    # Act: detect conflicts between the back-to-back tasks.
    warnings = scheduler.detect_conflicts([task_a, task_b])

    # Assert: touching at a boundary is not an overlap.
    assert warnings == []


# ---------------------------------------------------------------------------
# Phase 5 strongly recommended tests.
# ---------------------------------------------------------------------------


def test_weekly_recurrence_advances_seven_days():
    """A weekly task's next occurrence should be due seven days later."""
    # Arrange: a weekly task due July 13, 2026.
    task = make_task(
        "Litter box cleaning", time(12, 0), date(2026, 7, 13), frequency="weekly"
    )

    # Act: create the next occurrence.
    next_task = task.create_next_occurrence()

    # Assert: it is a new incomplete task due seven days later.
    assert isinstance(next_task, Task)
    assert next_task is not task
    assert next_task.due_date == date(2026, 7, 20)
    assert next_task.completed is False


def test_one_time_task_creates_no_next_occurrence():
    """A one-time task should not create any next occurrence."""
    # Arrange: a task with frequency "once".
    task = make_task("Vet checkup", time(10, 15), date(2026, 7, 13), frequency="once")

    # Act: attempt to create the next occurrence.
    result = task.create_next_occurrence()

    # Assert: no new task is created.
    assert result is None


def test_available_task_is_scheduled():
    """A task inside preferred hours with no blocks should be scheduled."""
    # Arrange: owner free 7 AM-9 PM, one task at 10 AM.
    owner = Owner("Mayra", time(7, 0), time(21, 0))
    pet = make_pet("Mochi")
    owner.add_pet(pet)
    due = date(2026, 7, 13)
    task = make_task("Morning feeding", time(10, 0), due, duration=30)
    pet.add_task(task)
    scheduler = Scheduler(owner)

    # Act: generate the daily schedule.
    scheduled = scheduler.generate_daily_schedule(due)

    # Assert: the task is scheduled at its preferred time with no skip reason.
    assert task in scheduled
    assert task.scheduled_time == time(10, 0)
    assert task.skipped_reason is None


def test_task_outside_preferred_hours_is_skipped():
    """A task outside the owner's preferred hours should be skipped."""
    # Arrange: owner free 7 AM-9 PM, one task at 10 PM.
    owner = Owner("Mayra", time(7, 0), time(21, 0))
    pet = make_pet("Mochi")
    owner.add_pet(pet)
    due = date(2026, 7, 13)
    task = make_task("Late feeding", time(22, 0), due, duration=30)
    pet.add_task(task)
    scheduler = Scheduler(owner)

    # Act: generate the daily schedule.
    scheduled = scheduler.generate_daily_schedule(due)

    # Assert: the task is not scheduled but is skipped with a reason.
    assert task not in scheduled
    assert task in scheduler.get_skipped_tasks()
    assert task.skipped_reason is not None


def test_task_in_overnight_unavailable_block_is_skipped():
    """A task inside an overnight unavailable block should be skipped."""
    # Arrange: unrestricted preferred window, unavailable 10 PM-7 AM, task at 2 AM.
    owner = Owner(
        "Mayra",
        time(0, 0),
        time(0, 0),  # equal start/end means the preferred window is unrestricted
        unavailable_time_blocks=[(time(22, 0), time(7, 0))],
    )
    pet = make_pet("Mochi")
    owner.add_pet(pet)
    due = date(2026, 7, 13)
    task = make_task("Midnight snack", time(2, 0), due, duration=15)
    pet.add_task(task)
    scheduler = Scheduler(owner)

    # Act: generate the daily schedule.
    scheduled = scheduler.generate_daily_schedule(due)

    # Assert: the task falls inside the overnight block and is skipped.
    assert task not in scheduled
    assert task in scheduler.get_skipped_tasks()


def test_overnight_task_conflict_is_detected():
    """Two tasks overlapping across midnight should produce one conflict."""
    # Arrange: task A 11:30 PM-12:30 AM overlaps task B 12:15 AM-12:45 AM.
    due = date(2026, 7, 13)
    owner = Owner("Mayra", time(7, 0), time(21, 0))
    scheduler = Scheduler(owner)
    task_a = make_task("Night walk", time(23, 30), due, duration=60)
    task_b = make_task("Late snack", time(0, 15), due, duration=30)

    # Act: detect conflicts across the midnight boundary.
    warnings = scheduler.detect_conflicts([task_a, task_b])

    # Assert: the overnight overlap is caught as one conflict.
    assert len(warnings) == 1


def test_tasks_on_different_dates_do_not_conflict():
    """Overlapping clock times on different dates should not conflict."""
    # Arrange: same time of day, but two different due dates.
    owner = Owner("Mayra", time(7, 0), time(21, 0))
    scheduler = Scheduler(owner)
    task_a = make_task("Morning feeding", time(8, 0), date(2026, 7, 13), duration=30)
    task_b = make_task("Morning feeding", time(8, 0), date(2026, 7, 14), duration=30)

    # Act: detect conflicts between tasks on different dates.
    warnings = scheduler.detect_conflicts([task_a, task_b])

    # Assert: different dates never conflict.
    assert warnings == []


def test_generate_daily_schedule_resets_previous_state():
    """Re-running the schedule should clear stale scheduled/skipped/conflict data."""
    # Arrange: a busy first day with a scheduled task, a skipped task,
    # and a conflicting pair, plus an empty second day.
    owner = Owner(
        "Mayra",
        time(7, 0),
        time(21, 0),
        unavailable_time_blocks=[(time(22, 0), time(7, 0))],
    )
    pet = make_pet("Mochi")
    owner.add_pet(pet)
    busy_day = date(2026, 7, 13)
    empty_day = date(2026, 7, 20)
    # Two overlapping tasks (conflict) that are both inside preferred hours.
    pet.add_task(make_task("Morning feeding", time(8, 0), busy_day, duration=30))
    pet.add_task(make_task("Morning medication", time(8, 15), busy_day, duration=20))
    # One task during the overnight block (skipped).
    pet.add_task(make_task("Midnight snack", time(2, 0), busy_day, duration=15))
    scheduler = Scheduler(owner)

    # Act (first): build the busy schedule and confirm all three lists have data.
    first = scheduler.generate_daily_schedule(busy_day)
    assert len(first) >= 1
    assert len(scheduler.get_skipped_tasks()) >= 1
    assert len(scheduler.conflict_warnings) >= 1

    # Act (second): build a schedule for a day with no tasks.
    second = scheduler.generate_daily_schedule(empty_day)

    # Assert: every list is reset to empty.
    assert second == []
    assert scheduler.scheduled_tasks == []
    assert scheduler.get_skipped_tasks() == []
    assert scheduler.conflict_warnings == []


def test_get_skipped_tasks_returns_a_copy():
    """get_skipped_tasks() should return a copy, not the internal list."""
    # Arrange: a scheduler (no tasks needed to test the copy behavior).
    owner = Owner("Mayra", time(7, 0), time(21, 0))
    scheduler = Scheduler(owner)

    # Act: retrieve the skipped list and mutate the returned copy.
    returned = scheduler.get_skipped_tasks()
    returned.append("not a real task")

    # Assert: the internal list is untouched and is a different object.
    assert returned is not scheduler.skipped_tasks
    assert scheduler.skipped_tasks == []
