import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:vitalsync/data/api/files_api.dart';

final _filesApiProvider = Provider<FilesApi>((ref) => FilesApi());

class UploadScreen extends ConsumerStatefulWidget {
  const UploadScreen({super.key});

  @override
  ConsumerState<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends ConsumerState<UploadScreen> {
  bool _uploading = false;
  String? _statusMessage;
  bool _isError = false;

  Future<void> _pickAndUpload(String type) async {
    final result = await FilePicker.platform.pickFiles(
      type: type == 'genetics' ? FileType.custom : FileType.any,
      allowedExtensions: type == 'genetics' ? ['txt'] : null,
      allowMultiple: false,
    );

    if (result == null || result.files.single.path == null) return;

    final file = result.files.single;
    setState(() {
      _uploading = true;
      _statusMessage = null;
      _isError = false;
    });

    try {
      final api = ref.read(_filesApiProvider);
      Map<String, dynamic> response;

      if (type == 'bloodwork') {
        response = await api.uploadBloodwork(file.path!, file.name);
      } else {
        response = await api.uploadGenetics(file.path!, file.name);
      }

      String message = 'File uploaded successfully.';
      if (type == 'genetics') {
        final parsed = response['parsed_summary'];
        if (parsed != null) {
          message += '\nGenetics parsed. Check your dashboard for insights.';
        }
      }

      setState(() {
        _statusMessage = message;
        _isError = false;
      });
    } catch (e) {
      setState(() {
        _statusMessage = e.toString();
        _isError = true;
      });
    } finally {
      setState(() => _uploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Upload Files')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Upload your health files for analysis and record keeping.',
          ),
          const SizedBox(height: 24),

          // Bloodwork upload
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.bloodtype_outlined,
                          color: Theme.of(context).colorScheme.primary),
                      const SizedBox(width: 8),
                      Text('Bloodwork Results',
                          style: Theme.of(context).textTheme.titleMedium),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text('Upload a PDF or image of your lab results.'),
                  const Text(
                    'Requires: Premium Lite or higher',
                    style: TextStyle(fontSize: 12, color: Colors.orange),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    icon: const Icon(Icons.upload),
                    label: const Text('Select Bloodwork File'),
                    onPressed:
                        _uploading ? null : () => _pickAndUpload('bloodwork'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Genetics upload
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.science_outlined,
                          color: Theme.of(context).colorScheme.secondary),
                      const SizedBox(width: 8),
                      Text('23andMe Raw Data',
                          style: Theme.of(context).textTheme.titleMedium),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                      'Upload your 23andMe raw data file (.txt) for SNP variant analysis.'),
                  const Text(
                    'Requires: VitalPro tier',
                    style: TextStyle(fontSize: 12, color: Colors.deepOrange),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    icon: const Icon(Icons.upload),
                    label: const Text('Select Genetics File (.txt)'),
                    onPressed:
                        _uploading ? null : () => _pickAndUpload('genetics'),
                  ),
                ],
              ),
            ),
          ),

          if (_uploading) ...[
            const SizedBox(height: 24),
            const Center(child: CircularProgressIndicator()),
            const SizedBox(height: 8),
            const Center(child: Text('Uploading...')),
          ],

          if (_statusMessage != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _isError
                    ? Colors.red.withOpacity(0.1)
                    : Colors.green.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: _isError ? Colors.red : Colors.green,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    _isError ? Icons.error_outline : Icons.check_circle_outline,
                    color: _isError ? Colors.red : Colors.green,
                  ),
                  const SizedBox(width: 8),
                  Expanded(child: Text(_statusMessage!)),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
