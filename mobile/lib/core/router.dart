import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:vitalsync/presentation/providers/auth_provider.dart';
import 'package:vitalsync/presentation/screens/auth/login_screen.dart';
import 'package:vitalsync/presentation/screens/auth/register_screen.dart';
import 'package:vitalsync/presentation/screens/dashboard/dashboard_screen.dart';
import 'package:vitalsync/presentation/screens/health/bloodwork_screen.dart';
import 'package:vitalsync/presentation/screens/health/lifestyle_screen.dart';
import 'package:vitalsync/presentation/screens/files/upload_screen.dart';
import 'package:vitalsync/presentation/screens/billing/subscription_screen.dart';
import 'package:vitalsync/presentation/screens/settings/settings_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/dashboard',
    redirect: (context, state) {
      // While checking auth, show nothing (loading handled by splash)
      if (authState.isLoading) return null;

      final isLoggedIn = authState.valueOrNull != null;
      final isAuthRoute = state.matchedLocation.startsWith('/auth');

      if (!isLoggedIn && !isAuthRoute) return '/auth/login';
      if (isLoggedIn && isAuthRoute) return '/dashboard';
      return null;
    },
    routes: [
      GoRoute(path: '/auth/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/auth/register', builder: (_, __) => const RegisterScreen()),
      GoRoute(path: '/dashboard', builder: (_, __) => const DashboardScreen()),
      GoRoute(path: '/health/bloodwork', builder: (_, __) => const BloodworkScreen()),
      GoRoute(path: '/health/lifestyle', builder: (_, __) => const LifestyleScreen()),
      GoRoute(path: '/files/upload', builder: (_, __) => const UploadScreen()),
      GoRoute(path: '/billing', builder: (_, __) => const SubscriptionScreen()),
      GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(child: Text('Page not found: ${state.uri}')),
    ),
  );
});
