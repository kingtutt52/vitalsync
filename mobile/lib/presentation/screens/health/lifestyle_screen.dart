import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:vitalsync/presentation/providers/health_provider.dart';

class LifestyleScreen extends ConsumerStatefulWidget {
  const LifestyleScreen({super.key});

  @override
  ConsumerState<LifestyleScreen> createState() => _LifestyleScreenState();
}

class _LifestyleScreenState extends ConsumerState<LifestyleScreen> {
  final _formKey = GlobalKey<FormState>();
  DateTime _entryDate = DateTime.now();

  final _sleepCtrl = TextEditingController();
  final _stepsCtrl = TextEditingController();
  final _restingHrCtrl = TextEditingController();
  final _hrvCtrl = TextEditingController();
  final _workoutCtrl = TextEditingController();
  final _dietCtrl = TextEditingController();
  int _stress = 5;

  @override
  void dispose() {
    for (final c in [
      _sleepCtrl, _stepsCtrl, _restingHrCtrl, _hrvCtrl, _workoutCtrl, _dietCtrl
    ]) {
      c.dispose();
    }
    super.dispose();
  }

  double? _parseDouble(TextEditingController c) =>
      c.text.trim().isEmpty ? null : double.tryParse(c.text.trim());

  int? _parseInt(TextEditingController c) =>
      c.text.trim().isEmpty ? null : int.tryParse(c.text.trim());

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _entryDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (picked != null) setState(() => _entryDate = picked);
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final data = {
      'entry_date': DateFormat('yyyy-MM-dd').format(_entryDate),
      'sleep_hours': _parseDouble(_sleepCtrl),
      'steps': _parseInt(_stepsCtrl),
      'resting_hr': _parseInt(_restingHrCtrl),
      'hrv': _parseDouble(_hrvCtrl),
      'workout_minutes': _parseInt(_workoutCtrl),
      'stress_1_10': _stress,
      'diet_notes': _dietCtrl.text.trim().isEmpty ? null : _dietCtrl.text.trim(),
    }..removeWhere((_, v) => v == null);

    await ref.read(lifestyleFormProvider.notifier).submit(data);
  }

  @override
  Widget build(BuildContext context) {
    final formState = ref.watch(lifestyleFormProvider);

    ref.listen(lifestyleFormProvider, (_, next) {
      if (next.hasError) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next.error.toString()), backgroundColor: Colors.red),
        );
      } else if (!next.isLoading) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Lifestyle logged ✓'), backgroundColor: Colors.green),
        );
        ref.invalidate(healthSummaryProvider);
        context.go('/dashboard');
      }
    });

    return Scaffold(
      appBar: AppBar(title: const Text('Log Lifestyle')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            ListTile(
              leading: const Icon(Icons.calendar_today),
              title: const Text('Entry Date'),
              subtitle: Text(DateFormat.yMMMd().format(_entryDate)),
              onTap: _pickDate,
              shape: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            const SizedBox(height: 16),

            _NumericField(ctrl: _sleepCtrl, label: 'Sleep Hours', unit: 'hrs', decimal: true),
            _NumericField(ctrl: _stepsCtrl, label: 'Steps', unit: 'steps'),
            _NumericField(ctrl: _restingHrCtrl, label: 'Resting Heart Rate', unit: 'bpm'),
            _NumericField(ctrl: _hrvCtrl, label: 'HRV', unit: 'ms', decimal: true),
            _NumericField(ctrl: _workoutCtrl, label: 'Workout Minutes', unit: 'min'),

            // Stress slider
            const SizedBox(height: 8),
            Text('Stress Level: $_stress/10',
                style: Theme.of(context).textTheme.bodyMedium),
            Slider(
              value: _stress.toDouble(),
              min: 1,
              max: 10,
              divisions: 9,
              label: '$_stress',
              onChanged: (v) => setState(() => _stress = v.round()),
            ),
            const SizedBox(height: 8),

            TextFormField(
              controller: _dietCtrl,
              decoration: const InputDecoration(
                labelText: 'Diet Notes (optional)',
                hintText: 'What did you eat today?',
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 24),

            ElevatedButton(
              onPressed: formState.isLoading ? null : _submit,
              child: formState.isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Save Lifestyle Entry'),
            ),
          ],
        ),
      ),
    );
  }
}

class _NumericField extends StatelessWidget {
  final TextEditingController ctrl;
  final String label;
  final String unit;
  final bool decimal;

  const _NumericField({
    required this.ctrl,
    required this.label,
    required this.unit,
    this.decimal = false,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextFormField(
        controller: ctrl,
        decoration: InputDecoration(labelText: label, suffixText: unit),
        keyboardType: TextInputType.numberWithOptions(decimal: decimal),
        validator: (v) {
          if (v == null || v.trim().isEmpty) return null;
          final parsed = decimal
              ? double.tryParse(v.trim())
              : int.tryParse(v.trim())?.toDouble();
          if (parsed == null) return 'Enter a valid number';
          if (parsed < 0) return 'Must be positive';
          return null;
        },
      ),
    );
  }
}
