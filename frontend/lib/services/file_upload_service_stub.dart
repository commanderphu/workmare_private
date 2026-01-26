import 'dart:typed_data';

/// Result of a file upload operation
class FileUploadResult {
  final Uint8List bytes;
  final String filename;

  FileUploadResult({
    required this.bytes,
    required this.filename,
  });
}

/// Abstract interface for file upload operations
abstract class FileUploadService {
  /// Pick a file from the camera
  Future<FileUploadResult?> pickFromCamera();

  /// Pick a file from the gallery/file system
  Future<FileUploadResult?> pickFromGallery();

  /// Pick any file (PDF, images)
  Future<FileUploadResult?> pickFile();

  factory FileUploadService() {
    throw UnsupportedError(
      'Cannot create FileUploadService without dart:html or dart:io',
    );
  }
}
