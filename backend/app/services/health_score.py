"""
Rules-based health scoring engine (MVP).

Design intent:
- Deterministic and auditable — every point deduction maps to a named rule.
- Each rule returns (delta: float, insight: str, action: str | None).
- Subscores are computed independently and averaged into the final score.
- This module is the single integration point; swap or extend it to add ML later.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from app.models.health import BloodworkEntry, LifestyleEntry


@dataclass
class RuleResult:
    delta: float
    insight: str
    action: Optional[str] = None


@dataclass
class ScoringOutput:
    health_score: float
    subscores: Dict[str, float]
    insights: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Individual rule functions
# ---------------------------------------------------------------------------

def _rule_vitamin_d(bw: BloodworkEntry) -> List[RuleResult]:
    results = []
    if bw.vitamin_d is None:
        return results
    if bw.vitamin_d < 20:
        results.append(RuleResult(
            delta=-12,
            insight=f"Vitamin D is critically low ({bw.vitamin_d} ng/mL; optimal ≥ 40).",
            action="Consider vitamin D3 + K2 supplementation (2000–5000 IU/day). Verify levels with your clinician.",
        ))
    elif bw.vitamin_d < 30:
        results.append(RuleResult(
            delta=-8,
            insight=f"Vitamin D is insufficient ({bw.vitamin_d} ng/mL; optimal ≥ 40).",
            action="Consider vitamin D3 supplementation (1000–2000 IU/day) and increase sunlight exposure.",
        ))
    elif bw.vitamin_d > 100:
        results.append(RuleResult(
            delta=-5,
            insight=f"Vitamin D may be elevated ({bw.vitamin_d} ng/mL). Toxicity is rare but possible above 150 ng/mL.",
            action="Discuss dosage with your clinician to ensure safe supplementation levels.",
        ))
    else:
        results.append(RuleResult(delta=0, insight=f"Vitamin D is in range ({bw.vitamin_d} ng/mL)."))
    return results


def _rule_ldl(bw: BloodworkEntry) -> List[RuleResult]:
    results = []
    if bw.ldl is None:
        return results
    if bw.ldl > 160:
        results.append(RuleResult(
            delta=-12,
            insight=f"LDL cholesterol is high ({bw.ldl} mg/dL; optimal < 100).",
            action="Reduce saturated fat and trans fats. Increase soluble fiber (oats, legumes). Consider requesting an ApoB test.",
        ))
    elif bw.ldl > 130:
        results.append(RuleResult(
            delta=-8,
            insight=f"LDL cholesterol is borderline high ({bw.ldl} mg/dL; optimal < 100).",
            action="Reduce saturated fat, increase fiber and omega-3 intake. Consider ApoB or LDL-P particle count for a fuller picture.",
        ))
    else:
        results.append(RuleResult(delta=0, insight=f"LDL cholesterol is acceptable ({bw.ldl} mg/dL)."))
    return results


def _rule_hdl(bw: BloodworkEntry) -> List[RuleResult]:
    results = []
    if bw.hdl is None:
        return results
    if bw.hdl < 40:
        results.append(RuleResult(
            delta=-8,
            insight=f"HDL cholesterol is low ({bw.hdl} mg/dL; optimal > 60).",
            action="Increase aerobic exercise, consume more healthy fats (avocado, olive oil, nuts), and reduce refined carbohydrates.",
        ))
    elif bw.hdl >= 60:
        results.append(RuleResult(delta=3, insight=f"HDL cholesterol is optimal ({bw.hdl} mg/dL). Good cardiovascular protection."))
    return results


def _rule_triglycerides(bw: BloodworkEntry) -> List[RuleResult]:
    results = []
    if bw.triglycerides is None:
        return results
    if bw.triglycerides > 200:
        results.append(RuleResult(
            delta=-10,
            insight=f"Triglycerides are high ({bw.triglycerides} mg/dL; optimal < 100).",
            action="Reduce refined carbohydrates, sugar, and alcohol. Increase omega-3 fatty acids and regular aerobic exercise.",
        ))
    elif bw.triglycerides > 150:
        results.append(RuleResult(
            delta=-5,
            insight=f"Triglycerides are borderline ({bw.triglycerides} mg/dL; optimal < 100).",
            action="Limit sugar and processed carbs. Consider fish oil supplementation.",
        ))
    else:
        results.append(RuleResult(delta=0, insight=f"Triglycerides are in range ({bw.triglycerides} mg/dL)."))
    return results


def _rule_a1c(bw: BloodworkEntry) -> List[RuleResult]:
    results = []
    if bw.a1c is None:
        return results
    if bw.a1c >= 6.5:
        results.append(RuleResult(
            delta=-15,
            insight=f"HbA1c is in diabetic range ({bw.a1c}%; diagnostic threshold ≥ 6.5%). Urgent medical review needed.",
            action="Consult your physician promptly. Reduce added sugars, refined carbs. Increase activity. Consider CGM.",
        ))
    elif bw.a1c >= 5.7:
        results.append(RuleResult(
            delta=-10,
            insight=f"HbA1c indicates pre-diabetes ({bw.a1c}%; normal < 5.7%).",
            action="Reduce added sugar and refined carbohydrates. Increase daily movement. A continuous glucose monitor (CGM) can provide useful feedback.",
        ))
    else:
        results.append(RuleResult(delta=0, insight=f"HbA1c is normal ({bw.a1c}%)."))
    return results


def _rule_fasting_glucose(bw: BloodworkEntry) -> List[RuleResult]:
    results = []
    if bw.fasting_glucose is None:
        return results
    if bw.fasting_glucose >= 126:
        results.append(RuleResult(
            delta=-10,
            insight=f"Fasting glucose is in diabetic range ({bw.fasting_glucose} mg/dL; normal < 100).",
            action="Seek medical evaluation. Dietary carbohydrate reduction and exercise intervention are first-line.",
        ))
    elif bw.fasting_glucose >= 100:
        results.append(RuleResult(
            delta=-5,
            insight=f"Fasting glucose is elevated ({bw.fasting_glucose} mg/dL; pre-diabetic range 100–125).",
            action="Reduce refined carbohydrates. Time meals appropriately. Walk after eating.",
        ))
    else:
        results.append(RuleResult(delta=0, insight=f"Fasting glucose is normal ({bw.fasting_glucose} mg/dL)."))
    return results


def _rule_crp(bw: BloodworkEntry) -> List[RuleResult]:
    results = []
    if bw.crp is None:
        return results
    if bw.crp > 3:
        results.append(RuleResult(
            delta=-8,
            insight=f"High-sensitivity CRP is elevated ({bw.crp} mg/L; low-risk < 1.0).",
            action="Address chronic inflammation: prioritize sleep, reduce ultra-processed foods, add omega-3s, manage stress, and ensure adequate recovery between workouts.",
        ))
    elif bw.crp > 1:
        results.append(RuleResult(
            delta=-4,
            insight=f"hsCRP is in the intermediate range ({bw.crp} mg/L). Monitor and investigate root causes.",
            action="Improve sleep quality, add anti-inflammatory foods (fatty fish, leafy greens, turmeric), and reduce chronic stress.",
        ))
    else:
        results.append(RuleResult(delta=0, insight=f"CRP (inflammation marker) is low ({bw.crp} mg/L). Good."))
    return results


def _rule_testosterone(bw: BloodworkEntry) -> List[RuleResult]:
    results = []
    if bw.testosterone_total is None:
        return results
    if bw.testosterone_total < 300:
        results.append(RuleResult(
            delta=-10,
            insight=f"Total testosterone is low ({bw.testosterone_total} ng/dL; typical optimal 500–900).",
            action="Prioritize sleep (7–9 hrs), resistance training, and stress reduction. Check zinc, vitamin D, and magnesium levels. Consult an endocrinologist.",
        ))
    elif bw.testosterone_total < 400:
        results.append(RuleResult(
            delta=-6,
            insight=f"Total testosterone is below optimal ({bw.testosterone_total} ng/dL).",
            action="Optimize sleep, compound strength training, adequate dietary fat, and stress management. Consider checking free testosterone and SHBG.",
        ))
    else:
        results.append(RuleResult(delta=0, insight=f"Total testosterone is in acceptable range ({bw.testosterone_total} ng/dL)."))
    return results


def _rule_sleep(ls: LifestyleEntry) -> List[RuleResult]:
    results = []
    if ls.sleep_hours is None:
        return results
    if ls.sleep_hours < 6:
        results.append(RuleResult(
            delta=-10,
            insight=f"Sleep duration is critically short ({ls.sleep_hours} hrs; recommended 7–9).",
            action="Prioritize sleep as a non-negotiable health input. Set a consistent bedtime, reduce screen time 1 hr before bed, and keep room cool and dark.",
        ))
    elif ls.sleep_hours < 7:
        results.append(RuleResult(
            delta=-6,
            insight=f"Sleep duration is below optimal ({ls.sleep_hours} hrs; recommended 7–9).",
            action="Improve your sleep routine: consistent schedule, limit caffeine after 2 PM, and manage evening light exposure.",
        ))
    else:
        results.append(RuleResult(delta=0, insight=f"Sleep duration is healthy ({ls.sleep_hours} hrs)."))
    return results


def _rule_steps(ls: LifestyleEntry) -> List[RuleResult]:
    results = []
    if ls.steps is None:
        return results
    if ls.steps < 5000:
        results.append(RuleResult(
            delta=-6,
            insight=f"Daily step count is very low ({ls.steps:,} steps; target ≥ 8,000).",
            action="Add short walks throughout the day. Even 3–5 minute walking breaks every hour meaningfully reduce sedentary risk.",
        ))
    elif ls.steps < 7000:
        results.append(RuleResult(
            delta=-4,
            insight=f"Daily steps are below the recommended threshold ({ls.steps:,}; target ≥ 8,000).",
            action="Aim for at least 8,000 steps per day. Park farther away, take stairs, or schedule a 20-minute walk.",
        ))
    else:
        results.append(RuleResult(delta=0, insight=f"Step count is solid ({ls.steps:,} steps/day)."))
    return results


def _rule_workout(ls: LifestyleEntry) -> List[RuleResult]:
    results = []
    if ls.workout_minutes is None:
        return results
    # Compare against weekly guideline (150 min/week = ~21 min/day tracked)
    # We treat a single lifestyle entry as a snapshot; threshold here is 30 min/session
    if ls.workout_minutes < 20:
        results.append(RuleResult(
            delta=-4,
            insight=f"Workout duration is low this session ({ls.workout_minutes} min).",
            action="Aim for at least 150 minutes of moderate-intensity exercise per week (e.g., 30 min × 5 days). Strength training 2× per week is also recommended.",
        ))
    return results


def _rule_stress(ls: LifestyleEntry) -> List[RuleResult]:
    results = []
    if ls.stress_1_10 is None:
        return results
    if ls.stress_1_10 >= 8:
        results.append(RuleResult(
            delta=-6,
            insight=f"Reported stress is very high ({ls.stress_1_10}/10). Chronic high stress elevates cortisol and impairs recovery.",
            action="Implement daily stress-reduction practices: breathwork (box breathing, 4-7-8), mindfulness, and adequate downtime. Evaluate workload and boundaries.",
        ))
    elif ls.stress_1_10 >= 7:
        results.append(RuleResult(
            delta=-4,
            insight=f"Reported stress is elevated ({ls.stress_1_10}/10).",
            action="Add short mindfulness or breathing sessions. Consider journaling or reducing decision fatigue.",
        ))
    return results


def _rule_hrv(ls: LifestyleEntry) -> List[RuleResult]:
    results = []
    if ls.hrv is None:
        return results
    # HRV is highly individual; a value below 30 ms is generally low for most adults
    if ls.hrv < 30:
        results.append(RuleResult(
            delta=-3,
            insight=f"HRV is low ({ls.hrv} ms), suggesting poor autonomic recovery.",
            action="Prioritize sleep, reduce alcohol, manage stress, and ensure adequate recovery days between intense workouts.",
        ))
    return results


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def compute_health_plan(
    bloodwork: Optional[BloodworkEntry],
    lifestyle: Optional[LifestyleEntry],
) -> ScoringOutput:
    """
    Compute the full health score and action plan.
    Base score is 80. Rules add or subtract points up to the 0–100 range.
    """
    BASE = 80.0

    # Subscore buckets accumulate their own deltas
    metabolic_delta = 0.0
    lipids_delta = 0.0
    sleep_delta = 0.0
    hormones_delta = 0.0
    inflammation_delta = 0.0

    all_insights: List[str] = []
    all_actions: List[str] = []

    def apply(results: List[RuleResult], bucket: str):
        nonlocal metabolic_delta, lipids_delta, sleep_delta, hormones_delta, inflammation_delta
        for r in results:
            all_insights.append(r.insight)
            if r.action:
                all_actions.append(r.action)
            if bucket == "metabolic":
                metabolic_delta += r.delta
            elif bucket == "lipids":
                lipids_delta += r.delta
            elif bucket == "sleep":
                sleep_delta += r.delta
            elif bucket == "hormones":
                hormones_delta += r.delta
            elif bucket == "inflammation":
                inflammation_delta += r.delta

    if bloodwork:
        apply(_rule_vitamin_d(bloodwork), "metabolic")
        apply(_rule_a1c(bloodwork), "metabolic")
        apply(_rule_fasting_glucose(bloodwork), "metabolic")
        apply(_rule_ldl(bloodwork), "lipids")
        apply(_rule_hdl(bloodwork), "lipids")
        apply(_rule_triglycerides(bloodwork), "lipids")
        apply(_rule_crp(bloodwork), "inflammation")
        apply(_rule_testosterone(bloodwork), "hormones")

    if lifestyle:
        apply(_rule_sleep(lifestyle), "sleep")
        apply(_rule_steps(lifestyle), "sleep")
        apply(_rule_workout(lifestyle), "sleep")
        apply(_rule_stress(lifestyle), "sleep")
        apply(_rule_hrv(lifestyle), "sleep")

    # Cap each subscore between 0 and 100
    def subscore(base: float, delta: float) -> float:
        return max(0.0, min(100.0, base + delta))

    metabolic = subscore(80, metabolic_delta)
    lipids = subscore(80, lipids_delta)
    sleep_recovery = subscore(80, sleep_delta)
    hormones = subscore(80, hormones_delta)
    inflammation = subscore(80, inflammation_delta)

    total_delta = (
        metabolic_delta + lipids_delta + sleep_delta + hormones_delta + inflammation_delta
    )
    final_score = max(0.0, min(100.0, BASE + total_delta))

    if not all_insights:
        all_insights.append(
            "No health data found. Add bloodwork or lifestyle data to generate a personalised plan."
        )

    return ScoringOutput(
        health_score=round(final_score, 1),
        subscores={
            "metabolic": round(metabolic, 1),
            "lipids": round(lipids, 1),
            "sleep_recovery": round(sleep_recovery, 1),
            "hormones": round(hormones, 1),
            "inflammation": round(inflammation, 1),
        },
        insights=all_insights,
        actions=list(dict.fromkeys(all_actions)),  # deduplicate while preserving order
    )
