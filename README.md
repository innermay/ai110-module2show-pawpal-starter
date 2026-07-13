# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Running `python3 main.py` produces the output below, which demonstrates both chronological sorting and priority sorting using the Scheduler.

```
Today's Schedule
----------------

08:00 AM - Morning feeding
Pet: Mochi
Duration: 10 minutes
Priority: high
Frequency: daily

10:15 AM - Vet checkup
Pet: Luna
Duration: 45 minutes
Priority: high
Frequency: once

12:00 PM - Litter box cleaning
Pet: Luna
Duration: 15 minutes
Priority: low
Frequency: weekly

06:30 PM - Evening walk
Pet: Mochi
Duration: 30 minutes
Priority: medium
Frequency: daily

Tasks by Priority
-----------------

HIGH - Morning feeding (Mochi)
Time: 08:00 AM
Duration: 10 minutes
Frequency: daily

HIGH - Vet checkup (Luna)
Time: 10:15 AM
Duration: 45 minutes
Frequency: once

MEDIUM - Evening walk (Mochi)
Time: 06:30 PM
Duration: 30 minutes
Frequency: daily

LOW - Litter box cleaning (Luna)
Time: 12:00 PM
Duration: 15 minutes
Frequency: weekly
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

