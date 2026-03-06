class BloodworkEntry {
  final String id;
  final String userId;
  final DateTime testDate;
  final double? vitaminD;
  final double? ldl;
  final double? hdl;
  final double? triglycerides;
  final double? a1c;
  final double? fastingGlucose;
  final double? crp;
  final double? testosteroneTotal;

  const BloodworkEntry({
    required this.id,
    required this.userId,
    required this.testDate,
    this.vitaminD,
    this.ldl,
    this.hdl,
    this.triglycerides,
    this.a1c,
    this.fastingGlucose,
    this.crp,
    this.testosteroneTotal,
  });

  factory BloodworkEntry.fromJson(Map<String, dynamic> j) => BloodworkEntry(
        id: j['id'] as String,
        userId: j['user_id'] as String,
        testDate: DateTime.parse(j['test_date'] as String),
        vitaminD: (j['vitamin_d'] as num?)?.toDouble(),
        ldl: (j['ldl'] as num?)?.toDouble(),
        hdl: (j['hdl'] as num?)?.toDouble(),
        triglycerides: (j['triglycerides'] as num?)?.toDouble(),
        a1c: (j['a1c'] as num?)?.toDouble(),
        fastingGlucose: (j['fasting_glucose'] as num?)?.toDouble(),
        crp: (j['crp'] as num?)?.toDouble(),
        testosteroneTotal: (j['testosterone_total'] as num?)?.toDouble(),
      );
}

class LifestyleEntry {
  final String id;
  final String userId;
  final DateTime entryDate;
  final double? sleepHours;
  final int? steps;
  final int? restingHr;
  final double? hrv;
  final int? workoutMinutes;
  final int? stress1To10;
  final String? dietNotes;

  const LifestyleEntry({
    required this.id,
    required this.userId,
    required this.entryDate,
    this.sleepHours,
    this.steps,
    this.restingHr,
    this.hrv,
    this.workoutMinutes,
    this.stress1To10,
    this.dietNotes,
  });

  factory LifestyleEntry.fromJson(Map<String, dynamic> j) => LifestyleEntry(
        id: j['id'] as String,
        userId: j['user_id'] as String,
        entryDate: DateTime.parse(j['entry_date'] as String),
        sleepHours: (j['sleep_hours'] as num?)?.toDouble(),
        steps: j['steps'] as int?,
        restingHr: j['resting_hr'] as int?,
        hrv: (j['hrv'] as num?)?.toDouble(),
        workoutMinutes: j['workout_minutes'] as int?,
        stress1To10: j['stress_1_10'] as int?,
        dietNotes: j['diet_notes'] as String?,
      );
}

class HealthSummary {
  final BloodworkEntry? latestBloodwork;
  final LifestyleEntry? latestLifestyle;
  final int bloodworkCount;
  final int lifestyleCount;

  const HealthSummary({
    this.latestBloodwork,
    this.latestLifestyle,
    required this.bloodworkCount,
    required this.lifestyleCount,
  });

  factory HealthSummary.fromJson(Map<String, dynamic> j) => HealthSummary(
        latestBloodwork: j['latest_bloodwork'] != null
            ? BloodworkEntry.fromJson(j['latest_bloodwork'] as Map<String, dynamic>)
            : null,
        latestLifestyle: j['latest_lifestyle'] != null
            ? LifestyleEntry.fromJson(j['latest_lifestyle'] as Map<String, dynamic>)
            : null,
        bloodworkCount: j['bloodwork_count'] as int,
        lifestyleCount: j['lifestyle_count'] as int,
      );
}
