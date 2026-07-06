const subjectsContainer = document.getElementById("subjects-container");
const template = document.getElementById("subject-row-template");
const addBtn = document.getElementById("add-subject-btn");
const form = document.getElementById("planner-form");
const errorText = document.getElementById("form-error");
const planOutput = document.getElementById("plan-output");

function addSubjectRow() {
    const clone = template.content.cloneNode(true);
    const removeBtn = clone.querySelector(".remove-subject-btn");
    removeBtn.addEventListener("click", (event) => {
        event.target.closest(".subject-row").remove();
    });
    subjectsContainer.appendChild(clone);
}

addBtn.addEventListener("click", addSubjectRow);

// Start with two subject rows so the form isn't empty
addSubjectRow();
addSubjectRow();

function collectSubjects() {
    const rows = subjectsContainer.querySelectorAll(".subject-row");
    const subjects = [];
    for (const row of rows) {
        const name = row.querySelector(".subj-name").value.trim();
        if (!name) continue;
        subjects.push({
            name,
            marks_percent: Number(row.querySelector(".subj-marks").value),
            difficulty: Number(row.querySelector(".subj-difficulty").value),
            days_to_exam: Number(row.querySelector(".subj-days").value),
            is_weak_topic: row.querySelector(".subj-weak").checked,
        });
    }
    return subjects;
}

function renderPlan(plan) {
    if (!plan.length) {
        planOutput.innerHTML = "<p>No plan could be generated.</p>";
        return;
    }
    const list = document.createElement("ol");
    list.setAttribute("aria-label", "Prioritized study plan");
    for (const block of plan) {
        const item = document.createElement("li");
        item.innerHTML = `
            <strong>${block.subject}</strong> &mdash; ${block.minutes} minutes
            <br><span class="reason-text">Why: ${block.reason} (priority score ${block.priority_score})</span>
        `;
        list.appendChild(item);
    }
    planOutput.innerHTML = "";
    planOutput.appendChild(list);
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorText.textContent = "";

    const totalMinutes = Number(document.getElementById("total-minutes").value);
    const subjects = collectSubjects();

    if (!subjects.length) {
        errorText.textContent = "Please add at least one subject with a name.";
        return;
    }

    const generateBtn = document.getElementById("generate-btn");
    generateBtn.disabled = true;
    generateBtn.textContent = "Generating...";

    try {
        const response = await fetch("/api/plan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ total_minutes: totalMinutes, subjects }),
        });
        const data = await response.json();

        if (!response.ok) {
            errorText.textContent = data.error || "Something went wrong. Please check your inputs.";
            return;
        }
        renderPlan(data.plan);
    } catch (err) {
        errorText.textContent = "Could not reach the server. Please try again.";
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = "Generate my study plan";
    }
});
