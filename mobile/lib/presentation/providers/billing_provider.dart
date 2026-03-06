import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:vitalsync/data/api/billing_api.dart';
import 'package:vitalsync/data/models/subscription.dart';

final billingApiProvider = Provider<BillingApi>((ref) => BillingApi());

final subscriptionStatusProvider = FutureProvider<SubscriptionStatus>((ref) async {
  return ref.read(billingApiProvider).getStatus();
});

class CheckoutNotifier extends StateNotifier<AsyncValue<String?>> {
  CheckoutNotifier(this._api) : super(const AsyncValue.data(null));

  final BillingApi _api;

  Future<String?> createCheckout(String tier) async {
    state = const AsyncValue.loading();
    try {
      final url = await _api.createCheckoutSession(tier);
      state = AsyncValue.data(url);
      return url;
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
      return null;
    }
  }
}

final checkoutProvider =
    StateNotifierProvider<CheckoutNotifier, AsyncValue<String?>>(
  (ref) => CheckoutNotifier(ref.read(billingApiProvider)),
);
