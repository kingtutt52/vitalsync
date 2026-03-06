class Subscores {
  final double metabolic;
  final double lipids;
  final double sleepRecovery;
  final double hormones;
  final double inflammation;

  const Subscores({
    required this.metabolic,
    required this.lipids,
    required this.sleepRecovery,
    required this.hormones,
    required this.inflammation,
  });

  factory Subscores.fromJson(Map<String, dynamic> j) => Subscores(
        metabolic: (j['metabolic'] as num).toDouble(),
        lipids: (j['lipids'] as num).toDouble(),
        sleepRecovery: (j['sleep_recovery'] as num).toDouble(),
        hormones: (j['hormones'] as num).toDouble(),
        inflammation: (j['inflammation'] as num).toDouble(),
      );
}

class HealthPlan {
  final double healthScore;
  final Subscores subscores;
  final List<String> insights;
  final List<String> actions;
  final String disclaimer;

  const HealthPlan({
    required this.healthScore,
    required this.subscores,
    required this.insights,
    required this.actions,
    required this.disclaimer,
  });

  factory HealthPlan.fromJson(Map<String, dynamic> j) => HealthPlan(
        healthScore: (j['health_score'] as num).toDouble(),
        subscores: Subscores.fromJson(j['subscores'] as Map<String, dynamic>),
        insights: List<String>.from(j['insights'] as List),
        actions: List<String>.from(j['actions'] as List),
        disclaimer: j['disclaimer'] as String,
      );
}
