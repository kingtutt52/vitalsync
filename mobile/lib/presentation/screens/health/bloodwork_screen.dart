import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:vitalsync/presentation/providers/health_provider.dart';

class BloodworkScreen extends ConsumerStatefulWidget {
  const BloodworkScreen({super.key});

  @override
  ConsumerState<BloodworkScreen> createState() => _BloodworkScreenState();
}

class _BloodworkScreenState extends ConsumerState<BloodworkScreen> {
  final _formKey = GlobalKey<FormState>();
  DateTime _testDate = DateTime.now();

  final _vitaminDCtrl = TextEditingController();
  final _ldlCtrl = TextEditingController();
  final _hdlCtrl = TextEditingController();
  final _triglyceridesCtrl = TextEditingController();
  final _a1cCtrl = TextEditingController();
  final _fastingGlucoseCtrl = TextEditingController();
  final _crpCtrl = TextEditingController();
  final _testosteroneCtrl = TextEditingController();

  @override
  void dispose() {
    for (final c in [
      _vitaminDCtrl, _ldlCtrl, _hdlCtrl, _triglyceridesCtrl,
      _a1cCtrl, _fastingGlucoseCtrl, _crpCtrl, _testosteroneCtrl
    ]) {
      c.dispose();
    }
    super.dispose();
  }

  double? _parse(TextEditingController c) =>
      c.text.trim().isEmpty ? null : double.tryParse(c.text.trim());

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _testDate,
      firstDate: DateTime(2000),
      lastDate: DateTime.now(),
    );
    if (picked != null) setState(() => _testDate = picked);
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final data = {
      'test_date': DateFormat('yyyy-MM-dd').format(_testDate),
      'vitamin_d': _parse(_vitaminDCtrl),
      'ldl': _parse(_ldlCtrl),
      'hdl': _parse(_hdlCtrl),
      'triglycerides': _parse(_triglyceridesCtrl),
      'a1c': _parse(_a1cCtrl),
      'fasting_glucose': _parse(_fastingGlucoseCtrl),
      'crp': _parse(_crpCtrl),
      'testosterone_total': _parse(_testosteroneCtrl),
    }..removeWhere((_, v) => v == null);

    await ref.read(bloodworkFormProvider.notifier).submit(data);
  }

  @override
  Widget build(BuildContext context) {
    final formState = ref.watch(bloodworkFormProvider);

    ref.listen(bloodworkFormProvider, (_, next) {
      if (!next.isLoading && !next.hasError && next.valueOrNull == null) return;
      if (next.hasError) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next.error.toString()), backgroundColor: Colors.red),
        );
      } else if (!next.isLoading) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Bloodwork saved ✓'), backgroundColor: Colors.green),
        );
        ref.invalidate(healthSummaryProvider);
        context.go('/dashboard');
      }
    });

    return Scaffold(
      appBar: AppBar(title: const Text('Log Bloodwork')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Date picker
            ListTile(
              leading: const Icon(Icons.calendar_today),
              title: const Text('Test Date'),
              subtitle: Text(DateFormat.yMMMd().format(_testDate)),
              onTap: _pickDate,
              shape: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            const SizedBox(height: 16),

            _BiomarkerField(
                controller: _vitaminDCtrl, label: 'Vitamin D', unit: 'ng/mL'),
            _BiomarkerField(
                controller: _ldlCtrl, label: 'LDL Cholesterol', unit: 'mg/dL'),
            _BiomarkerField(
                controller: _hdlCtrl, label: 'HDL Cholesterol', unit: 'mg/dL'),
            _BiomarkerField(
                controller: _triglyceridesCtrl, label: 'Triglycerides', unit: 'mg/dL'),
            _BiomarkerField(controller: _a1cCtrl, label: 'HbA1c', unit: '%'),
            _BiomarkerField(
                controller: _fastingGlucoseCtrl, label: 'Fasting Glucose', unit: 'mg/dL'),
            _BiomarkerField(
                controller: _crpCtrl, label: 'hsCRP', unit: 'mg/L'),
            _BiomarkerField(
                controller: _testosteroneCtrl, label: 'Total Testosterone', unit: 'ng/dL'),

            const SizedBox(height: 8),
            Text(
              'Leave any field blank if not tested.',
              style: Theme.of(context)
                  .textTheme
                  .bodySmall
                  ?.copyWith(color: Theme.of(context).colorScheme.outline),
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
                  : const Text('Save Bloodwork'),
            ),
          ],
        ),
      ),
    );
  }
}

class _BiomarkerField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String unit;

  const _BiomarkerField({
    required this.controller,
    required this.label,
    required this.unit,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextFormField(
        controller: controller,
        decoration: InputDecoration(
          labelText: label,
          suffixText: unit,
        ),
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        validator: (v) {
          if (v == null || v.trim().isEmpty) return null; // optional
          if (double.tryParse(v.trim()) == null) return 'Enter a valid number';
          if (double.parse(v.trim()) < 0) return 'Must be positive';
          return null;
        },
      ),
    );
  }
}
