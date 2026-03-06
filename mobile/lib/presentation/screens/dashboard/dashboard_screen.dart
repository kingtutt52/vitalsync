import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:vitalsync/data/models/ai_plan.dart';
import 'package:vitalsync/presentation/providers/auth_provider.dart';
import 'package:vitalsync/presentation/providers/ai_provider.dart';
import 'package:vitalsync/presentation/providers/health_provider.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authStateProvider).valueOrNull;
    final planState = ref.watch(healthPlanProvider);
    final summaryAsync = ref.watch(healthSummaryProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('VitalSync'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => context.go('/settings'),
          ),
        ],
      ),
      drawer: _AppDrawer(),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(healthSummaryProvider);
          ref.invalidate(healthPlanProvider);
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Greeting
            Text(
              'Hello, ${user?.name.split(' ').first ?? 'there'} 👋',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              'Here\'s your health snapshot.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.outline,
                  ),
            ),
            const SizedBox(height: 20),

            // Health Score Card
            _HealthScoreCard(planState: planState),
            const SizedBox(height: 16),

            // Generate Plan button
            ElevatedButton.icon(
              icon: const Icon(Icons.auto_awesome),
              label: const Text('Generate / Refresh Health Plan'),
              onPressed: planState.isLoading
                  ? null
                  : () => ref.read(healthPlanProvider.notifier).generate(),
            ),
            const SizedBox(height: 20),

            // Summary stats
            summaryAsync.when(
              data: (summary) => _SummarySection(summary: summary),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Text('Could not load summary: $e'),
            ),

            // Action items from plan
            if (planState.valueOrNull != null) ...[
              const SizedBox(height: 20),
              _ActionList(plan: planState.valueOrNull!),
            ],

            const SizedBox(height: 20),

            // Quick Actions
            _QuickActions(),
          ],
        ),
      ),
    );
  }
}

class _HealthScoreCard extends StatelessWidget {
  final AsyncValue<HealthPlan?> planState;
  const _HealthScoreCard({required this.planState});

  @override
  Widget build(BuildContext context) {
    final score = planState.valueOrNull?.healthScore;
    final color = score == null
        ? Theme.of(context).colorScheme.outline
        : score >= 80
            ? Colors.green
            : score >= 60
                ? Colors.orange
                : Colors.red;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Row(
          children: [
            CircleAvatar(
              radius: 36,
              backgroundColor: color.withOpacity(0.15),
              child: Text(
                score != null ? score.toStringAsFixed(0) : '--',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Health Score',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 4),
                  Text(
                    score == null
                        ? 'Generate your plan to see your score'
                        : score >= 80
                            ? 'Looking good — keep it up!'
                            : score >= 60
                                ? 'Room to improve — check your action plan'
                                : 'Needs attention — prioritise your actions',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  if (planState.isLoading) ...[
                    const SizedBox(height: 8),
                    const LinearProgressIndicator(),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SummarySection extends StatelessWidget {
  final dynamic summary;
  const _SummarySection({required this.summary});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Data Overview', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _StatChip(
                icon: Icons.bloodtype_outlined,
                label: 'Bloodwork entries',
                value: '${summary.bloodworkCount}',
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _StatChip(
                icon: Icons.directions_run,
                label: 'Lifestyle entries',
                value: '${summary.lifestyleCount}',
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _StatChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  const _StatChip({required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Icon(icon, color: Theme.of(context).colorScheme.primary),
            const SizedBox(height: 4),
            Text(value,
                style: Theme.of(context)
                    .textTheme
                    .headlineSmall
                    ?.copyWith(fontWeight: FontWeight.bold)),
            Text(label,
                style: Theme.of(context).textTheme.bodySmall,
                textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}

class _ActionList extends StatelessWidget {
  final HealthPlan plan;
  const _ActionList({required this.plan});

  @override
  Widget build(BuildContext context) {
    if (plan.actions.isEmpty) return const SizedBox.shrink();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Your Action Plan', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        ...plan.actions.map(
          (action) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.check_circle_outline,
                    color: Colors.green, size: 20),
                const SizedBox(width: 8),
                Expanded(child: Text(action)),
              ],
            ),
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surfaceVariant,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            plan.disclaimer,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
      ],
    );
  }
}

class _QuickActions extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Log Data', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            _QuickActionChip(
              icon: Icons.bloodtype_outlined,
              label: 'Bloodwork',
              onTap: () => context.go('/health/bloodwork'),
            ),
            _QuickActionChip(
              icon: Icons.directions_run,
              label: 'Lifestyle',
              onTap: () => context.go('/health/lifestyle'),
            ),
            _QuickActionChip(
              icon: Icons.upload_file,
              label: 'Upload File',
              onTap: () => context.go('/files/upload'),
            ),
          ],
        ),
      ],
    );
  }
}

class _QuickActionChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  const _QuickActionChip(
      {required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ActionChip(
      avatar: Icon(icon, size: 18),
      label: Text(label),
      onPressed: onTap,
    );
  }
}

class _AppDrawer extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authStateProvider).valueOrNull;
    return Drawer(
      child: ListView(
        children: [
          UserAccountsDrawerHeader(
            accountName: Text(user?.name ?? ''),
            accountEmail: Text(user?.email ?? ''),
            currentAccountPicture: CircleAvatar(
              child: Text(
                (user?.name.isNotEmpty ?? false)
                    ? user!.name[0].toUpperCase()
                    : 'V',
                style: const TextStyle(fontSize: 24),
              ),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.dashboard_outlined),
            title: const Text('Dashboard'),
            onTap: () {
              context.pop();
              context.go('/dashboard');
            },
          ),
          ListTile(
            leading: const Icon(Icons.bloodtype_outlined),
            title: const Text('Log Bloodwork'),
            onTap: () {
              context.pop();
              context.go('/health/bloodwork');
            },
          ),
          ListTile(
            leading: const Icon(Icons.directions_run),
            title: const Text('Log Lifestyle'),
            onTap: () {
              context.pop();
              context.go('/health/lifestyle');
            },
          ),
          ListTile(
            leading: const Icon(Icons.upload_file),
            title: const Text('Upload Files'),
            onTap: () {
              context.pop();
              context.go('/files/upload');
            },
          ),
          ListTile(
            leading: const Icon(Icons.credit_card_outlined),
            title: const Text('Subscription'),
            onTap: () {
              context.pop();
              context.go('/billing');
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.settings_outlined),
            title: const Text('Settings'),
            onTap: () {
              context.pop();
              context.go('/settings');
            },
          ),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('Sign Out'),
            onTap: () async {
              await ref.read(authStateProvider.notifier).logout();
              if (context.mounted) context.go('/auth/login');
            },
          ),
        ],
      ),
    );
  }
}
