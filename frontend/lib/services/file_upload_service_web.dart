import 'dart:async';
import 'dart:html' as html;
import 'dart:typed_data';

import 'file_upload_service_stub.dart';

/// Web implementation of FileUploadService using dart:html
class FileUploadService {
  /// Pick a file from the camera (on mobile browsers, opens camera directly)
  Future<FileUploadResult?> pickFromCamera() async {
    return _pickFile(useCamera: true);
  }

  /// Pick a file from the gallery/file system
  Future<FileUploadResult?> pickFromGallery() async {
    return _pickFile(useCamera: false);
  }

  /// Pick any file (PDF, images)
  Future<FileUploadResult?> pickFile() async {
    return _pickFile(
      useCamera: false,
      accept: 'image/*,.pdf',
    );
  }

  Future<FileUploadResult?> _pickFile({
    bool useCamera = false,
    String accept = 'image/*,.pdf',
  }) async {
    final completer = Completer<FileUploadResult?>();

    // Create HTML file input element
    final html.FileUploadInputElement uploadInput = html.FileUploadInputElement();
    uploadInput.accept = accept;

    // On mobile browsers, this will open the camera directly
    if (useCamera) {
      uploadInput.setAttribute('capture', 'environment');
    }

    uploadInput.click();

    uploadInput.onChange.listen((e) async {
      final files = uploadInput.files;
      if (files == null || files.isEmpty) {
        completer.complete(null);
        return;
      }

      final file = files[0];
      final reader = html.FileReader();

      reader.readAsArrayBuffer(file);
      reader.onLoadEnd.listen((e) async {
        final bytes = reader.result as Uint8List;

        completer.complete(FileUploadResult(
          bytes: bytes,
          filename: file.name,
        ));
      });

      reader.onError.listen((e) {
        completer.complete(null);
      });
    });

    // Handle cancel (when user closes picker without selecting)
    uploadInput.onCancel.listen((e) {
      completer.complete(null);
    });

    return completer.future;
  }
}
