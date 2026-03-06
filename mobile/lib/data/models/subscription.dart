class SubscriptionStatus {
  final String tier;
  final bool isActive;
  final String? stripeCustomerId;
  final String? stripeSubscriptionId;
  final DateTime? currentPeriodEnd;

  const SubscriptionStatus({
    required this.tier,
    required this.isActive,
    this.stripeCustomerId,
    this.stripeSubscriptionId,
    this.currentPeriodEnd,
  });

  factory SubscriptionStatus.fromJson(Map<String, dynamic> j) =>
      SubscriptionStatus(
        tier: j['tier'] as String,
        isActive: j['is_active'] as bool,
        stripeCustomerId: j['stripe_customer_id'] as String?,
        stripeSubscriptionId: j['stripe_subscription_id'] as String?,
        currentPeriodEnd: j['current_period_end'] != null
            ? DateTime.parse(j['current_period_end'] as String)
            : null,
      );

  bool get isPaid => tier != 'free';

  String get displayName {
    switch (tier) {
      case 'premium_lite':
        return 'Premium Lite';
      case 'vital_plus':
        return 'Vital+';
      case 'vital_pro':
        return 'VitalPro';
      default:
        return 'Free';
    }
  }
}

class TierInfo {
  final String id;
  final String name;
  final String price;
  final List<String> features;

  const TierInfo({
    required this.id,
    required this.name,
    required this.price,
    required this.features,
  });

  static const tiers = [
    TierInfo(
      id: 'free',
      name: 'Free',
      price: '\$0/mo',
      features: [
        'Manual health data entry',
        'Basic health summary',
        'Bloodwork & lifestyle logs',
      ],
    ),
    TierInfo(
      id: 'premium_lite',
      name: 'Premium Lite',
      price: '\$9.99/mo',
      features: [
        'Everything in Free',
        'AI Health Score & Action Plan',
        'Bloodwork file upload',
        'Priority support',
      ],
    ),
    TierInfo(
      id: 'vital_plus',
      name: 'Vital+',
      price: '\$29.99/mo',
      features: [
        'Everything in Premium Lite',
        'Wearables integration (coming soon)',
        'Downloadable health reports (coming soon)',
        'Advanced trend analysis',
      ],
    ),
    TierInfo(
      id: 'vital_pro',
      name: 'VitalPro',
      price: '\$79.99/mo',
      features: [
        'Everything in Vital+',
        'Genetics file upload & SNP analysis',
        'Comprehensive genetic insights',
        'Concierge support',
      ],
    ),
  ];
}
