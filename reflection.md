# PawPal+ Project Reflection

## 1. System Design

### Three Core Actions
**1. Add and manage pets and owner information:**
Users need to create pet profiles and add owner information first. The user should be able to add or edit a pet: this includes information such as name, breed, age, conditions, dietary restrictions, sex, activity level so that the owner can keep important pet information in one place and use it when creating appropriate care tasks. The user should be able to enter their basic information and add constraints such as preferred task times, unavailable time blocks, and care preferences so the system can schedule tasks accordingly.

**2. Add and schedule care tasks:**
This is the main purpose of the app. The user should be able to create and update a pet-care task for activities such as walking, feeding, bathing, hygiene, appointments and other care activities. Each task should include the assigned pet, duration, priority, frequency, and preferred time so that the scheduler can organize it appropriately.

**3. View and prioritize today’s tasks:**
The app should organize today’s tasks based on priority, duration, preferred time, and the owner’s available time. The user should be able to view the ordered plan, see which tasks were skipped because there was not enough time, mark tasks as complete, and read a short explanation of why the tasks were arranged in that order.

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
Yes. The main four-class structure stayed the same, but I
clarified several design assumptions after asking AI to review
the initial UML and class skeletons.


- If yes, describe at least one change and why you made it.
I documented that all time values must use the 24-hour `HH:MM`
format and all dates must use the `YYYY-MM-DD` format. This is
important because the Scheduler will need to sort and compare
times and dates consistently.

I also clarified that priority values must be `low`, `medium`,
or `high`. Pet names are treated as unique within one Owner,
and task titles are treated as unique within one Pet. These
assumptions make it easier to find and remove pets and tasks.

I kept `pet_name` in the Task class because the Scheduler will
combine tasks from different pets into one list. The pet name
allows each task to identify which pet it belongs to.

I also decided that `Scheduler.get_all_tasks()` should call
`Owner.get_all_tasks()` instead of repeating the same task
collection logic. This avoids duplicated code and keeps the
responsibilities of each class clear.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

One tradeoff I made was keeping the availability-checking
algorithm slightly repetitive instead of replacing parts of it
with another helper function. The current method separately
converts and normalizes the owner's preferred care window and
unavailable time blocks.

AI suggested creating a shared helper method to remove the
repeated time-conversion logic. Although that version would be
slightly shorter and more reusable, it would also require a
beginner reading the code to move between multiple functions
to understand one scheduling decision.

I decided to keep the current version because the full
availability algorithm remains visible in one place. This
makes it easier to follow how normal and overnight time ranges
are handled.

- Why is that tradeoff reasonable for this scenario?

This tradeoff is reasonable because PawPal+ is a small
pet-care application with only a few unavailable time blocks.
The current algorithm is already fast enough, readable, and
has passed the required boundary and overnight tests.

Removing a small amount of duplicated code would not create a
meaningful performance improvement. Keeping the tested version
also reduces the risk of accidentally changing working
behavior while refactoring.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

