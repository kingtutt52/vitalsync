import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:vitalsync/core/constants.dart';

const _tokenKey = 'access_token';

/// Singleton Dio instance configured with auth interceptor.
/// Call [ApiClient.instance] to get it.
class ApiClient {
  ApiClient._();
  static final ApiClient _singleton = ApiClient._();
  static ApiClient get instance => _singleton;

  final _storage = const FlutterSecureStorage();

  late final Dio dio = Dio(
    BaseOptions(
      baseUrl: AppConstants.apiBaseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 15),
      headers: {'Content-Type': 'application/json'},
    ),
  )..interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.read(key: _tokenKey);
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (error, handler) {
          // Surface a clean message instead of raw Dio noise
          handler.next(error);
        },
      ),
    );

  Future<void> saveToken(String token) =>
      _storage.write(key: _tokenKey, value: token);

  Future<void> clearToken() => _storage.delete(key: _tokenKey);

  Future<bool> hasToken() async =>
      (await _storage.read(key: _tokenKey)) != null;
}

/// Extracts a human-readable error message from a DioException.
String parseDioError(DioException e) {
  final data = e.response?.data;
  if (data is Map && data['detail'] != null) {
    return data['detail'].toString();
  }
  return e.message ?? 'An unexpected error occurred';
}
