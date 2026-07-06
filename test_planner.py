"""
Unit tests for planner.py

Run with: pytest tests/
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from planner import Subject, calculate_priority, generate_study_plan


def test_subject_rejects_invalid_marks():
    with pytest.raises(ValueError):
        Subject(name="Maths", marks_percent=150, difficulty=3, days_to_exam=5)


def test_subject_rejects_invalid_difficulty():
    with pytest.raises(ValueError):
        Subject(name="Maths", marks_percent=50, difficulty=9, days_to_exam=5)


def test_subject_rejects_negative_days():
    with pytest.raises(ValueError):
        Subject(name="Maths", marks_percent=50, difficulty=3, days_to_exam=-1)


def test_weak_subject_gets_higher_priority_than_strong_subject():
    weak = Subject(name="Physics", marks_percent=35, difficulty=4, days_to_exam=3, is_weak_topic=True)
    strong = Subject(name="History", marks_percent=90, difficulty=2, days_to_exam=20)

    assert calculate_priority(weak) > calculate_priority(strong)


def test_closer_exam_increases_priority():
    near = Subject(name="Chemistry", marks_percent=70, difficulty=3, days_to_exam=1)
    far = Subject(name="Chemistry", marks_percent=70, difficulty=3, days_to_exam=30)

    assert calculate_priority(near) > calculate_priority(far)


def test_plan_allocates_more_time_to_higher_priority_subject():
    subjects = [
        Subject(name="Weak Subject", marks_percent=30, difficulty=5, days_to_exam=2, is_weak_topic=True),
        Subject(name="Strong Subject", marks_percent=95, difficulty=1, days_to_exam=60),
    ]
    plan = generate_study_plan(subjects, total_minutes=120)

    weak_block = next(b for b in plan if b.subject == "Weak Subject")
    strong_block = next(b for b in plan if b.subject == "Strong Subject")

    assert weak_block.minutes > strong_block.minutes


def test_plan_respects_total_minutes_roughly():
    subjects = [
        Subject(name="A", marks_percent=50, difficulty=3, days_to_exam=10),
        Subject(name="B", marks_percent=60, difficulty=2, days_to_exam=15),
    ]
    plan = generate_study_plan(subjects, total_minutes=100)
    total_allocated = sum(b.minutes for b in plan)

    # allow small rounding drift, should stay close to requested total
    assert abs(total_allocated - 100) <= 5


def test_plan_raises_on_zero_minutes():
    subjects = [Subject(name="A", marks_percent=50, difficulty=3, days_to_exam=10)]
    with pytest.raises(ValueError):
        generate_study_plan(subjects, total_minutes=0)


def test_plan_empty_subjects_returns_empty_list():
    assert generate_study_plan([], total_minutes=60) == []
