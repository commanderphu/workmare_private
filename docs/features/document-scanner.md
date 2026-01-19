# Document Scanner

## Overview

Der Document Scanner ist das Eingangstor für alle Dokumente in Workmate Private. Er kombiniert moderne OCR-Technologie mit KI-Analyse für maximale Genauigkeit und Benutzerfreundlichkeit.

---

## Input Methods

### 1. Mobile Camera (Primary)

**Platform:** Flutter Camera Plugin

**Features:**
- Auto-Focus
- Auto-Exposure
- Edge Detection (Dokumenten-Ränder erkennen)
- Perspective Correction (Verzerrung korrigieren)
- Multi-Page Scan

**User Flow:**
```
1. User öffnet Scanner
2. Kamera aktiviert sich
3. Dokument ins Bild halten
4. Auto-Detection: Grüner Rahmen wenn Dokument erkannt
5. Auto-Capture oder manueller Button
6. Preview & Crop
7. Upload
```

**Implementation:**
```dart
import 'package:camera/camera.dart';

class DocumentScanner extends StatefulWidget {
  @override
  _DocumentScannerState createState() => _DocumentScannerState();
}

class _DocumentScannerState extends State<DocumentScanner> {
  CameraController? _controller;
  
  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }
  
  Future<void> _initializeCamera() async {
    final cameras = await availableCameras();
    _controller = CameraController(
      cameras.first,
      ResolutionPreset.high,
      enableAudio: false,
    );
    await _controller!.initialize();
    setState(() {});
  }
  
  Future<void> _captureDocument() async {
    final image = await _controller!.takePicture();
    // Edge detection & perspective correction
    final processed = await _processImage(image.path);
    // Upload
    await _uploadDocument(processed);
  }
}
```

### 2. File Upload (Scanner/Desktop)

**Supported Formats:**
- PDF (single/multi-page)
- Images: JPG, PNG, TIFF, WEBP
- Max Size: 20MB per file

**Features:**
- Drag & Drop (Web)
- File Picker (Mobile/Desktop)
- Batch Upload (multiple files at once)

**Implementation:**
```dart
import 'package:file_picker/file_picker.dart';

Future<void> _pickDocument() async {
  FilePickerResult? result = await FilePicker.platform.pickFiles(
    type: FileType.custom,
    allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png'],
    allowMultiple: true,
  );
  
  if (result != null) {
    for (var file in result.files) {
      await _uploadDocument(file.path!);
    }
  }
}
```

### 3. Email Import (Automatic)

**Setup:**
- User verbindet Email-Account (IMAP)
- Workmate scannt Inbox
- Automatischer Import von Anhängen

**Rules:**
```yaml
email_import_rules:
  - from: "*@telekom.de"
    action: auto_import
    category: invoice
  
  - subject: "Rechnung"
    action: auto_import
    category: invoice
  
  - attachment_type: "pdf"
    from: "*"
    action: auto_import
    category: other
```

**Implementation:**
```python
import imaplib
import email

class EmailImporter:
    def __init__(self, host: str, user: str, password: str):
        self.imap = imaplib.IMAP4_SSL(host)
        self.imap.login(user, password)
    
    def scan_inbox(self):
        self.imap.select('INBOX')
        _, messages = self.imap.search(None, 'UNSEEN')
        
        for msg_id in messages[0].split():
            _, msg_data = self.imap.fetch(msg_id, '(RFC822)')
            email_body = msg_data[0][1]
            message = email.message_from_bytes(email_body)
            
            # Extract attachments
            for part in message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                
                filename = part.get_filename()
                if filename and filename.endswith('.pdf'):
                    data = part.get_payload(decode=True)
                    await self._process_document(data, filename)
```

---

## OCR & Text Extraction

### Primary: Claude Vision API

**Why Claude Vision?**
- ✅ Beste Genauigkeit für Dokumente
- ✅ Multi-Language Support
- ✅ Kann strukturierte Daten extrahieren
- ✅ Versteht Kontext

**API Call:**
```python
import anthropic
import base64

async def extract_text_claude(image_path: str) -> str:
    with open(image_path, 'rb') as f:
        image_data = base64.standard_b64encode(f.read()).decode('utf-8')
    
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Extract all text from this document. Preserve structure and formatting."
                    }
                ],
            }
        ],
    )
    
    return message.content[0].text
```

### Fallback: Tesseract OCR

**When to use:**
- Self-Hosted without Claude API
- Offline Mode
- Cost Optimization

**Implementation:**
```python
import pytesseract
from PIL import Image

def extract_text_tesseract(image_path: str, lang: str = 'deu') -> str:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang=lang)
    return text
```

**Language Support:**
```bash
# Install Tesseract languages
apt-get install tesseract-ocr-deu  # German
apt-get install tesseract-ocr-eng  # English
```

---

## Image Processing Pipeline

### Pre-Processing Steps

**1. Grayscale Conversion**
```python
from PIL import Image

def to_grayscale(image_path: str) -> Image:
    img = Image.open(image_path)
    return img.convert('L')
```

**2. Deskew (Rotation Correction)**
```python
from PIL import Image
import numpy as np
from scipy.ndimage import rotate

def deskew(image: Image) -> Image:
    # Detect skew angle
    angle = detect_skew_angle(image)
    # Rotate
    return image.rotate(angle, expand=True)
```

**3. Contrast Enhancement**
```python
from PIL import ImageEnhance

def enhance_contrast(image: Image) -> Image:
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(2.0)
```

**4. Noise Reduction**
```python
import cv2
import numpy as np

def denoise(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
```

### Complete Pipeline
```python
class ImageProcessor:
    def process(self, image_path: str) -> str:
        # 1. Load
        img = Image.open(image_path)
        
        # 2. Convert to grayscale
        img = img.convert('L')
        
        # 3. Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # 4. Deskew
        img = self._deskew(img)
        
        # 5. Save processed
        processed_path = f"/tmp/processed_{uuid.uuid4()}.jpg"
        img.save(processed_path, quality=95)
        
        return processed_path
```

---

## Document Classification

### AI-Based Classification

**Prompt:**
```python
CLASSIFICATION_PROMPT = """
Analyze this document and classify it into one of these categories:
- invoice (Rechnung)
- reminder (Mahnung)
- contract (Vertrag)
- receipt (Quittung)
- other (Sonstiges)

Also extract:
- Confidence score (0-1)
- Key indicators (why this classification?)

Respond in JSON:
{
  "type": "invoice",
  "confidence": 0.95,
  "indicators": ["contains 'Rechnung' keyword", "has amount and due date", "formal structure"]
}
"""
```

**API Call:**
```python
async def classify_document(text: str) -> DocumentClassification:
    response = await claude_api.complete(
        prompt=f"{CLASSIFICATION_PROMPT}\n\nDocument Text:\n{text}",
        max_tokens=500
    )
    
    data = json.loads(response.text)
    return DocumentClassification(**data)
```

### Rule-Based Fallback

**Keywords per Type:**
```python
CLASSIFICATION_RULES = {
    'invoice': [
        'rechnung', 'invoice', 'betrag', 'amount',
        'fällig', 'due date', 'zahlbar', 'payable'
    ],
    'reminder': [
        'mahnung', 'reminder', 'zahlungserinnerung',
        'überfällig', 'overdue', 'letzte mahnung'
    ],
    'contract': [
        'vertrag', 'contract', 'laufzeit', 'term',
        'kündigung', 'cancellation', 'vereinbarung'
    ],
    'receipt': [
        'quittung', 'receipt', 'beleg', 'kaufbeleg',
        'kassenbon', 'bon'
    ]
}

def classify_by_rules(text: str) -> str:
    text_lower = text.lower()
    scores = {}
    
    for doc_type, keywords in CLASSIFICATION_RULES.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        scores[doc_type] = score
    
    return max(scores, key=scores.get) if scores else 'other'
```

---

## Metadata Extraction

### Structured Extraction via AI

**Prompt:**
```python
EXTRACTION_PROMPT = """
Extract the following information from this document:
- Amount (if any, as number)
- Currency (EUR, USD, etc.)
- Due date (ISO format YYYY-MM-DD)
- Invoice/Contract number
- Sender name
- Sender address
- Recipient name
- Payment information (IBAN, reference)

Respond in JSON. Use null for missing fields.

{
  "amount": 89.99,
  "currency": "EUR",
  "due_date": "2026-01-25",
  "invoice_number": "12345678",
  "sender": {
    "name": "Telekom Deutschland GmbH",
    "address": "..."
  },
  "recipient": {
    "name": "Joshua ...",
    "address": "..."
  },
  "payment_info": {
    "iban": "DE...",
    "reference": "..."
  }
}
"""
```

### Regex-Based Extraction (Fallback)

**Amount:**
```python
import re

def extract_amount(text: str) -> Optional[float]:
    patterns = [
        r'(\d+[.,]\d{2})\s*€',
        r'€\s*(\d+[.,]\d{2})',
        r'Betrag:?\s*(\d+[.,]\d{2})',
        r'Amount:?\s*(\d+[.,]\d{2})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount_str = match.group(1).replace(',', '.')
            return float(amount_str)
    
    return None
```

**Dates:**
```python
from dateutil import parser

def extract_dates(text: str) -> List[datetime]:
    patterns = [
        r'\d{2}\.\d{2}\.\d{4}',  # DD.MM.YYYY
        r'\d{4}-\d{2}-\d{2}',    # YYYY-MM-DD
    ]
    
    dates = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                date = parser.parse(match, dayfirst=True)
                dates.append(date)
            except:
                pass
    
    return dates
```

**IBAN:**
```python
def extract_iban(text: str) -> Optional[str]:
    pattern = r'[A-Z]{2}\d{2}[\s]?[\d\s]{12,30}'
    match = re.search(pattern, text)
    return match.group(0).replace(' ', '') if match else None
```

---

## Quality Assurance

### Confidence Scoring

**Factors:**
1. OCR Quality (clear text vs. noise)
2. Classification Confidence
3. Extraction Completeness (% of fields found)

**Score Calculation:**
```python
def calculate_confidence(
    ocr_quality: float,
    classification_conf: float,
    extraction_completeness: float
) -> float:
    weights = [0.3, 0.4, 0.3]  # OCR, Classification, Extraction
    scores = [ocr_quality, classification_conf, extraction_completeness]
    
    return sum(w * s for w, s in zip(weights, scores))
```

### User Validation

**Low Confidence Workflow:**
```
If confidence < 0.7:
  1. Show extracted data to user
  2. Highlight uncertain fields
  3. Ask for confirmation/correction
  4. Learn from corrections (future feature)
```

**UI Example:**
```
⚠️ Unsicher bei einigen Feldern (Konfidenz: 65%)

Betrag: 89.99 € ✅
Fälligkeitsdatum: 25.01.2026 ⚠️ [Korrigieren?]
Rechnungsnummer: 12345678 ✅
Absender: Telekom ❌ [Fehlt - Bitte ergänzen]

[Bestätigen] [Bearbeiten]
```

---

## Performance Optimization

### Async Processing

**Non-Blocking Upload:**
```python
@app.post("/documents/upload")
async def upload_document(file: UploadFile, background_tasks: BackgroundTasks):
    # 1. Save file immediately
    file_id = await storage.save(file)
    
    # 2. Create document record
    doc = await db.create_document(
        user_id=current_user.id,
        file_id=file_id,
        status="pending"
    )
    
    # 3. Queue processing
    background_tasks.add_task(process_document_async, doc.id)
    
    # 4. Return immediately
    return {"document_id": doc.id, "status": "processing"}
```

**Background Worker:**
```python
@celery_app.task
async def process_document_async(document_id: str):
    doc = await db.get_document(document_id)
    
    try:
        # OCR
        text = await ocr_service.extract(doc.file.path)
        
        # Classification
        classification = await ai_service.classify(text)
        
        # Metadata extraction
        metadata = await ai_service.extract_metadata(text)
        
        # Update document
        await db.update_document(
            document_id,
            status="done",
            extracted_text=text,
            type=classification.type,
            metadata=metadata,
            confidence=classification.confidence
        )
        
        # Create tasks
        await task_engine.create_from_document(doc)
        
    except Exception as e:
        await db.update_document(
            document_id,
            status="failed",
            error=str(e)
        )
```

### Caching

**Image Processing Results:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def process_image_cached(image_hash: str) -> str:
    return process_image(image_hash)
```

---

## Error Handling

### Common Errors

**1. Unreadable Image**
- Error: OCR confidence < 20%
- Solution: Ask user to re-scan

**2. Unknown Document Type**
- Error: Classification confidence < 50%
- Solution: Ask user to classify manually

**3. Missing Critical Data**
- Error: No amount or date found
- Solution: Show extraction, ask for manual input

**4. File Too Large**
- Error: > 20MB
- Solution: Compress or reject

### User Feedback
```python
ERROR_MESSAGES = {
    "ocr_failed": {
        "title": "Dokument unleserlich",
        "message": "Das Dokument konnte nicht gelesen werden. Bitte stelle sicher, dass das Bild scharf ist und das Dokument gut beleuchtet ist.",
        "action": "Erneut scannen"
    },
    "unknown_type": {
        "title": "Dokumenten-Typ unklar",
        "message": "Ich bin mir nicht sicher, um welche Art Dokument es sich handelt. Kannst du helfen?",
        "action": "Typ manuell auswählen"
    }
}
```

---

## Zusammenfassung

**Der Document Scanner:**
- ✅ Nimmt Dokumente auf (Foto, Upload, Email)
- ✅ Verarbeitet sie (OCR, Enhancement)
- ✅ Klassifiziert sie (KI + Rules)
- ✅ Extrahiert Metadaten (Beträge, Daten)
- ✅ Erstellt automatisch Tasks

**ADHD-Optimiert:**
- Schnell (< 5 Sekunden)
- Fehler-tolerant
- Minimale User-Intervention
- Klare Feedback