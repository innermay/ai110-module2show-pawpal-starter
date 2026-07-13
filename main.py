"""Temporary CLI demo for PawPal+ (Phase 2, Step 2).

This script builds a small example of an Owner with pets and tasks,
then uses the Scheduler to filter and sort those tasks. It is only a
demo of the backend classes in pawpal_system.py. The Streamlit
interface (app.py) will be connected in Phase 3.
"""

from datetime import date, time

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    """Build a sample owner, pets, and tasks, then print two schedules."""
    # 1. Create the owner with preferred care hours.
    owner = Owner(
        name="Mayra",
        preferred_start_time=time(7, 0),
        preferred_end_time=time(21, 0),
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


if __name__ == "__main__":
    main()
