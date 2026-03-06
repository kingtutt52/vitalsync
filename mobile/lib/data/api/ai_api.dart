import 'package:dio/dio.dart';
import 'package:vitalsync/data/api/api_client.dart';
import 'package:vitalsync/data/models/ai_plan.dart';

class AiApi {
  final _client = ApiClient.instance;

  Future<HealthPlan> generatePlan() async {
    try {
      final res = await _client.dio.post('/ai/generate-plan');
      return HealthPlan.fromJson(res.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }
}
