"""
planner.py

Core logic for EduMentor - an adaptive study planning assistant.

The assistant looks at each subject a student provides and works out how
urgently it needs attention today, then splits the student's available
study time across subjects based on that urgency.

Decision factors (this is the "smart, dynamic" part of the assistant):
    1. Performance gap  -> lower marks means more attention needed
    2. Difficulty       -> harder subjects need more time per topic
    3. Exam proximity   -> subjects with exams coming up soon are boosted
    4. Weak topic flag  -> subjects explicitly marked as weak get extra weight
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Subject:
    name: str
    marks_percent: float          # 0-100, most recent score/understanding level
    difficulty: int               # 1 (easy) - 5 (very hard)
    days_to_exam: int             # days left until exam/test for this subject
    is_weak_topic: bool = False   # student self-reports this as a weak area

    def __post_init__(self):
        if not (0 <= self.marks_percent <= 100):
            raise ValueError(f"marks_percent for '{self.name}' must be between 0 and 100")
        if not (1 <= self.difficulty <= 5):
            raise ValueError(f"difficulty for '{self.name}' must be between 1 and 5")
        if self.days_to_exam < 0:
            raise ValueError(f"days_to_exam for '{self.name}' cannot be negative")


@dataclass
class StudyBlock:
    subject: str
    minutes: int
    priority_score: float
    reason: str


def calculate_priority(subject: Subject) -> float:
    """
    Returns a priority score for a subject. Higher score = needs more
    study time today.

    Formula (weights chosen so no single factor dominates):
        performance_gap  = (100 - marks_percent) / 100      -> 0 to 1
        difficulty_score = difficulty / 5                    -> 0.2 to 1
        urgency_score    = 1 / (days_to_exam + 1)             -> decays as exam gets closer... wait, increases
        weak_bonus       = 0.15 if is_weak_topic else 0

    Note: urgency_score is defined so that closer exams (smaller days_to_exam)
    produce a LARGER value, since 1/(small number) is large.
    """
    performance_gap = (100 - subject.marks_percent) / 100
    difficulty_score = subject.difficulty / 5
    urgency_score = 1 / (subject.days_to_exam + 1)
    weak_bonus = 0.15 if subject.is_weak_topic else 0.0

    score = (0.4 * performance_gap) + (0.25 * difficulty_score) + (0.25 * urgency_score) + weak_bonus
    return round(score, 4)


def _priority_reason(subject: Subject, score: float) -> str:
    """Generates a short human-readable explanation for why a subject got its score."""
    reasons = []
    if subject.marks_percent < 50:
        reasons.append("low current marks")
    if subject.difficulty >= 4:
        reasons.append("high difficulty")
    if subject.days_to_exam <= 3:
        reasons.append("exam very close")
    if subject.is_weak_topic:
        reasons.append("marked as weak topic")
    if not reasons:
        reasons.append("routine revision")
    return ", ".join(reasons)


def generate_study_plan(subjects: List[Subject], total_minutes: int) -> List[StudyBlock]:
    """
    Distributes total_minutes across subjects proportional to their priority
    score. Every subject gets at least a small minimum block so nothing is
    fully ignored, then the remainder is distributed by priority weight.
    """
    if total_minutes <= 0:
        raise ValueError("total_minutes must be greater than 0")
    if not subjects:
        return []

    scored = [(s, calculate_priority(s)) for s in subjects]
    total_score = sum(score for _, score in scored)

    min_block = 10  # every subject gets at least 10 minutes if time allows
    reserved = min(min_block * len(subjects), total_minutes)
    remaining_minutes = total_minutes - reserved

    plan = []
    for subject, score in scored:
        base = min_block if reserved == min_block * len(subjects) else int(total_minutes / len(subjects))
        share = (score / total_score) * remaining_minutes if total_score > 0 else 0
        minutes = int(base + share)
        plan.append(StudyBlock(
            subject=subject.name,
            minutes=minutes,
            priority_score=score,
            reason=_priority_reason(subject, score),
        ))

    # Sort so the highest priority subject is shown first
    plan.sort(key=lambda block: block.priority_score, reverse=True)
    return plan
