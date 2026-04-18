import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'api_service.dart';

// Top-level handler required by Firebase for background messages
@pragma('vm:entry-point')
Future<void> _firebaseBackgroundHandler(RemoteMessage message) async {
  // Background message received – no UI action needed here
}

class PushNotificationService {
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final ApiService _api = ApiService();

  Future<void> initialize() async {
    // Register background handler
    FirebaseMessaging.onBackgroundMessage(_firebaseBackgroundHandler);

    // Request permission (iOS + Web)
    final settings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    if (settings.authorizationStatus == AuthorizationStatus.denied) {
      debugPrint('Push-Benachrichtigungen verweigert');
      return;
    }

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // Handle notification tap when app is in background
    FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);

    // Register token with backend
    await registerToken();

    // Refresh token when it rotates
    _messaging.onTokenRefresh.listen((newToken) {
      _registerTokenWithBackend(newToken);
    });
  }

  Future<void> registerToken() async {
    try {
      final token = await _messaging.getToken();
      if (token != null) {
        await _registerTokenWithBackend(token);
      }
    } catch (e) {
      debugPrint('FCM Token-Registrierung fehlgeschlagen: $e');
    }
  }

  Future<void> unregisterToken() async {
    try {
      await _api.delete('/notifications/fcm-token');
      await _messaging.deleteToken();
    } catch (e) {
      debugPrint('FCM Token-Deregistrierung fehlgeschlagen: $e');
    }
  }

  Future<void> _registerTokenWithBackend(String token) async {
    try {
      await _api.post('/notifications/fcm-token', data: {'token': token});
      debugPrint('FCM Token registriert');
    } catch (e) {
      debugPrint('FCM Token Backend-Registrierung fehlgeschlagen: $e');
    }
  }

  void _handleForegroundMessage(RemoteMessage message) {
    debugPrint('Foreground-Nachricht: ${message.notification?.title}');
    // TODO: In-App Snackbar/Banner anzeigen
  }

  void _handleNotificationTap(RemoteMessage message) {
    debugPrint('Notification getappt: ${message.data}');
    // TODO: Zu relevantem Task/Dokument navigieren
  }
}
