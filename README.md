# EduMentor - Adaptive Study Planning Assistant

## Chosen Vertical

**EdTech / Learning Assistant.**

EduMentor is built for the persona of a student juggling multiple subjects
with different exam dates, difficulty levels, and current performance. It
acts as a lightweight personal tutor that decides, every day, *which subject
deserves attention right now and for how long*.

## Approach and Logic

The core idea is that a student's limited study time should not be split
evenly across subjects. Some subjects need more attention than others based
on real, changing context. EduMentor scores each subject using four factors:

| Factor | What it captures | Why it matters |
|---|---|---|
| Performance gap | `(100 - current marks) / 100` | Weaker subjects get more time |
| Difficulty | subject difficulty (1-5) / 5 | Harder subjects need more time per topic |
| Exam proximity | `1 / (days_to_exam + 1)` | Subjects with exams coming up soon are boosted |
| Weak-topic flag | student self-reports a weak area | Adds a fixed bonus on top of the calculated score |

These are combined into a single **priority score** per subject
(`planner.calculate_priority`). The total available study time is then
distributed across subjects proportional to their priority score, with a
small guaranteed minimum per subject so nothing gets fully ignored
(`planner.generate_study_plan`).

This is the "dynamic decision making" part of the assignment: the plan
changes automatically as the student's inputs change — a subject that was
low priority yesterday can become the top priority today if its exam is now
closer, or if the student updates their marks.

## How the Solution Works

1. **`planner.py`** — pure logic layer. Defines the `Subject` data model with
   input validation, the priority scoring formula, and the time-allocation
   algorithm. This file has no web/UI dependencies, so it is independently
   testable and reusable.
2. **`app.py`** — a small Flask API layer. Exposes `/` (the UI) and
   `POST /api/plan` (accepts subject data as JSON, validates it defensively,
   and returns a prioritized plan).
3. **`templates/index.html` + `static/`** — a simple, accessible front end.
   Students add subjects through a form, submit it, and see their generated
   plan with an explanation of *why* each subject got its allotted time.
4. **`tests/`** — unit tests for the scoring/allocation logic and integration
   tests for the API endpoint, covering both valid and invalid inputs.

### Running it locally

```bash
pip install -r requirements.txt
python app.py
# open http://localhost:5000 in a browser
```

### Running the tests

```bash
pytest tests/
```

## Security Notes

- All user input from the API is validated server-side (type, range, and
  length checks) before being used — the front end is never trusted on its
  own.
- Subject name length and count are capped to prevent oversized or abusive
  payloads.
- `app.run()` does not enable debug mode by default, avoiding the Flask
  debugger/reloader being exposed in a real deployment.
- No external network calls, no secrets, no user data is persisted or
  logged, so there is no data-retention or credential-leak surface.

## Accessibility Notes

- Semantic HTML (`<fieldset>`, `<legend>`, `<label>`) so form fields are
  properly associated with their labels for screen readers.
- Visible focus outlines on all interactive elements for keyboard
  navigation.
- `aria-live="polite"` on the plan output so screen readers announce the
  generated plan without needing a page reload.
- Error messages use `role="alert"` so they are announced immediately.

## Assumptions Made

- A student manually enters their current marks/understanding level per
  subject rather than this being pulled from an external gradebook system
  (no such integration was in scope for this challenge).
- "Difficulty" is a subjective 1-5 self-rating by the student rather than a
  standardized external metric.
- The tool plans for a single day at a time; multi-day/weekly planning could
  be a natural extension but was kept out of scope to stay focused.
- The priority formula's weights (0.4 / 0.25 / 0.25 + 0.15 bonus) were
  chosen so that no single factor (e.g., just exam proximity) can dominate
  the decision — this can be tuned further with real usage data.
