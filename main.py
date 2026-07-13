"""CLI verification demo for the implemented PawPal+ backend.

This script builds a sample Owner with pets and tasks, then exercises the
Scheduler end to end: filtering and sorting, recurring-task creation,
owner-availability checks (preferred care hours and unavailable-time
blocks), conflict detection, and daily schedule generation. It prints the
results so the backend in pawpal_system.py can be verified from the
terminal.
"""

from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    """Build a sample owner, pets, and tasks, then print two schedules."""
    # 1. Create the owner with preferred care hours.
    owner = Owner(
        name="Mayra",
        preferred_start_time=time(7, 0),
        preferred_end_time=time(21, 0),
        unavailable_time_blocks=[(time(22, 0), time(7, 0))],
    )

    # 2. Create the pets and add them through the owner's method.
    mochi = Pet(
        name="Mochi",
        species="Dog",
        breed="Shiba Inu",
        age=3,
        sex="Female",
        activity_level="high",
    )
    luna = Pet(
        name="Luna",
        species="Cat",
        breed="Siamese",
        age=5,
        sex="Female",
        activity_level="low",
    )
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # 3. Create tasks divided between the two pets and add them through
    #    each pet's method (never by appending to pet.tasks directly).
    today = date.today()

    morning_feeding = Task(
        title="Morning feeding",
        description="Fill the bowl with breakfast kibble.",
        pet_name="Mochi",
        duration_minutes=10,
        priority="high",
        preferred_time=time(8, 0),
        due_date=today,
        frequency="daily",
    )
    evening_walk = Task(
        title="Evening walk",
        description="Take a walk around the neighborhood.",
        pet_name="Mochi",
        duration_minutes=30,
        priority="medium",
        preferred_time=time(18, 30),
        due_date=today,
        frequency="daily",
    )
    litter_cleaning = Task(
        title="Litter box cleaning",
        description="Scoop and refresh the litter box.",
        pet_name="Luna",
        duration_minutes=15,
        priority="low",
        preferred_time=time(12, 0),
        due_date=today,
        frequency="weekly",
    )
    vet_visit = Task(
        title="Vet checkup",
        description="Annual wellness appointment.",
        pet_name="Luna",
        duration_minutes=45,
        priority="high",
        preferred_time=time(10, 15),
        due_date=today,
        frequency="once",
    )

    mochi.add_task(morning_feeding)
    mochi.add_task(evening_walk)
    luna.add_task(litter_cleaning)
    luna.add_task(vet_visit)

    # 4. Create the scheduler for this owner.
    scheduler = Scheduler(owner)

    # 5. Retrieve today's incomplete tasks.
    todays_tasks = scheduler.filter_tasks(date=date.today(), completed=False)

    # 6. Print the tasks sorted chronologically.
    tasks_by_time = scheduler.sort_by_time(todays_tasks)
    print("Today's Schedule")
    print("----------------")
    print()
    for task in tasks_by_time:
        task_time = task.scheduled_time or task.preferred_time
        print(f"{task_time.strftime('%I:%M %p')} - {task.title}")
        print(f"Pet: {task.pet_name}")
        print(f"Duration: {task.duration_minutes} minutes")
        print(f"Priority: {task.priority}")
        print(f"Frequency: {task.frequency}")
        print()

    # 7. Print the same tasks sorted by priority.
    tasks_by_priority = scheduler.sort_by_priority(todays_tasks)
    print("Tasks by Priority")
    print("-----------------")
    print()
    for task in tasks_by_priority:
        task_time = task.scheduled_time or task.preferred_time
        print(f"{task.priority.upper()} - {task.title} ({task.pet_name})")
        print(f"Time: {task_time.strftime('%I:%M %p')}")
        print(f"Duration: {task.duration_minutes} minutes")
        print(f"Frequency: {task.frequency}")
        print()

    # 8. Demonstrate recurring-task behavior. Completing a daily task should
    #    automatically create its next occurrence through the scheduler.
    daily_task = morning_feeding
    original_due_date = daily_task.due_date
    next_task = scheduler.mark_task_complete(daily_task)

    print("Recurring Task Demo")
    print("-------------------")
    print()
    print(f"Original task: {daily_task.title}")
    print(f"Original completed: {daily_task.completed}")
    print(f"Original due date: {original_due_date.isoformat()}")

    if next_task is not None:
        print(f"New occurrence due date: {next_task.due_date.isoformat()}")
        print(f"New occurrence completed: {next_task.completed}")
        is_one_day_later = next_task.due_date == original_due_date + timedelta(days=1)
        print(f"New occurrence is one day later: {is_one_day_later}")
    print()

    # 9. Add tasks that exercise the scheduling algorithms. Two of them overlap
    #    in time (a conflict) and one falls inside the sleeping block (skipped).
    #    We only add the tasks; the Scheduler decides what happens to them.
    play_session = Task(
        title="Play session",
        description="Fetch and tug in the backyard.",
        pet_name="Mochi",
        duration_minutes=30,
        priority="medium",
        preferred_time=time(8, 0),
        due_date=today,
        frequency="once",
    )
    morning_medication = Task(
        title="Morning medication",
        description="Give Luna her ear-drop medication.",
        pet_name="Luna",
        duration_minutes=20,
        priority="high",
        preferred_time=time(8, 15),
        due_date=today,
        frequency="once",
    )
    midnight_snack = Task(
        title="Midnight snack",
        description="Late-night treat during sleeping hours.",
        pet_name="Mochi",
        duration_minutes=15,
        priority="low",
        preferred_time=time(2, 0),
        due_date=today,
        frequency="once",
    )
    mochi.add_task(play_session)
    luna.add_task(morning_medication)
    mochi.add_task(midnight_snack)

    # 10. Let the Scheduler build the plan. It decides scheduling, conflicts,
    #     and skips; main.py only prints what the Scheduler reports.
    generated = scheduler.generate_daily_schedule(today)

    print("Generated Daily Schedule")
    print("------------------------")
    print()
    for task in generated:
        task_time = task.scheduled_time or task.preferred_time
        print(f"{task_time.strftime('%I:%M %p')} - {task.title}")
        print(f"Pet: {task.pet_name}")
        print(f"Duration: {task.duration_minutes} minutes")
        print(f"Priority: {task.priority}")
        print()

    print("Conflict Warnings")
    print("-----------------")
    print()
    if scheduler.conflict_warnings:
        for warning in scheduler.conflict_warnings:
            print(warning)
    else:
        print("No conflicts detected.")
    print()

    print("Skipped Tasks")
    print("-------------")
    print()
    skipped = scheduler.get_skipped_tasks()
    if skipped:
        for task in skipped:
            print(f"Title: {task.title}")
            print(f"Pet: {task.pet_name}")
            print(f"Preferred time: {task.preferred_time.strftime('%I:%M %p')}")
            print(f"Skipped reason: {task.skipped_reason}")
            print()
    else:
        print("No tasks were skipped.")
        print()


if __name__ == "__main__":
    main()
