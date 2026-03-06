"""
Unit tests for the rules-based health scoring engine.
Run with: pytest app/tests/test_health_score.py -v
"""
from datetime import date
import pytest

from app.models.health import BloodworkEntry, LifestyleEntry
from app.services.health_score import compute_health_plan


def make_bloodwork(**kwargs) -> BloodworkEntry:
    defaults = dict(
        id="test",
        user_id="user1",
        test_date=date.today(),
        vitamin_d=None,
        ldl=None,
        hdl=None,
        triglycerides=None,
        a1c=None,
        fasting_glucose=None,
        crp=None,
        testosterone_total=None,
    )
    defaults.update(kwargs)
    bw = BloodworkEntry.__new__(BloodworkEntry)
    bw.__dict__.update(defaults)
    return bw


def make_lifestyle(**kwargs) -> LifestyleEntry:
    defaults = dict(
        id="test",
        user_id="user1",
        entry_date=date.today(),
        sleep_hours=None,
        steps=None,
        resting_hr=None,
        hrv=None,
        workout_minutes=None,
        stress_1_10=None,
        diet_notes=None,
    )
    defaults.update(kwargs)
    ls = LifestyleEntry.__new__(LifestyleEntry)
    ls.__dict__.update(defaults)
    return ls


class TestBloodworkRules:
    def test_perfect_bloodwork_stays_near_base(self):
        bw = make_bloodwork(
            vitamin_d=50, ldl=80, hdl=65, triglycerides=90,
            a1c=5.2, fasting_glucose=85, crp=0.5, testosterone_total=600
        )
        result = compute_health_plan(bw, None)
        # HDL bonus of +3, everything else at 0 → 83
        assert result.health_score == 83.0

    def test_low_vitamin_d_deducts_points(self):
        bw = make_bloodwork(vitamin_d=18)
        result = compute_health_plan(bw, None)
        assert result.health_score < 80
        assert any("Vitamin D" in a for a in result.actions)

    def test_insufficient_vitamin_d_deducts_8(self):
        bw = make_bloodwork(vitamin_d=25)
        result = compute_health_plan(bw, None)
        assert result.health_score == 72.0

    def test_high_ldl_deducts_points(self):
        bw = make_bloodwork(ldl=145)
        result = compute_health_plan(bw, None)
        assert result.health_score < 80
        assert any("LDL" in i for i in result.insights)

    def test_prediabetic_a1c_deducts_10(self):
        bw = make_bloodwork(a1c=5.9)
        result = compute_health_plan(bw, None)
        assert result.health_score == 70.0

    def test_elevated_crp_deducts_points(self):
        bw = make_bloodwork(crp=4.0)
        result = compute_health_plan(bw, None)
        assert result.health_score < 80
        assert any("CRP" in i or "inflammation" in i.lower() for i in result.insights)

    def test_low_testosterone_deducts_6(self):
        bw = make_bloodwork(testosterone_total=350)
        result = compute_health_plan(bw, None)
        assert result.health_score == 74.0

    def test_score_capped_at_100(self):
        bw = make_bloodwork(hdl=70)  # only +3
        result = compute_health_plan(bw, None)
        assert result.health_score <= 100.0

    def test_score_floored_at_0(self):
        bw = make_bloodwork(
            vitamin_d=10, ldl=200, a1c=7.0, crp=6.0,
            testosterone_total=200, triglycerides=250, fasting_glucose=140
        )
        result = compute_health_plan(bw, None)
        assert result.health_score >= 0.0


class TestLifestyleRules:
    def test_poor_sleep_deducts_points(self):
        ls = make_lifestyle(sleep_hours=5.5)
        result = compute_health_plan(None, ls)
        assert result.health_score < 80
        assert any("sleep" in a.lower() for a in result.actions)

    def test_low_steps_deducts_points(self):
        ls = make_lifestyle(steps=4000)
        result = compute_health_plan(None, ls)
        assert result.health_score == 74.0

    def test_high_stress_deducts_points(self):
        ls = make_lifestyle(stress_1_10=9)
        result = compute_health_plan(None, ls)
        assert result.health_score < 80

    def test_low_hrv_deducts_3(self):
        ls = make_lifestyle(hrv=20)
        result = compute_health_plan(None, ls)
        assert result.health_score == 77.0

    def test_no_data_returns_base_score_with_message(self):
        result = compute_health_plan(None, None)
        assert result.health_score == 80.0
        assert len(result.insights) == 1
        assert "No health data" in result.insights[0]


class TestSubscores:
    def test_subscores_present(self):
        bw = make_bloodwork(ldl=150)
        result = compute_health_plan(bw, None)
        assert "metabolic" in result.subscores
        assert "lipids" in result.subscores
        assert "sleep_recovery" in result.subscores
        assert "hormones" in result.subscores
        assert "inflammation" in result.subscores

    def test_lipids_subscore_affected_by_ldl(self):
        bw_bad = make_bloodwork(ldl=150)
        bw_good = make_bloodwork(ldl=80)
        r_bad = compute_health_plan(bw_bad, None)
        r_good = compute_health_plan(bw_good, None)
        assert r_bad.subscores["lipids"] < r_good.subscores["lipids"]
