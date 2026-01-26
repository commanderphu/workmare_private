import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../models/document.dart';
import '../providers/document_provider.dart';
import '../services/file_upload_service.dart';
import 'document_detail_page.dart';

class DocumentsPage extends StatefulWidget {
  const DocumentsPage({super.key});

  @override
  State<DocumentsPage> createState() => _DocumentsPageState();
}

class _DocumentsPageState extends State<DocumentsPage> {
  final FileUploadService _fileUploadService = FileUploadService();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<DocumentProvider>().loadDocuments();
    });
  }

  Future<void> _uploadFromCamera() async {
    try {
      final result = await _fileUploadService.pickFromCamera();
      if (result == null) return;

      await _processAndUpload(result.bytes, result.filename);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Fehler beim Öffnen der Kamera: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _uploadFromGallery() async {
    try {
      final result = await _fileUploadService.pickFromGallery();
      if (result == null) return;

      await _processAndUpload(result.bytes, result.filename);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Fehler beim Auswählen des Bildes: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _uploadFromFiles() async {
    try {
      final result = await _fileUploadService.pickFile();
      if (result == null) return;

      await _processAndUpload(result.bytes, result.filename);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Fehler beim Auswählen der Datei: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _processAndUpload(Uint8List bytes, String fileName) async {
    // Show type selection dialog
    if (!mounted) return;
    final type = await _showTypeSelectionDialog();
    if (type == null) return;

    // Upload
    if (!mounted) return;
    final success = await context.read<DocumentProvider>().uploadDocument(
          fileBytes: bytes,
          filename: fileName,
          type: type,
          title: fileName,
        );

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Dokument erfolgreich hochgeladen'),
          backgroundColor: Colors.green,
        ),
      );
    } else {
      final error = context.read<DocumentProvider>().error;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(error ?? 'Fehler beim Hochladen'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _showUploadOptions() {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Text(
                  'Dokument hinzufügen',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              const Divider(),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.blue.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.camera_alt, color: Colors.blue),
                ),
                title: const Text('Mit Kamera aufnehmen'),
                subtitle: const Text('Foto direkt aufnehmen'),
                onTap: () {
                  Navigator.pop(context);
                  _uploadFromCamera();
                },
              ),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.green.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.photo_library, color: Colors.green),
                ),
                title: const Text('Aus Galerie wählen'),
                subtitle: const Text('Vorhandenes Foto auswählen'),
                onTap: () {
                  Navigator.pop(context);
                  _uploadFromGallery();
                },
              ),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.orange.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.folder, color: Colors.orange),
                ),
                title: const Text('Datei auswählen'),
                subtitle: const Text('PDF oder Bild hochladen'),
                onTap: () {
                  Navigator.pop(context);
                  _uploadFromFiles();
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<String?> _showTypeSelectionDialog() async {
    return showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Dokumenttyp auswählen'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _TypeOption(
                icon: Icons.receipt_long,
                iconColor: Colors.blue,
                title: 'Rechnung',
                onTap: () => Navigator.pop(context, 'invoice'),
              ),
              _TypeOption(
                icon: Icons.warning,
                iconColor: Colors.red,
                title: 'Mahnung',
                onTap: () => Navigator.pop(context, 'reminder'),
              ),
              _TypeOption(
                icon: Icons.description,
                iconColor: Colors.purple,
                title: 'Vertrag',
                onTap: () => Navigator.pop(context, 'contract'),
              ),
              _TypeOption(
                icon: Icons.receipt,
                iconColor: Colors.green,
                title: 'Quittung',
                onTap: () => Navigator.pop(context, 'receipt'),
              ),
              _TypeOption(
                icon: Icons.folder,
                iconColor: Colors.grey,
                title: 'Sonstiges',
                onTap: () => Navigator.pop(context, 'other'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final documentProvider = context.watch<DocumentProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dokumente'),
        actions: [
          if (documentProvider.documents.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () => documentProvider.loadDocuments(),
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => documentProvider.loadDocuments(),
        child: documentProvider.isLoading && documentProvider.documents.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : documentProvider.error != null && documentProvider.documents.isEmpty
                ? Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.error_outline, size: 64, color: Colors.red),
                          const SizedBox(height: 16),
                          Text(
                            documentProvider.error!,
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontSize: 16),
                          ),
                          const SizedBox(height: 16),
                          FilledButton.icon(
                            onPressed: () => documentProvider.loadDocuments(),
                            icon: const Icon(Icons.refresh),
                            label: const Text('Erneut versuchen'),
                          ),
                        ],
                      ),
                    ),
                  )
                : documentProvider.documents.isEmpty
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(24),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.cloud_upload_outlined,
                                size: 100,
                                color: Colors.grey.shade300,
                              ),
                              const SizedBox(height: 24),
                              Text(
                                'Noch keine Dokumente',
                                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                              const SizedBox(height: 12),
                              Text(
                                'Lade dein erstes Dokument hoch.\nDie KI analysiert es automatisch!',
                                textAlign: TextAlign.center,
                                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                      color: Colors.grey,
                                    ),
                              ),
                              const SizedBox(height: 32),
                              FilledButton.icon(
                                onPressed: _showUploadOptions,
                                icon: const Icon(Icons.add),
                                label: const Text('Jetzt hochladen'),
                              ),
                            ],
                          ),
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: documentProvider.documents.length,
                        itemBuilder: (context, index) {
                          final document = documentProvider.documents[index];
                          return _DocumentCard(
                            document: document,
                            onDelete: () async {
                              final confirmed = await _confirmDelete(document);
                              if (confirmed == true && mounted) {
                                await context.read<DocumentProvider>().deleteDocument(document.id);
                              }
                            },
                          );
                        },
                      ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showUploadOptions,
        icon: const Icon(Icons.add),
        label: const Text('Hochladen'),
      ),
    );
  }

  Future<bool?> _confirmDelete(Document document) {
    return showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Dokument löschen'),
        content: Text('Möchtest du "${document.title}" wirklich löschen?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Löschen'),
          ),
        ],
      ),
    );
  }
}

class _TypeOption extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final VoidCallback onTap;

  const _TypeOption({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 8),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: iconColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: iconColor),
            ),
            const SizedBox(width: 16),
            Text(
              title,
              style: const TextStyle(fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}

class _DocumentCard extends StatelessWidget {
  final Document document;
  final VoidCallback onDelete;

  const _DocumentCard({
    required this.document,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => DocumentDetailPage(documentId: document.id),
            ),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              _buildStatusIcon(),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      document.title,
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: _getTypeColor().withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            document.typeLabel,
                            style: TextStyle(
                              color: _getTypeColor(),
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        if (document.file != null) ...[
                          const Icon(Icons.insert_drive_file, size: 14, color: Colors.grey),
                          const SizedBox(width: 4),
                          Text(
                            document.file!.sizeFormatted,
                            style: const TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      DateFormat('dd.MM.yyyy HH:mm').format(document.uploadedAt),
                      style: const TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: const Icon(Icons.delete_outline, color: Colors.red),
                onPressed: onDelete,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusIcon() {
    IconData icon;
    Color color;
    String label;

    switch (document.processingStatus) {
      case 'pending':
        icon = Icons.schedule;
        color = Colors.orange;
        label = 'Wartend';
        break;
      case 'processing':
        icon = Icons.sync;
        color = Colors.blue;
        label = 'Verarbeitung';
        break;
      case 'done':
        icon = Icons.check_circle;
        color = Colors.green;
        label = 'Fertig';
        break;
      case 'needs_review':
        icon = Icons.flag;
        color = Colors.amber;
        label = 'Prüfung';
        break;
      case 'failed':
        icon = Icons.error;
        color = Colors.red;
        label = 'Fehler';
        break;
      default:
        icon = Icons.help;
        color = Colors.grey;
        label = 'Unbekannt';
    }

    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.15),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color, size: 28),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Color _getTypeColor() {
    switch (document.type) {
      case 'invoice':
        return Colors.blue;
      case 'reminder':
        return Colors.red;
      case 'contract':
        return Colors.purple;
      case 'receipt':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }
}
