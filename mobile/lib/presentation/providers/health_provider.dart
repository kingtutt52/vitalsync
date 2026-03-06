import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:vitalsync/data/api/health_api.dart';
import 'package:vitalsync/data/models/health.dart';

final healthApiProvider = Provider<HealthApi>((ref) => HealthApi());

final healthSummaryProvider = FutureProvider<HealthSummary>((ref) async {
  return ref.read(healthApiProvider).getSummary();
});

// Notifier that holds submit state for bloodwork form
class BloodworkFormNotifier extends StateNotifier<AsyncValue<void>> {
  BloodworkFormNotifier(this._api) : super(const AsyncValue.data(null));

  final HealthApi _api;

  Future<void> submit(Map<String, dynamic> data) async {
    state = const AsyncValue.loading();
    try {
      await _api.submitBloodwork(data);
      state = const AsyncValue.data(null);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

final bloodworkFormProvider =
    StateNotifierProvider<BloodworkFormNotifier, AsyncValue<void>>(
  (ref) => BloodworkFormNotifier(ref.read(healthApiProvider)),
);

class LifestyleFormNotifier extends StateNotifier<AsyncValue<void>> {
  LifestyleFormNotifier(this._api) : super(const AsyncValue.data(null));

  final HealthApi _api;

  Future<void> submit(Map<String, dynamic> data) async {
    state = const AsyncValue.loading();
    try {
      await _api.submitLifestyle(data);
      state = const AsyncValue.data(null);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

final lifestyleFormProvider =
    StateNotifierProvider<LifestyleFormNotifier, AsyncValue<void>>(
  (ref) => LifestyleFormNotifier(ref.read(healthApiProvider)),
);
