# Paperless-ngx Integration

## Overview

Die Paperless-ngx Integration ermöglicht es Power-Usern, ihre bestehende Paperless-Installation mit Workmate Private zu verbinden. Workmate fungiert als "intelligente Layer" on top von Paperless, die proaktive Task-Erstellung und Reminder-Funktionalität hinzufügt.

---

## Why Paperless-ngx?

**Paperless-ngx** ist ein Open-Source Dokumenten-Management-System (DMS), das bereits von vielen Self-Hostern genutzt wird.

**Vorteile:**
- ✅ Etablierte Lösung mit großer Community
- ✅ Hervorragende OCR-Fähigkeiten
- ✅ Leistungsstarke Archivierung & Suche
- ✅ Tag-System & Custom Fields
- ✅ Workflow-Automation

**Was Paperless NICHT hat:**
- ❌ Proaktive Reminders
- ❌ Task-Management
- ❌ Eskalations-Logik
- ❌ Multi-Channel Notifications
- ❌ SLA-Monitoring

**→ Genau hier setzt Workmate Private an!**

---

## Integration Architecture
```
┌────────────────────────────────────────┐
│     Paperless-ngx                      │
│  (Document Archive & OCR)              │
└────────────┬───────────────────────────┘
             │ REST API
             │
┌────────────▼───────────────────────────┐
│  Workmate Private                      │
│  - Reads documents from Paperless      │
│  - Creates tasks & reminders           │
│  - Writes tags/custom fields back      │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│  Notifications & Reminders             │
│  (Push, Email, SMS, Smart Home)        │
└────────────────────────────────────────┘
```

**Flow:**
1. User scanned Dokument → Paperless-ngx
2. Paperless macht OCR & Archivierung
3. Workmate liest Dokument via API
4. Workmate analysiert mit KI (Claude)
5. Workmate erstellt Tasks & Reminders
6. Workmate schreibt Tags/Notes zurück zu Paperless

---

## Paperless API

### Authentication
```python
import aiohttp
from typing import Optional, List, Dict

class PaperlessAPI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict = None,
        params: dict = None
    ):
        """Make authenticated request to Paperless API"""
        
        url = f"{self.base_url}/api{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                headers=self.headers,
                json=data,
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
```

### Get Documents
```python
async def get_documents(
    self,
    created_after: datetime = None,
    page: int = 1,
    page_size: int = 50
) -> Dict:
    """Fetch documents from Paperless"""
    
    params = {
        "page": page,
        "page_size": page_size,
        "ordering": "-created"
    }
    
    if created_after:
        params["created__date__gte"] = created_after.strftime("%Y-%m-%d")
    
    return await self._request("GET", "/documents/", params=params)

async def get_document(self, document_id: int) -> Dict:
    """Get single document details"""
    
    return await self._request("GET", f"/documents/{document_id}/")

async def download_document(self, document_id: int) -> bytes:
    """Download document file"""
    
    url = f"{self.base_url}/api/documents/{document_id}/download/"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=self.headers) as response:
            return await response.read()
```

### Update Document
```python
async def update_document(
    self,
    document_id: int,
    tags: List[int] = None,
    custom_fields: List[Dict] = None,
    notes: str = None
) -> Dict:
    """Update document metadata"""
    
    data = {}
    
    if tags is not None:
        data["tags"] = tags
    
    if custom_fields is not None:
        data["custom_fields"] = custom_fields
    
    if notes is not None:
        data["notes"] = notes
    
    return await self._request(
        "PATCH",
        f"/documents/{document_id}/",
        data=data
    )
```

### Tags & Custom Fields
```python
async def get_tags(self) -> List[Dict]:
    """Get all tags"""
    return await self._request("GET", "/tags/")

async def create_tag(self, name: str, color: str = "#00ff00") -> Dict:
    """Create new tag"""
    return await self._request(
        "POST",
        "/tags/",
        data={"name": name, "color": color}
    )

async def get_custom_fields(self) -> List[Dict]:
    """Get all custom fields"""
    return await self._request("GET", "/custom_fields/")

async def create_custom_field(
    self,
    name: str,
    data_type: str = "string"
) -> Dict:
    """Create new custom field"""
    return await self._request(
        "POST",
        "/custom_fields/",
        data={"name": name, "data_type": data_type}
    )
```

---

## Integration Service

### Sync Service
```python
class PaperlessSyncService:
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        self.integration = self._load_integration()
        self.paperless = self._init_paperless_client()
    
    def _load_integration(self) -> Integration:
        """Load Paperless integration config"""
        return await db.query(Integration).filter(
            Integration.user_id == self.user_id,
            Integration.integration_type == "paperless_ngx"
        ).first()
    
    def _init_paperless_client(self) -> PaperlessAPI:
        """Initialize Paperless API client"""
        
        config = self.integration.config
        credentials = self.integration.get_credentials(settings.ENCRYPTION_KEY)
        
        return PaperlessAPI(
            base_url=config['url'],
            token=credentials['token']
        )
```

### Import Documents
```python
async def import_new_documents(self):
    """Import new documents from Paperless"""
    
    # Get last sync time
    last_sync = self.integration.last_sync_at or (datetime.now() - timedelta(days=365))
    
    # Fetch new documents
    result = await self.paperless.get_documents(created_after=last_sync)
    
    documents = result['results']
    
    for paperless_doc in documents:
        try:
            await self._process_paperless_document(paperless_doc)
        except Exception as e:
            logger.error(f"Failed to process document {paperless_doc['id']}: {e}")
    
    # Update sync timestamp
    self.integration.last_sync_at = datetime.now()
    await db.save(self.integration)

async def _process_paperless_document(self, paperless_doc: Dict):
    """Process single Paperless document"""
    
    # Check if already imported
    existing = await db.query(Document).filter(
        Document.user_id == self.user_id,
        Document.metadata['paperless_id'].astext == str(paperless_doc['id'])
    ).first()
    
    if existing:
        logger.info(f"Document {paperless_doc['id']} already imported")
        return
    
    # Download document
    file_data = await self.paperless.download_document(paperless_doc['id'])
    
    # Save to Workmate storage
    file_path = await storage_service.save_file(
        user_id=self.user_id,
        filename=paperless_doc['original_file_name'],
        data=file_data
    )
    
    # Create Workmate document
    doc = Document(
        user_id=self.user_id,
        file_path=file_path,
        title=paperless_doc['title'],
        extracted_text=paperless_doc.get('content', ''),
        metadata={
            'paperless_id': paperless_doc['id'],
            'paperless_created': paperless_doc['created'],
            'paperless_tags': paperless_doc.get('tags', [])
        },
        processing_status='pending'
    )
    
    await db.save(doc)
    
    # Trigger AI processing
    await document_processor.process_document(doc.id)
```

### Write Back to Paperless
```python
async def write_back_to_paperless(self, document_id: UUID):
    """Write Workmate analysis back to Paperless"""
    
    # Get Workmate document
    doc = await db.get_document(document_id)
    
    if not doc.metadata.get('paperless_id'):
        return  # Not a Paperless document
    
    paperless_id = doc.metadata['paperless_id']
    
    # Prepare tags
    tags_to_add = await self._prepare_tags(doc)
    
    # Prepare custom fields
    custom_fields = await self._prepare_custom_fields(doc)
    
    # Prepare notes
    notes = self._generate_notes(doc)
    
    # Update Paperless document
    await self.paperless.update_document(
        document_id=paperless_id,
        tags=tags_to_add,
        custom_fields=custom_fields,
        notes=notes
    )

async def _prepare_tags(self, doc: Document) -> List[int]:
    """Prepare tags for Paperless"""
    
    # Get or create Workmate tag
    workmate_tag = await self._get_or_create_tag("workmate-processed")
    
    tags = [workmate_tag['id']]
    
    # Add document type tag
    if doc.type:
        type_tag = await self._get_or_create_tag(f"type:{doc.type}")
        tags.append(type_tag['id'])
    
    # Add priority tag if task created
    if doc.tasks:
        task = doc.tasks[0]
        priority_tag = await self._get_or_create_tag(f"priority:{task.priority}")
        tags.append(priority_tag['id'])
    
    return tags

async def _prepare_custom_fields(self, doc: Document) -> List[Dict]:
    """Prepare custom fields for Paperless"""
    
    fields = []
    
    # Due date
    if doc.metadata.get('due_date'):
        due_date_field = await self._get_or_create_custom_field(
            "workmate_due_date",
            "date"
        )
        fields.append({
            "field": due_date_field['id'],
            "value": doc.metadata['due_date']
        })
    
    # Amount
    if doc.metadata.get('amount'):
        amount_field = await self._get_or_create_custom_field(
            "workmate_amount",
            "monetary"
        )
        fields.append({
            "field": amount_field['id'],
            "value": doc.metadata['amount']
        })
    
    # Task ID
    if doc.tasks:
        task_id_field = await self._get_or_create_custom_field(
            "workmate_task_id",
            "string"
        )
        fields.append({
            "field": task_id_field['id'],
            "value": str(doc.tasks[0].id)
        })
    
    return fields

def _generate_notes(self, doc: Document) -> str:
    """Generate notes for Paperless"""
    
    notes = f"Processed by Workmate Private on {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    notes += f"Type: {doc.type}\n"
    notes += f"Confidence: {doc.confidence_score:.2%}\n\n"
    
    if doc.tasks:
        notes += "Tasks created:\n"
        for task in doc.tasks:
            notes += f"- {task.title} (Priority: {task.priority}, Due: {task.due_date})\n"
    
    return notes
```

---

## Bidirectional Sync

### Paperless → Workmate

**Use Case:** User uploaded Dokument direkt in Paperless, Workmate soll es automatisch verarbeiten

**Implementation:** Webhook oder Periodic Polling

**Webhook (wenn Paperless configured):**
```python
@app.post("/webhooks/paperless")
async def paperless_webhook(
    request: Request,
    x_paperless_signature: str = Header(None)
):
    """Handle Paperless webhook for new documents"""
    
    # Verify signature (if configured)
    if x_paperless_signature:
        payload = await request.body()
        if not verify_paperless_signature(payload, x_paperless_signature):
            raise HTTPException(401, "Invalid signature")
    
    data = await request.json()
    
    if data['event'] == 'document_added':
        document_id = data['document']['id']
        user_id = await _get_user_for_paperless_instance(request.headers.get('x-paperless-instance'))
        
        # Trigger import
        await paperless_sync_service.import_document(user_id, document_id)
    
    return {"status": "ok"}
```

**Polling (fallback):**
```python
@celery_app.task
async def poll_paperless_for_new_documents():
    """Periodic task to check for new Paperless documents"""
    
    integrations = await db.query(Integration).filter(
        Integration.integration_type == "paperless_ngx",
        Integration.enabled == True
    ).all()
    
    for integration in integrations:
        try:
            sync_service = PaperlessSyncService(integration.user_id)
            await sync_service.import_new_documents()
        except Exception as e:
            logger.error(f"Failed to poll Paperless for user {integration.user_id}: {e}")
```

### Workmate → Paperless

**Use Case:** User scanned Dokument in Workmate, soll auch in Paperless archiviert werden

**Implementation:**
```python
async def export_to_paperless(self, document_id: UUID):
    """Export Workmate document to Paperless"""
    
    doc = await db.get_document(document_id)
    
    if doc.metadata.get('paperless_id'):
        logger.info(f"Document {document_id} already in Paperless")
        return
    
    # Upload to Paperless
    with open(doc.file_path, 'rb') as f:
        file_data = f.read()
    
    paperless_doc = await self.paperless.upload_document(
        filename=doc.original_filename,
        data=file_data,
        title=doc.title,
        correspondent=doc.metadata.get('sender', {}).get('name'),
        document_type=self._map_workmate_type_to_paperless(doc.type)
    )
    
    # Update Workmate document with Paperless ID
    doc.metadata['paperless_id'] = paperless_doc['id']
    await db.save(doc)
    
    logger.info(f"Exported document {document_id} to Paperless as {paperless_doc['id']}")
```

---

## Configuration UI

### Setup Flow
```dart
// Flutter UI for Paperless setup
class PaperlessSetup extends StatefulWidget {
  @override
  _PaperlessSetupState createState() => _PaperlessSetupState();
}

class _PaperlessSetupState extends State<PaperlessSetup> {
  String _paperlessUrl = '';
  String _paperlessToken = '';
  bool _bidirectionalSync = true;
  bool _autoExport = false;
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Paperless-ngx Integration')),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          Text(
            'Verbinde deine Paperless-ngx Installation',
            style: Theme.of(context).textTheme.headline6,
          ),
          SizedBox(height: 16),
          
          TextField(
            decoration: InputDecoration(
              labelText: 'Paperless URL',
              hintText: 'http://paperless.local:8000',
              helperText: 'URL deiner Paperless Installation',
            ),
            onChanged: (value) => setState(() => _paperlessUrl = value),
          ),
          
          SizedBox(height: 16),
          
          TextField(
            decoration: InputDecoration(
              labelText: 'API Token',
              helperText: 'Erstelle einen Token in Paperless unter Settings > API',
            ),
            obscureText: true,
            onChanged: (value) => setState(() => _paperlessToken = value),
          ),
          
          SizedBox(height: 24),
          
          SwitchListTile(
            title: Text('Bidirektionale Synchronisation'),
            subtitle: Text('Dokumente werden in beide Richtungen synchronisiert'),
            value: _bidirectionalSync,
            onChanged: (value) => setState(() => _bidirectionalSync = value),
          ),
          
          SwitchListTile(
            title: Text('Automatischer Export'),
            subtitle: Text('Neue Workmate-Dokumente automatisch in Paperless archivieren'),
            value: _autoExport,
            onChanged: (value) => setState(() => _autoExport = value),
          ),
          
          SizedBox(height: 24),
          
          ElevatedButton(
            onPressed: _testConnection,
            child: Text('Verbindung testen'),
          ),
          
          SizedBox(height: 8),
          
          ElevatedButton(
            onPressed: _saveConfiguration,
            child: Text('Speichern & Aktivieren'),
            style: ElevatedButton.styleFrom(primary: Colors.green),
          ),
        ],
      ),
    );
  }
  
  Future<void> _testConnection() async {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Teste Verbindung...'),
        content: CircularProgressIndicator(),
      ),
    );
    
    try {
      final response = await http.get(
        Uri.parse('$_paperlessUrl/api/documents/'),
        headers: {'Authorization': 'Token $_paperlessToken'},
      );
      
      Navigator.pop(context);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: Text('✅ Verbindung erfolgreich!'),
            content: Text('${data['count']} Dokumente gefunden in Paperless'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: Text('OK'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      Navigator.pop(context);
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('❌ Fehler'),
          content: Text('Verbindung fehlgeschlagen: $e'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('OK'),
            ),
          ],
        ),
      );
    }
  }
  
  Future<void> _saveConfiguration() async {
    await api.post('/integrations/paperless', {
      'url': _paperlessUrl,
      'token': _paperlessToken,
      'bidirectional_sync': _bidirectionalSync,
      'auto_export': _autoExport,
    });
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('✅ Paperless Integration aktiviert!')),
    );
    
    Navigator.pop(context);
  }
}
```

---

## Use Cases

### Use Case 1: Power User mit bestehendem Paperless

**Persona:** Joshua hat bereits 5000+ Dokumente in Paperless archiviert

**Workflow:**
1. Aktiviert Paperless Integration in Workmate
2. Workmate importiert alle Rechnungen der letzten 12 Monate
3. Erstellt automatisch Tasks für offene Rechnungen
4. Schreibt Task-IDs zurück in Paperless Custom Fields
5. Bei Task-Completion: Updated Paperless-Dokument mit "paid" Tag

**Benefits:**
- Nutzt bestehende Paperless-Infrastruktur
- Kein Datenverlust oder Migration nötig
- Best of both worlds: Paperless Archiv + Workmate Intelligence

### Use Case 2: Hybrid Workflow

**Persona:** User scannt manchmal in Workmate, manchmal in Paperless

**Workflow:**
1. Bidirektionale Sync aktiviert
2. Dokument in Paperless → automatisch in Workmate importiert → Tasks erstellt
3. Dokument in Workmate → automatisch in Paperless exportiert → archiviert
4. Beide Systeme bleiben synchron

### Use Case 3: Paperless als Archiv

**Persona:** User nutzt Workmate für aktive Tasks, Paperless nur zur Langzeit-Archivierung

**Workflow:**
1. Dokument in Workmate verarbeitet
2. Task erledigt → Dokument nach Paperless exportieren
3. Aus Workmate löschen (oder archivieren)
4. Paperless als langfristiges Archiv

---

## Advanced Features

### Smart Tag Mapping
```python
class SmartTagMapper:
    """Map Workmate analysis to Paperless tags intelligently"""
    
    TAG_MAPPING = {
        'invoice': 'workmate:rechnung',
        'reminder': 'workmate:mahnung',
        'contract': 'workmate:vertrag',
        'receipt': 'workmate:quittung',
    }
    
    PRIORITY_MAPPING = {
        'critical': 'workmate:dringend',
        'high': 'workmate:wichtig',
        'medium': 'workmate:normal',
        'low': 'workmate:niedrig',
    }
    
    async def generate_tags(self, doc: Document) -> List[str]:
        """Generate Paperless tags based on Workmate analysis"""
        
        tags = []
        
        # Document type
        if doc.type in self.TAG_MAPPING:
            tags.append(self.TAG_MAPPING[doc.type])
        
        # Priority (if task exists)
        if doc.tasks:
            priority = doc.tasks[0].priority
            if priority in self.PRIORITY_MAPPING:
                tags.append(self.PRIORITY_MAPPING[priority])
        
        # Amount-based
        if doc.metadata.get('amount'):
            amount = doc.metadata['amount']
            if amount > 500:
                tags.append('workmate:high-amount')
        
        # Sender-based
        if doc.metadata.get('sender', {}).get('name'):
            sender = doc.metadata['sender']['name'].lower()
            # Normalize sender name
            sender_tag = f"sender:{sender.replace(' ', '-')}"
            tags.append(sender_tag)
        
        return tags
```

### Automatic Correspondent Matching
```python
async def match_correspondent(self, sender_name: str) -> Optional[int]:
    """Match Workmate sender to Paperless correspondent"""
    
    # Get all correspondents from Paperless
    correspondents = await self.paperless.get_correspondents()
    
    # Fuzzy match
    from fuzzywuzzy import fuzz
    
    best_match = None
    best_score = 0
    
    for correspondent in correspondents:
        score = fuzz.ratio(
            sender_name.lower(),
            correspondent['name'].lower()
        )
        
        if score > best_score and score > 80:  # 80% similarity threshold
            best_match = correspondent['id']
            best_score = score
    
    # If no match found, create new correspondent
    if not best_match:
        new_correspondent = await self.paperless.create_correspondent(sender_name)
        return new_correspondent['id']
    
    return best_match
```

---

## Monitoring & Analytics

### Sync Status Dashboard
```python
class PaperlessSyncAnalytics:
    async def get_sync_stats(self, user_id: UUID) -> Dict:
        """Get Paperless sync statistics"""
        
        integration = await db.query(Integration).filter(
            Integration.user_id == user_id,
            Integration.integration_type == "paperless_ngx"
        ).first()
        
        if not integration:
            return None
        
        # Count documents
        total_docs = await db.query(Document).filter(
            Document.user_id == user_id,
            Document.metadata['paperless_id'].isnot(None)
        ).count()
        
        # Recent syncs
        recent_syncs = await db.query(Document).filter(
            Document.user_id == user_id,
            Document.metadata['paperless_id'].isnot(None),
            Document.created_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        return {
            'enabled': integration.enabled,c
            'last_sync': integration.last_sync_at,
            'total_documents': total_docs,
            'synced_this_week': recent_syncs,
            'sync_status': integration.sync_status,
            'errors': integration.error_log
        }
```

---

## Troubleshooting

### Common Issues

**1. Authentication Failed**
```python
async def test_authentication(url: str, token: str) -> bool:
    """Test Paperless authentication"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{url}/api/",
                headers={"Authorization": f"Token {token}"}
            ) as response:
                return response.status == 200
    except:
        return False
```

**2. Network Unreachable**
```python
def is_local_network(url: str) -> bool:
    """Check if Paperless URL is on local network"""
    from urllib.parse import urlparse
    import ipaddress
    
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private
    except:
        return hostname.endswith('.local')
```

---

## Testing
```python
@pytest.mark.integration
async def test_paperless_integration():
    # Setup mock Paperless
    paperless = PaperlessAPI(
        base_url="http://localhost:8000",
        token="test_token"
    )
    
    # Test document fetch
    docs = await paperless.get_documents()
    assert 'results' in docs
    
    # Test document download
    if docs['results']:
        doc_id = docs['results'][0]['id']
        file_data = await paperless.download_document(doc_id)
        assert len(file_data) > 0
```

---

## Zusammenfassung

**Paperless-ngx Integration Features:**
- ✅ Import from Paperless
- ✅ Export to Paperless
- ✅ Bidirectional Sync
- ✅ Tag Mapping
- ✅ Custom Fields
- ✅ Correspondent Matching
- ✅ Webhook Support
- ✅ Periodic Polling

**Benefits:**
- Nutzt bestehende Paperless-Installation
- Workmate als intelligente Layer
- Best of both worlds
- Keine Migration nötig
- Power-User friendly

**ADHD-Optimierung:**
- Alle Vorteile von Paperless (Archiv, OCR, Suche)
- PLUS: Proaktive Reminders, Tasks, Eskalation
- Nahtlose Integration, keine Doppelarbeit