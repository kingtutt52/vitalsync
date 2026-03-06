import 'package:dio/dio.dart';
import 'package:vitalsync/data/api/api_client.dart';
import 'package:vitalsync/data/models/health.dart';

class HealthApi {
  final _client = ApiClient.instance;

  Future<BloodworkEntry> submitBloodwork(Map<String, dynamic> data) async {
    try {
      final res = await _client.dio.post('/health/bloodwork', data: data);
      return BloodworkEntry.fromJson(res.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }

  Future<List<BloodworkEntry>> getBloodwork() async {
    try {
      final res = await _client.dio.get('/health/bloodwork');
      return (res.data as List)
          .map((j) => BloodworkEntry.fromJson(j as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }

  Future<void> submitLifestyle(Map<String, dynamic> data) async {
    try {
      await _client.dio.post('/health/lifestyle', data: data);
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }

  Future<HealthSummary> getSummary() async {
    try {
      final res = await _client.dio.get('/health/summary');
      return HealthSummary.fromJson(res.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }
}
