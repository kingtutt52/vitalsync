import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:vitalsync/data/api/api_client.dart';
import 'package:vitalsync/data/api/auth_api.dart';
import 'package:vitalsync/data/models/user.dart';

final authApiProvider = Provider<AuthApi>((ref) => AuthApi());

// Tracks whether the user is logged in. Starts as null (unknown) then resolves.
final authStateProvider = StateNotifierProvider<AuthNotifier, AsyncValue<UserProfile?>>(
  (ref) => AuthNotifier(ref.read(authApiProvider)),
);

class AuthNotifier extends StateNotifier<AsyncValue<UserProfile?>> {
  AuthNotifier(this._api) : super(const AsyncValue.loading()) {
    _init();
  }

  final AuthApi _api;

  Future<void> _init() async {
    final hasToken = await ApiClient.instance.hasToken();
    if (!hasToken) {
      state = const AsyncValue.data(null);
      return;
    }
    try {
      final user = await _api.getMe();
      state = AsyncValue.data(user);
    } catch (_) {
      // Token expired or invalid — treat as logged out
      await ApiClient.instance.clearToken();
      state = const AsyncValue.data(null);
    }
  }

  Future<void> login(String email, String password) async {
    state = const AsyncValue.loading();
    try {
      await _api.login(email: email, password: password);
      final user = await _api.getMe();
      state = AsyncValue.data(user);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> register(String email, String password, String name) async {
    state = const AsyncValue.loading();
    try {
      await _api.register(email: email, password: password, name: name);
      final user = await _api.getMe();
      state = AsyncValue.data(user);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> logout() async {
    await _api.logout();
    state = const AsyncValue.data(null);
  }
}
