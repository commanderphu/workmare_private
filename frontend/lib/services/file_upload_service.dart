/// Platform-agnostic file upload service interface
///
/// This file exports the correct implementation based on the platform.
/// - On web: uses dart:html for file selection
/// - On mobile: uses image_picker and file_picker packages

import 'file_upload_service_stub.dart'
    if (dart.library.html) 'file_upload_service_web.dart'
    if (dart.library.io) 'file_upload_service_mobile.dart';

export 'file_upload_service_stub.dart'
    if (dart.library.html) 'file_upload_service_web.dart'
    if (dart.library.io) 'file_upload_service_mobile.dart';
