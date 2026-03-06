import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:vitalsync/presentation/providers/auth_provider.dart';
import 'package:vitalsync/presentation/providers/billing_provider.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authStateProvider).valueOrNull;
    final statusAsync = ref.watch(subscriptionStatusProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        children: [
          // Profile section
          if (user != null)
            ListTile(
              leading: CircleAvatar(
                child: Text(user.name.isNotEmpty ? user.name[0].toUpperCase() : 'V'),
              ),
              title: Text(user.name),
              subtitle: Text(user.email),
            ),
          const Divider(),

          // Subscription
          ListTile(
            leading: const Icon(Icons.credit_card_outlined),
            title: const Text('Subscription'),
            subtitle: statusAsync.whenOrNull(
              data: (s) => Text(s.displayName),
            ),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.go('/billing'),
          ),

          const Divider(),

          // Data section
          ListTile(
            leading: const Icon(Icons.bloodtype_outlined),
            title: const Text('Log Bloodwork'),
            onTap: () => context.go('/health/bloodwork'),
          ),
          ListTile(
            leading: const Icon(Icons.directions_run),
            title: const Text('Log Lifestyle'),
            onTap: () => context.go('/health/lifestyle'),
          ),
          ListTile(
            leading: const Icon(Icons.upload_file),
            title: const Text('Upload Files'),
            onTap: () => context.go('/files/upload'),
          ),

          const Divider(),

          ListTile(
            leading: const Icon(Icons.logout, color: Colors.red),
            title: const Text('Sign Out', style: TextStyle(color: Colors.red)),
            onTap: () async {
              await ref.read(authStateProvider.notifier).logout();
              if (context.mounted) context.go('/auth/login');
            },
          ),

          const SizedBox(height: 24),
          Center(
            child: Text(
              'VitalSync v1.0.0\nNot medical advice.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}
