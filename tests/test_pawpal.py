"""Basic automated tests for PawPal+ (Phase 2, Step 3)."""

from datetime import date, time

from pawpal_system import Pet, Task


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
