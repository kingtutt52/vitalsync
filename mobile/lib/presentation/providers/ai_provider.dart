import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:vitalsync/data/api/ai_api.dart';
import 'package:vitalsync/data/models/ai_plan.dart';

final aiApiProvider = Provider<AiApi>((ref) => AiApi());

class HealthPlanNotifier extends StateNotifier<AsyncValue<HealthPlan?>> {
  HealthPlanNotifier(this._api) : super(const AsyncValue.data(null));

  final AiApi _api;

  Future<void> generate() async {
    state = const AsyncValue.loading();
    try {
      final plan = await _api.generatePlan();
      state = AsyncValue.data(plan);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

final healthPlanProvider =
    StateNotifierProvider<HealthPlanNotifier, AsyncValue<HealthPlan?>>(
  (ref) => HealthPlanNotifier(ref.read(aiApiProvider)),
);
