import 'package:dio/dio.dart';
import 'package:vitalsync/data/api/api_client.dart';

class FilesApi {
  final _client = ApiClient.instance;

  Future<Map<String, dynamic>> uploadBloodwork(String filePath, String filename) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath, filename: filename),
      });
      final res = await _client.dio.post(
        '/files/bloodwork-upload',
        data: formData,
        options: Options(contentType: 'multipart/form-data'),
      );
      return res.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }

  Future<Map<String, dynamic>> uploadGenetics(String filePath, String filename) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath, filename: filename),
      });
      final res = await _client.dio.post(
        '/files/genetics-upload',
        data: formData,
        options: Options(contentType: 'multipart/form-data'),
      );
      return res.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }

  Future<List<Map<String, dynamic>>> listFiles() async {
    try {
      final res = await _client.dio.get('/files/');
      return List<Map<String, dynamic>>.from(res.data as List);
    } on DioException catch (e) {
      throw parseDioError(e);
    }
  }
}
