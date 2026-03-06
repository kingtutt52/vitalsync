import 'package:dio/dio.dart';
import 'package:vitalsync/data/api/api_client.dart';
import 'package:vitalsync/data/models/subscription.dart';

class BillingApi {
  final _client = ApiClient.instance;

  Future<String> createCheckoutSession(String tier) async {
    try {
      final res = await _client.dio.post('/billing/create-checkout-session', data: {'tier': tier});
      return res.data['checkout_url'] as String;
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }

  Future<SubscriptionStatus> getStatus() async {
    try {
      final res = await _client.dio.get('/billing/status');
      return SubscriptionStatus.fromJson(res.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }
}
