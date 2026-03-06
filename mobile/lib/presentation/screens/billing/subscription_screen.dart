import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:vitalsync/data/models/subscription.dart';
import 'package:vitalsync/presentation/providers/billing_provider.dart';

class SubscriptionScreen extends ConsumerWidget {
  const SubscriptionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statusAsync = ref.watch(subscriptionStatusProvider);
    final checkoutState = ref.watch(checkoutProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Subscription')),
      body: statusAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (status) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Current status banner
            _CurrentTierBanner(status: status),
            const SizedBox(height: 24),

            Text('Choose a Plan',
                style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),

            ...TierInfo.tiers.map((tier) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: _TierCard(
                    tier: tier,
                    isCurrent: tier.id == status.tier,
                    isLoading: checkoutState.isLoading,
                    onUpgrade: tier.id == 'free'
                        ? null
                        : () async {
                            final url = await ref
                                .read(checkoutProvider.notifier)
                                .createCheckout(tier.id);
                            if (url != null && context.mounted) {
                              final uri = Uri.parse(url);
                              if (await canLaunchUrl(uri)) {
                                await launchUrl(uri,
                                    mode: LaunchMode.externalApplication);
                              } else {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                      content: Text(
                                          'Could not open Stripe checkout')),
                                );
                              }
                            }
                          },
                  ),
                )),

            if (checkoutState.hasError)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  checkoutState.error.toString(),
                  style: const TextStyle(color: Colors.red),
                ),
              ),

            const SizedBox(height: 16),
            Text(
              'Subscriptions are managed via Stripe. Cancel anytime from your Stripe customer portal.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}

class _CurrentTierBanner extends StatelessWidget {
  final SubscriptionStatus status;
  const _CurrentTierBanner({required this.status});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Icons.verified,
              color: Theme.of(context).colorScheme.primary, size: 28),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Current Plan',
                  style: Theme.of(context).textTheme.bodySmall),
              Text(
                status.displayName,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).colorScheme.primary,
                    ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _TierCard extends StatelessWidget {
  final TierInfo tier;
  final bool isCurrent;
  final bool isLoading;
  final VoidCallback? onUpgrade;

  const _TierCard({
    required this.tier,
    required this.isCurrent,
    required this.isLoading,
    this.onUpgrade,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: isCurrent
          ? Theme.of(context).colorScheme.secondaryContainer
          : null,
      shape: isCurrent
          ? RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(
                  color: Theme.of(context).colorScheme.primary, width: 2),
            )
          : null,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(tier.name,
                    style: Theme.of(context)
                        .textTheme
                        .titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold)),
                Text(tier.price,
                    style: Theme.of(context)
                        .textTheme
                        .titleMedium
                        ?.copyWith(
                            color: Theme.of(context).colorScheme.primary,
                            fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 8),
            ...tier.features.map(
              (f) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  children: [
                    const Icon(Icons.check, size: 16, color: Colors.green),
                    const SizedBox(width: 6),
                    Expanded(child: Text(f, style: const TextStyle(fontSize: 13))),
                  ],
                ),
              ),
            ),
            if (!isCurrent && onUpgrade != null) ...[
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: isLoading ? null : onUpgrade,
                  child: isLoading
                      ? const SizedBox(
                          height: 18,
                          width: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Text('Upgrade to ${tier.name}'),
                ),
              ),
            ],
            if (isCurrent)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Chip(
                  label: const Text('Current Plan'),
                  backgroundColor:
                      Theme.of(context).colorScheme.primary.withOpacity(0.1),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
