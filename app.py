from datetime import date, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** is a pet-care planning assistant. Add your pets and their care
tasks below, then generate an organized daily schedule.
"""
)

with st.expander("About PawPal+"):
    st.markdown(
        """
PawPal+ helps a pet owner plan care tasks for their pet(s) based on constraints
like time, priority, and preferences. This interface is connected to the backend
classes (`Owner`, `Pet`, `Task`, `Scheduler`). Your data stays for the duration
of this browser session.
"""
    )

# ---------------------------------------------------------------------------
# Session state: store the actual backend objects so they survive reruns.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        preferred_start_time=time(7, 0),
        preferred_end_time=time(21, 0),
        unavailable_time_blocks=[(time(22, 0), time(7, 0))],
    )

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner = st.session_state.owner
scheduler = st.session_state.scheduler

# An owner must always keep at least one unavailable block. If an older
# session created the owner without one, add the default sleeping hours once.
if not owner.unavailable_time_blocks:
    owner.add_unavailable_time(time(22, 0), time(7, 0))


def text_to_list(text: str) -> list[str]:
    """Turn comma-separated text into a clean list of non-empty strings."""
    return [item.strip() for item in text.split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Owner section
# ---------------------------------------------------------------------------
st.divider()
st.subheader("👤 Owner")

owner.name = st.text_input("Owner name", value=owner.name)
col_start, col_end = st.columns(2)
with col_start:
    owner.preferred_start_time = st.time_input(
        "Preferred care start time", value=owner.preferred_start_time
    )
with col_end:
    owner.preferred_end_time = st.time_input(
        "Preferred care end time", value=owner.preferred_end_time
    )
st.caption(
    "Tasks must fit completely inside your preferred care hours. Tasks that "
    "overlap your unavailable hours will also be skipped."
)

# ---------------------------------------------------------------------------
# Owner Availability section
# ---------------------------------------------------------------------------
st.divider()
st.subheader("🌙 Owner Availability")
st.markdown(
    "Set the main block of time you are unavailable (for example, sleeping "
    "hours). A block whose end time is earlier than its start time crosses "
    "midnight."
)

old_start, old_end = owner.unavailable_time_blocks[0]
with st.form("availability_form"):
    col_sleep_start, col_sleep_end = st.columns(2)
    with col_sleep_start:
        new_sleep_start = st.time_input(
            "Sleeping/unavailable start time", value=old_start
        )
    with col_sleep_end:
        new_sleep_end = st.time_input(
            "Sleeping/unavailable end time", value=old_end
        )
    availability_submitted = st.form_submit_button("Update availability")

if availability_submitted:
    if new_sleep_start == new_sleep_end:
        st.warning(
            "Start and end times cannot be equal. Please choose a real "
            "time range."
        )
    else:
        owner.remove_unavailable_time(old_start, old_end)
        owner.add_unavailable_time(new_sleep_start, new_sleep_end)
        st.success("Updated your unavailable time block.")
        if new_sleep_end < new_sleep_start:
            st.info(
                f"This block crosses midnight: you are unavailable from "
                f"{new_sleep_start.strftime('%I:%M %p')} until "
                f"{new_sleep_end.strftime('%I:%M %p')} the next day."
            )

# ---------------------------------------------------------------------------
# Add Pet section
# ---------------------------------------------------------------------------
st.divider()
st.subheader("🐕 Add a Pet")

with st.form("add_pet_form"):
    new_pet_name = st.text_input("Name")
    new_pet_species = st.text_input("Species", value="Dog")
    new_pet_breed = st.text_input("Breed")
    new_pet_age = st.number_input("Age", min_value=0, max_value=50, value=1)
    new_pet_sex = st.selectbox("Sex", ["Female", "Male", "Unknown"])
    new_pet_activity = st.selectbox("Activity level", ["low", "medium", "high"])
    new_pet_medical = st.text_input("Medical conditions (comma-separated, optional)")
    new_pet_dietary = st.text_input("Dietary restrictions (comma-separated, optional)")
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    if not new_pet_name.strip():
        st.warning("Please enter a pet name.")
    elif owner.get_pet(new_pet_name) is not None:
        st.warning(f"A pet named '{new_pet_name}' already exists.")
    else:
        pet = Pet(
            name=new_pet_name.strip(),
            species=new_pet_species.strip(),
            breed=new_pet_breed.strip(),
            age=int(new_pet_age),
            sex=new_pet_sex,
            activity_level=new_pet_activity,
            medical_conditions=text_to_list(new_pet_medical),
            dietary_restrictions=text_to_list(new_pet_dietary),
        )
        owner.add_pet(pet)
        st.success(f"Added {pet.name} the {pet.species}.")

# ---------------------------------------------------------------------------
# Display Pets section
# ---------------------------------------------------------------------------
st.divider()
st.subheader("🐾 Your Pets")

if owner.pets:
    pet_rows = [
        {
            "Name": pet.name,
            "Species": pet.species,
            "Breed": pet.breed,
            "Age": pet.age,
            "Activity level": pet.activity_level,
            "Tasks": len(pet.get_tasks()),
        }
        for pet in owner.pets
    ]
    st.table(pet_rows)
else:
    st.info("No pets yet. Add one above to get started.")

# ---------------------------------------------------------------------------
# Add Task section
# ---------------------------------------------------------------------------
st.divider()
st.subheader("📝 Add a Task")

if not owner.pets:
    st.info("Add at least one pet before creating tasks.")
else:
    with st.form("add_task_form"):
        assigned_pet_name = st.selectbox(
            "Assign to pet", [pet.name for pet in owner.pets]
        )
        new_task_title = st.text_input("Task title")
        new_task_description = st.text_area("Description")
        new_task_duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=15
        )
        new_task_priority = st.selectbox("Priority", ["low", "medium", "high"])
        new_task_time = st.time_input("Preferred time", value=time(8, 0))
        new_task_due_date = st.date_input("Due date", value=date.today())
        new_task_frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        selected_pet = owner.get_pet(assigned_pet_name)
        if not new_task_title.strip():
            st.warning("Please enter a task title.")
        elif selected_pet is None:
            st.warning("Selected pet could not be found.")
        elif selected_pet.find_task(new_task_title, new_task_due_date) is not None:
            st.warning(
                f"{selected_pet.name} already has a task titled "
                f"'{new_task_title}' on {new_task_due_date.isoformat()}."
            )
        else:
            task = Task(
                title=new_task_title.strip(),
                description=new_task_description.strip(),
                pet_name=selected_pet.name,
                duration_minutes=int(new_task_duration),
                priority=new_task_priority,
                preferred_time=new_task_time,
                due_date=new_task_due_date,
                frequency=new_task_frequency,
            )
            selected_pet.add_task(task)
            st.success(f"Added '{task.title}' for {selected_pet.name}.")

# ---------------------------------------------------------------------------
# Current Tasks section
# ---------------------------------------------------------------------------
st.divider()
st.subheader("📋 Current Tasks")

all_tasks = scheduler.get_all_tasks()
if all_tasks:
    task_rows = [
        {
            "Title": task.title,
            "Pet": task.pet_name,
            "Due date": task.due_date.isoformat(),
            "Preferred time": task.preferred_time.strftime("%I:%M %p"),
            "Duration": f"{task.duration_minutes} min",
            "Priority": task.priority,
            "Frequency": task.frequency,
            "Completed": "Yes" if task.completed else "No",
        }
        for task in all_tasks
    ]
    st.table(task_rows)
else:
    st.info("No tasks yet. Add a task above.")

# ---------------------------------------------------------------------------
# Generate Schedule section
# ---------------------------------------------------------------------------
st.divider()
st.subheader("📅 Daily Schedule")

schedule_date = st.date_input("Schedule date", value=date.today(), key="schedule_date")

if st.button("Generate schedule"):
    scheduled_tasks = scheduler.generate_daily_schedule(schedule_date)

    if scheduled_tasks:
        st.markdown(f"**Schedule for {schedule_date.isoformat()}**")
        schedule_rows = [
            {
                "Time": (task.scheduled_time or task.preferred_time).strftime(
                    "%I:%M %p"
                ),
                "Title": task.title,
                "Pet": task.pet_name,
                "Duration": f"{task.duration_minutes} min",
                "Priority": task.priority,
                "Frequency": task.frequency,
                "Why": scheduler.explain_task_placement(task),
            }
            for task in scheduled_tasks
        ]
        st.table(schedule_rows)
    else:
        st.info("No tasks were scheduled for the selected date.")

    # Conflict warnings: conflicting tasks stay scheduled but are flagged.
    for warning in scheduler.conflict_warnings:
        st.warning(warning)

    # Skipped tasks: shown separately with the reason each was skipped.
    skipped_tasks = scheduler.get_skipped_tasks()
    if skipped_tasks:
        st.markdown("**Skipped tasks**")
        skipped_rows = [
            {
                "Preferred time": task.preferred_time.strftime("%I:%M %p"),
                "Title": task.title,
                "Pet": task.pet_name,
                "Skipped reason": task.skipped_reason,
            }
            for task in skipped_tasks
        ]
        st.table(skipped_rows)
