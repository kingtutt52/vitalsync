import 'package:dio/dio.dart';
import 'package:vitalsync/data/api/api_client.dart';
import 'package:vitalsync/data/models/user.dart';

class AuthApi {
  final _client = ApiClient.instance;

  Future<String> register({
    required String email,
    required String password,
    required String name,
  }) async {
    try {
      final res = await _client.dio.post('/auth/register', data: {
        'email': email,
        'password': password,
        'name': name,
      });
      final token = res.data['access_token'] as String;
      await _client.saveToken(token);
      return token;
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }

  Future<String> login({
    required String email,
    required String password,
  }) async {
    try {
      final res = await _client.dio.post('/auth/login', data: {
        'email': email,
        'password': password,
      });
      final token = res.data['access_token'] as String;
      await _client.saveToken(token);
      return token;
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }

  Future<UserProfile> getMe() async {
    try {
      final res = await _client.dio.get('/auth/me');
      return UserProfile.fromJson(res.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }

  Future<void> logout() => _client.clearToken();
}
