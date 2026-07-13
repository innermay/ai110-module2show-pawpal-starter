# PawPal+ Project Reflection

## 1. System Design

### Three Core Actions
**1. Add pets and owner information:**
Users need to create pet profiles and add owner information first. The user should be able to add a pet: this includes information such as name, breed, age, conditions, dietary restrictions, sex, activity level so that the owner can keep important pet information in one place and use it when creating appropriate care tasks. The user should be able to enter their basic information and add constraints such as preferred task times, unavailable time blocks, and care preferences so the system can schedule tasks accordingly.

**2. Add and schedule care tasks:**
This is the main purpose of the app. The user should be able to create a pet-care task for activities such as walking, feeding, bathing, hygiene, appointments and other care activities. Each task should include the assigned pet, duration, priority, frequency, and preferred time so that the scheduler can organize it appropriately. After a task is created, the user can also update an incomplete task's duration and priority.

**3. View and organize today’s tasks:**
The app should show today’s unfinished tasks in chronological order, taking the owner’s available time into account. The user should be able to view the ordered plan, see which tasks were skipped because they fall outside the preferred hours or overlap the owner’s unavailable hours, mark tasks as complete, and read a short explanation of why each task was scheduled or skipped. The user can also separately view the current tasks by priority, but the generated daily schedule itself always stays chronological rather than being reordered by priority.

**a. Initial design**

- Briefly describe your initial UML design.

My initial UML design organizes PawPal+ into four connected classes: Owner, Pet, Task, and Scheduler. The design shows that one Owner can manage multiple Pets, each Pet can have multiple Tasks, and the Scheduler uses the owner’s preferences, availability, pets, and tasks to create an organized daily care plan.

- What classes did you include, and what responsibilities did you assign to each?

I included the following four classes:

- Owner: Stores the owner’s basic information, pets, care preferences, preferred task times, and unavailable time blocks. It also provides access to the tasks assigned to all of the owner’s pets.

- Pet: Stores information about one pet, including its name, species, breed, age, medical conditions, dietary restrictions, and activity level. It also manages the care tasks assigned to that pet.

- Task: Represents one pet-care activity, such as feeding, walking, medication, grooming, or an appointment. It stores details such as the task title, duration, priority, preferred time, frequency, assigned pet, and completion status.

- Scheduler: Acts as the main decision-making class. It collects tasks from the owner’s pets, sorts and filters them, considers the owner’s availability, detects scheduling conflicts, and generates the daily care plan.

**b. Design changes**

- Did your design change during implementation?

Yes. The main four-class structure (Owner, Pet, Task, and Scheduler) stayed the same the whole way through, but I changed and clarified several design assumptions once I started actually implementing and testing the code. I also updated the final UML in `diagrams/uml_final.mmd` so it matches the completed code, including the real return types like `Task | None` and the extra `mark_task_complete()` method that I added later.

- If yes, describe at least one change and why you made it.

The biggest change was how I store times and dates. In my early notes I planned to store times as `HH:MM` strings and dates as `YYYY-MM-DD` strings. When I implemented the Scheduler I switched to real Python `datetime.time` and `datetime.date` objects instead. This made sorting, comparison, recurrence, and overnight scheduling much safer and clearer: I can compare and sort times directly, add a `timedelta` of one day or seven days to a date for recurring tasks, and do the overnight math in minutes without parsing strings by hand. Storing them as strings would have meant re-parsing everywhere and would have made the overnight logic easy to get wrong.

A second change was how I prevent duplicate tasks. At first I assumed a task title alone had to be unique inside a Pet. That turned out to be too strict, because a recurring task like "Morning feeding" needs to exist on many different dates. So the final rule prevents duplicates using the combination of the task title **and** the due date for the same Pet. This lets a recurring task reuse the same title on different dates, while still blocking an accidental exact duplicate on the same day. You can see this in `Pet.find_task()`, which accepts an optional due date, and in the Streamlit "Add a Task" check in `app.py`.

I kept several other design decisions that turned out to be accurate:

- Pet names are treated as unique within one Owner, which makes it easy to find and remove a pet by name.
- Priority values are restricted to `low`, `medium`, or `high`.
- The Task class keeps a `pet_name` field, because the Scheduler combines tasks from different pets into one flat list and each task still needs to say which pet it belongs to.
- `Scheduler.get_all_tasks()` simply delegates to `Owner.get_all_tasks()` instead of repeating the task-collection logic, which keeps each class responsible for its own data.
- The original four-class structure (Owner, Pet, Task, Scheduler) stayed the same, and I updated the final UML so it reflects the completed code.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

When it builds a plan, the Scheduler considers:

- The selected due date (only that day's tasks are planned)
- Completion status (only incomplete tasks are scheduled)
- The preferred time of each task
- The duration of each task
- The owner's preferred care window (preferred start and end times)
- The owner's unavailable-time blocks (like sleeping hours)
- Both normal and overnight time ranges (a range that crosses midnight)
- Recurrence frequency (once, daily, or weekly) when a task is completed
- Conflicts between task time intervals
- The pet name, when filtering tasks by pet
- Task priority, when the user chooses the priority-sorting view

A few things about how this actually works in the current code:

- The generated daily schedule is ordered **chronologically** by time, not by priority.
- Priority sorting is available separately through `Scheduler.sort_by_priority()`, which is used for the priority view.
- The daily scheduler does **not** automatically rearrange tasks based on priority, and priority does not change the order of the generated schedule.
- Availability is treated as a **hard constraint**: a task that does not fit the preferred window or that overlaps an unavailable block is skipped, not squeezed in.
- Conflicts create warning messages but do **not** remove any tasks from the schedule.

- How did you decide which constraints mattered most?

I treated the due date, completion status, preferred time, and owner availability as the most important constraints. The reason is that the plan has to be honest: it must show the correct day's unfinished tasks, and it must never pretend the owner is available when they are not. If the schedule showed already-completed tasks, or the wrong day's tasks, or asked the owner to walk the dog at 2:00 AM while they are asleep, the plan would not be trustworthy. Priority still matters, but I decided it should help the owner *look* at their tasks a certain way (the priority view) rather than silently override when things are scheduled.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

My scheduler makes several deliberate tradeoffs, all in the direction of being transparent instead of "clever":

- **Conflicting tasks stay in the schedule and generate warnings** instead of being deleted or automatically moved. If "Play session" and "Morning medication" overlap, both remain in the plan and the owner sees a warning message. PawPal+ does not decide for them which task wins.
- **Unavailable tasks are skipped with a reason** instead of being moved to another time. A task at 2:00 AM inside the sleeping block is placed in the skipped list with the reason "Owner is unavailable during this task's time," rather than being relocated to a free slot.
- **It checks exact start times and durations but does not search for the best alternative open time.** The scheduler reasons about the real interval of each task, but it does not try to optimize the day by shifting tasks around to fill gaps.
- **I kept the current tested availability method instead of accepting an AI suggestion to extract a new normalization helper.** AI suggested pulling the repeated overnight time-conversion logic into a shared helper like `_to_minute_interval()`. That would remove a little repetition, but I chose to keep the full availability algorithm visible in one place because it was already readable and had already passed the overnight and boundary tests.

- Why is that tradeoff reasonable for this scenario?

These tradeoffs are reasonable for a small beginner pet-care project because the behavior stays transparent, predictable, and under the owner's control. The owner can always see *why* something happened — a conflict warning or a skip reason — and they get to make the real care decisions themselves, like which of two overlapping tasks to move. Automatically deleting, relocating, or optimizing tasks would be harder to follow and could quietly do the wrong thing. Keeping the tested availability code as-is also avoids the risk of introducing a new boundary or overnight bug in exchange for only a small readability gain.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used AI through almost every phase of PawPal+, but as a helper rather than a replacement for my own decisions. Specifically, I used it for:

- Brainstorming the four classes and what each one should be responsible for
- Generating and reviewing the Mermaid UML diagram
- Translating the UML into Python class skeletons
- Implementing methods in small phases instead of all at once
- Designing the sorting, filtering, recurrence, availability, and conflict logic
- Debugging the overnight time calculations, which were the trickiest part
- Reviewing the code for readability and possible refactoring
- Creating a pytest test plan
- Writing and reviewing the tests
- Reviewing the Streamlit UI for clarity and usability
- Updating the documentation (README and this reflection)

I used two AI tools in different roles. I used **Claude inside the coding environment** to actually read and edit the project files, run commands, and make changes directly in the repo. I used **ChatGPT as a mentor** to help me break the assignment into phases, explain design decisions in plain language, and write focused prompts before I ran them.

- What kinds of prompts or questions were most helpful?

The most helpful prompts were the specific, bounded ones. The ones that worked best:

- Named the exact files to read first
- Limited which files were allowed to be edited (for example, "only edit `app.py`")
- Described the expected behavior and the edge cases up front
- Required verification commands like `python3 -m pytest` or `python3 -m py_compile`
- Asked the AI to explain its reasoning and summarize what it changed

Vague prompts gave vague results, so being precise about files, behavior, and how to verify made a big difference.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

The clearest example was the availability-refactoring review. While reviewing `is_owner_available()`, the AI suggested extracting the repeated overnight-normalization logic into a new helper method called `_to_minute_interval()`. The suggestion was actually valid — it would have slightly reduced the repeated "convert to minutes and extend past midnight" code.

I decided **not** to apply it. The existing code was already readable, beginner-friendly, and, most importantly, already passed my overnight, boundary, and availability tests. Refactoring correct time logic risked introducing a new boundary bug (for example, an off-by-one at exactly midnight) in exchange for only a small readability improvement. That was not a good trade for a small project, so I kept the tested version. I did not accept every AI recommendation.

- How did you evaluate or verify what the AI suggested?

I evaluated that specific suggestion against my existing test cases — the overnight conflict test, the boundary "touching" test, and the outside-hours and overnight-block skip tests — and asked whether the refactor could earn back the risk it introduced. It could not, so I declined it.

More generally, I verified AI-generated code by:

- Reading the changed method myself before trusting it
- Running `python3 -m py_compile` to catch syntax errors
- Running the CLI demo (`python3 main.py`) to see the backend behave end to end
- Manually testing the Streamlit app in the browser
- Running the complete pytest suite

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

The final suite in `tests/test_pawpal.py` contains **15 passing tests**. It started as just two basic Phase 2 tests and grew into 15 focused ones. Together they cover:

- Marking a Task complete
- Adding a Task to a Pet (and the pet_name being set)
- Chronological sorting of out-of-order tasks
- Daily recurrence creating a correct next occurrence
- Weekly recurrence advancing seven days
- One-time tasks creating no next occurrence
- Regular overlapping tasks producing one conflict warning
- Tasks that only touch at a boundary producing no conflict
- Overnight conflicts that cross midnight
- Tasks on different dates not conflicting
- Scheduling a task the owner is available for
- Skipping a task outside the preferred hours
- Skipping a task inside an overnight unavailable block
- Resetting the scheduler's scheduled/skipped/conflict lists between plans
- Returning a safe copy of the skipped-task list

- Why were these tests important?

These tests matter because they verify the main requirements of the assignment and protect the parts that are easy to get wrong. The boundary test protects against false conflicts when one task ends exactly as another begins. The overnight tests protect the most complicated time logic, which is where a bug is most likely to hide. The recurrence tests make sure completing a daily or weekly task does not lose a future care task or accidentally create a duplicate. And the state-reset test makes sure that generating a new plan does not leave stale scheduled, skipped, or conflict results from a previous run.

**b. Confidence**

- How confident are you that your scheduler works correctly?

★★★★★ — 5 out of 5 stars

I am confident because all 15 tests pass, the code compiles cleanly with `python3 -m py_compile`, and I also exercised the whole system through the CLI demo and through the Streamlit UI by hand. That is more than one kind of verification, which is why I rate it 5 out of 5.

At the same time, I want to be honest: passing tests does not prove that every possible case works. My tests cover the important behaviors and the main edge cases, but there are still situations I have not tested yet.

- What edge cases would you test next if you had more time?

If I had more time, I would add tests for:

- Filtering by pet and completion status together in the same call
- A Pet that has no tasks at all
- An owner with multiple unavailable-time blocks
- Invalid priority or frequency values
- Very long tasks that last more than one full day
- More Streamlit interaction testing
- Trying to complete the same task twice
- Longer recurrence chains (completing several occurrences in a row)

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with a few things:

- Keeping the backend logic (`pawpal_system.py`) separate from the Streamlit UI (`app.py`)
- Making the final UI call Scheduler methods like `generate_daily_schedule()` and `mark_task_complete()` instead of re-implementing any algorithms in the UI
- Correctly supporting overnight care windows and overnight conflicts, which were the hardest part
- Handling recurrence by creating brand-new Task objects instead of mutating the old one
- Growing the test suite from two basic tests up to 15 focused tests
- Updating the final UML so it actually matches the code I built

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

In another iteration I would add:

- Permanent data storage so pets and tasks survive after the browser session ends
- Editing additional task fields (the UI currently edits an incomplete task's duration and priority)
- Moving tasks between pets
- Deleting tasks
- Managing multiple unavailable-time blocks in the UI (right now the UI edits one main block)
- Suggesting alternative open times for tasks that get skipped
- Optional automatic conflict resolution
- Stronger validation for priority and frequency values
- Better Streamlit persistence and more interaction tests

To be clear, none of these are implemented right now — the current version keeps conflicting tasks with warnings, skips unavailable tasks with reasons, stores data only for the browser session, and lets the owner make the final decisions.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

My main takeaway is that AI-generated code still needs human design decisions, verification, and testing. AI could suggest code quickly, but I was the one who had to decide whether a suggestion actually fit PawPal+, and I had to verify it with real tests before trusting it.

Breaking the work into phases is what made this possible. Going phase by phase helped me understand:

- What each class was responsible for
- How the Scheduler communicates with the Owner and Pet classes to gather tasks
- Why edge cases (like overnight ranges and boundary times) have to be considered before trusting the code
- How having tests let me change code later with more confidence
- Why a shorter or more "Pythonic" solution is not always the clearest one, especially for a beginner reading the code
