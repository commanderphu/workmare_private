# AI Processor

## Overview

Der AI Processor ist das Herzstück der intelligenten Dokumenten-Analyse in Workmate Private. Er nutzt Claude API (Cloud) oder Ollama (Self-Hosted) für Dokumenten-Klassifizierung, Metadaten-Extraktion und kontextuelle Analyse.

---

## Architecture
```
┌─────────────────────────────────────────────┐
│           AI Processor Service              │
│                                             │
│  ┌─────────────┐        ┌─────────────┐    │
│  │   Claude    │        │   Ollama    │    │
│  │     API     │        │   Local     │    │
│  └──────┬──────┘        └──────┬──────┘    │
│         │                      │            │
│         └──────────┬───────────┘            │
│                    │                        │
│         ┌──────────▼──────────┐             │
│         │  AI Strategy Router │             │
│         └──────────┬──────────┘             │
│                    │                        │
│         ┌──────────▼──────────┐             │
│         │  Response Parser    │             │
│         └──────────┬──────────┘             │
│                    │                        │
│         ┌──────────▼──────────┐             │
│         │  Task Generator     │             │
│         └─────────────────────┘             │
└─────────────────────────────────────────────┘
```

---

## AI Strategy Pattern

### Strategy Router
```python
from abc import ABC, abstractmethod
from enum import Enum

class AIProvider(str, Enum):
    CLAUDE = "claude"
    OLLAMA = "ollama"

class AIStrategy(ABC):
    @abstractmethod
    async def analyze_document(self, text: str, image_path: str = None) -> DocumentAnalysis:
        pass
    
    @abstractmethod
    async def classify(self, text: str) -> Classification:
        pass
    
    @abstractmethod
    async def extract_metadata(self, text: str, doc_type: str) -> dict:
        pass

class AIProcessor:
    def __init__(self, provider: AIProvider):
        self.strategy = self._get_strategy(provider)
    
    def _get_strategy(self, provider: AIProvider) -> AIStrategy:
        if provider == AIProvider.CLAUDE:
            return ClaudeStrategy()
        elif provider == AIProvider.OLLAMA:
            return OllamaStrategy()
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def analyze_document(self, text: str, image_path: str = None) -> DocumentAnalysis:
        return await self.strategy.analyze_document(text, image_path)
```

---

## Claude Strategy

### Configuration
```python
import anthropic
from anthropic.types import Message

class ClaudeStrategy(AIStrategy):
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=settings.ANTHROPIC_API_KEY
        )
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 2000
```

### Document Analysis

**Complete Analysis Prompt:**
```python
DOCUMENT_ANALYSIS_PROMPT = """
You are an AI assistant specialized in analyzing financial and administrative documents.

Analyze this document and provide:

1. **Classification:**
   - Type: invoice, reminder, contract, receipt, or other
   - Confidence: 0.0 to 1.0
   - Reasoning: Why this classification?

2. **Metadata Extraction:**
   - amount: numerical value (null if not found)
   - currency: ISO code (EUR, USD, etc.)
   - due_date: ISO format YYYY-MM-DD
   - invoice_number: string
   - sender: { name, address, tax_id }
   - recipient: { name, address }
   - payment_info: { iban, bic, reference }

3. **Action Items:**
   - What actions need to be taken?
   - When are they due?
   - Priority level (low, medium, high, critical)

4. **Context:**
   - Any special notes or important details
   - Potential risks (late fees, deadlines, etc.)

Respond ONLY with valid JSON:
{
  "classification": {
    "type": "invoice",
    "confidence": 0.95,
    "reasoning": "Contains 'Rechnung' header, amount, due date, and payment instructions"
  },
  "metadata": {
    "amount": 89.99,
    "currency": "EUR",
    "due_date": "2026-01-25",
    "invoice_number": "RE-2026-001",
    "sender": {
      "name": "Telekom Deutschland GmbH",
      "address": "Friedrich-Ebert-Allee 140, 53113 Bonn",
      "tax_id": "DE123456789"
    },
    "recipient": {
      "name": "Joshua ...",
      "address": "..."
    },
    "payment_info": {
      "iban": "DE89370400440532013000",
      "bic": "COBADEFFXXX",
      "reference": "RE-2026-001"
    }
  },
  "action_items": [
    {
      "action": "Pay invoice",
      "due_date": "2026-01-25",
      "priority": "high",
      "details": "Payment must be received by due date to avoid late fees"
    }
  ],
  "context": {
    "notes": "Monthly mobile phone bill",
    "risks": ["Late fee of 5€ if not paid on time"]
  }
}
"""
```

### Implementation
```python
async def analyze_document(
    self, 
    text: str, 
    image_path: str = None
) -> DocumentAnalysis:
    
    messages = []
    
    # If image available, use Vision
    if image_path:
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')
        
        messages.append({
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
                    "text": DOCUMENT_ANALYSIS_PROMPT
                }
            ],
        })
    else:
        # Text-only
        messages.append({
            "role": "user",
            "content": f"{DOCUMENT_ANALYSIS_PROMPT}\n\nDocument Text:\n{text}"
        })
    
    # Call API
    response = self.client.messages.create(
        model=self.model,
        max_tokens=self.max_tokens,
        messages=messages
    )
    
    # Parse JSON response
    response_text = response.content[0].text
    
    # Extract JSON (handle markdown code blocks)
    json_str = self._extract_json(response_text)
    data = json.loads(json_str)
    
    return DocumentAnalysis(**data)

def _extract_json(self, text: str) -> str:
    """Extract JSON from markdown code blocks"""
    # Remove ```json and ``` markers
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    return text.strip()
```

### Rate Limiting & Retry
```python
from tenacity import retry, stop_after_attempt, wait_exponential

class ClaudeStrategy(AIStrategy):
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def analyze_document(self, text: str, image_path: str = None):
        try:
            return await self._analyze_document_impl(text, image_path)
        except anthropic.RateLimitError as e:
            logger.warning(f"Claude rate limit hit: {e}")
            raise
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise
```

### Cost Optimization

**Token Counting:**
```python
def estimate_tokens(text: str) -> int:
    """Rough estimation: 1 token ≈ 4 characters"""
    return len(text) // 4

def truncate_if_needed(text: str, max_tokens: int = 8000) -> str:
    """Truncate text to fit within token limit"""
    estimated = estimate_tokens(text)
    
    if estimated > max_tokens:
        # Keep first and last parts
        chars_limit = max_tokens * 4
        half = chars_limit // 2
        return text[:half] + "\n\n[... truncated ...]\n\n" + text[-half:]
    
    return text
```

**Caching Strategy:**
```python
from functools import lru_cache
import hashlib

def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

@lru_cache(maxsize=1000)
async def analyze_cached(text_hash: str, text: str):
    return await analyze_document(text)
```

---

## Ollama Strategy (Self-Hosted)

### Configuration
```python
import aiohttp

class OllamaStrategy(AIStrategy):
    def __init__(self):
        self.base_url = settings.OLLAMA_URL or "http://localhost:11434"
        self.model = settings.OLLAMA_MODEL or "llama3.1:8b"
```

### Document Analysis
```python
async def analyze_document(
    self, 
    text: str, 
    image_path: str = None
) -> DocumentAnalysis:
    
    prompt = f"{DOCUMENT_ANALYSIS_PROMPT}\n\nDocument Text:\n{text}"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"  # Force JSON output
            }
        ) as response:
            data = await response.json()
            response_text = data['response']
            
            # Parse JSON
            json_data = json.loads(response_text)
            return DocumentAnalysis(**json_data)
```

### Model Selection
```python
OLLAMA_MODELS = {
    "fast": "llama3.1:8b",      # Quick, less accurate
    "balanced": "mistral:7b",   # Good balance
    "accurate": "llama3.1:70b"  # Slow, very accurate
}

def select_model(priority: str = "balanced") -> str:
    return OLLAMA_MODELS.get(priority, OLLAMA_MODELS["balanced"])
```

### Performance Considerations

**GPU Acceleration:**
```bash
# Check if GPU available
nvidia-smi

# Run Ollama with GPU
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 ollama/ollama
```

**Model Loading:**
```python
async def preload_model():
    """Load model into memory on startup"""
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": "Hello",  # Dummy prompt to load model
                "keep_alive": -1    # Keep in memory
            }
        )
```

---

## Response Parsing

### Structured Output Parser
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List

class Sender(BaseModel):
    name: str
    address: Optional[str] = None
    tax_id: Optional[str] = None

class PaymentInfo(BaseModel):
    iban: Optional[str] = None
    bic: Optional[str] = None
    reference: Optional[str] = None

class ActionItem(BaseModel):
    action: str
    due_date: Optional[str] = None
    priority: str = "medium"
    details: Optional[str] = None

class DocumentMetadata(BaseModel):
    amount: Optional[float] = None
    currency: str = "EUR"
    due_date: Optional[str] = None
    invoice_number: Optional[str] = None
    sender: Optional[Sender] = None
    recipient: Optional[Sender] = None
    payment_info: Optional[PaymentInfo] = None

class Classification(BaseModel):
    type: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str

class DocumentAnalysis(BaseModel):
    classification: Classification
    metadata: DocumentMetadata
    action_items: List[ActionItem] = []
    context: dict = {}
    
    @validator('classification')
    def validate_type(cls, v):
        valid_types = ['invoice', 'reminder', 'contract', 'receipt', 'other']
        if v.type not in valid_types:
            raise ValueError(f"Invalid type: {v.type}")
        return v
```

### Error Handling
```python
class AIResponseError(Exception):
    pass

def parse_ai_response(response_text: str) -> DocumentAnalysis:
    try:
        # Try to parse as JSON
        data = json.loads(response_text)
        return DocumentAnalysis(**data)
    
    except json.JSONDecodeError:
        # Try to extract JSON from text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return DocumentAnalysis(**data)
            except:
                pass
        
        raise AIResponseError("Could not parse AI response as JSON")
    
    except ValidationError as e:
        logger.error(f"Invalid AI response structure: {e}")
        raise AIResponseError(f"Invalid response structure: {e}")
```

---

## Task Generation from Analysis

### Task Generator
```python
class TaskGenerator:
    async def generate_from_analysis(
        self,
        document_id: UUID,
        analysis: DocumentAnalysis,
        user_id: UUID
    ) -> List[Task]:
        
        tasks = []
        
        # Generate tasks from action items
        for action_item in analysis.action_items:
            task = await self._create_task(
                user_id=user_id,
                document_id=document_id,
                title=action_item.action,
                due_date=action_item.due_date,
                priority=action_item.priority,
                description=action_item.details,
                amount=analysis.metadata.amount
            )
            tasks.append(task)
        
        # If no action items, create default task based on type
        if not tasks:
            task = await self._create_default_task(
                user_id=user_id,
                document_id=document_id,
                doc_type=analysis.classification.type,
                metadata=analysis.metadata
            )
            tasks.append(task)
        
        return tasks
    
    async def _create_default_task(
        self,
        user_id: UUID,
        document_id: UUID,
        doc_type: str,
        metadata: DocumentMetadata
    ) -> Task:
        
        if doc_type == "invoice":
            title = f"Rechnung bezahlen"
            if metadata.sender:
                title += f" - {metadata.sender.name}"
            if metadata.amount:
                title += f" ({metadata.amount:.2f} {metadata.currency})"
            
            return await db.create_task(
                user_id=user_id,
                document_id=document_id,
                title=title,
                due_date=metadata.due_date,
                priority="high" if metadata.amount and metadata.amount > 100 else "medium",
                amount=metadata.amount
            )
        
        elif doc_type == "contract":
            # Check for cancellation deadline
            title = "Vertrag prüfen"
            if metadata.sender:
                title += f" - {metadata.sender.name}"
            
            return await db.create_task(
                user_id=user_id,
                document_id=document_id,
                title=title,
                priority="medium"
            )
        
        else:
            # Generic task
            return await db.create_task(
                user_id=user_id,
                document_id=document_id,
                title=f"Dokument bearbeiten ({doc_type})",
                priority="low"
            )
```

---

## Quality Assurance

### Confidence Thresholds
```python
CONFIDENCE_THRESHOLDS = {
    "auto_process": 0.85,    # Full automation
    "review_suggested": 0.70, # Show to user, suggest values
    "manual_required": 0.50,  # Ask user to review/correct
    "reject": 0.30           # Too uncertain, re-scan
}

def determine_workflow(confidence: float) -> str:
    if confidence >= CONFIDENCE_THRESHOLDS["auto_process"]:
        return "auto"
    elif confidence >= CONFIDENCE_THRESHOLDS["review_suggested"]:
        return "review"
    elif confidence >= CONFIDENCE_THRESHOLDS["manual_required"]:
        return "manual"
    else:
        return "reject"
```

### Human-in-the-Loop
```python
class DocumentProcessor:
    async def process_with_validation(
        self,
        document_id: UUID,
        analysis: DocumentAnalysis
    ):
        
        confidence = analysis.classification.confidence
        workflow = determine_workflow(confidence)
        
        if workflow == "auto":
            # Fully automated
            await self._create_tasks_and_finalize(document_id, analysis)
        
        elif workflow == "review":
            # Show to user with suggestions
            await self._request_user_review(
                document_id,
                analysis,
                message="Bitte überprüfe die extrahierten Daten"
            )
        
        elif workflow == "manual":
            # Ask user to fill in missing data
            await self._request_manual_input(
                document_id,
                analysis,
                message="Einige Felder konnten nicht erkannt werden"
            )
        
        else:  # reject
            # Ask to re-scan
            await self._request_rescan(
                document_id,
                message="Dokument konnte nicht zuverlässig gelesen werden"
            )
```

---

## Performance Metrics

### Tracking
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AIMetrics:
    provider: str
    model: str
    duration_ms: float
    tokens_used: int
    cost_usd: float
    confidence: float
    success: bool
    timestamp: datetime

class MetricsCollector:
    async def track_analysis(
        self,
        provider: str,
        model: str,
        start_time: datetime,
        result: DocumentAnalysis
    ):
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        metrics = AIMetrics(
            provider=provider,
            model=model,
            duration_ms=duration,
            tokens_used=self._estimate_tokens(result),
            cost_usd=self._calculate_cost(provider, model, tokens_used),
            confidence=result.classification.confidence,
            success=True,
            timestamp=datetime.now()
        )
        
        await db.save_metrics(metrics)
```

### Monitoring Dashboard
```python
class AIAnalytics:
    async def get_summary(self, days: int = 7) -> dict:
        metrics = await db.get_metrics(days=days)
        
        return {
            "total_documents": len(metrics),
            "avg_confidence": mean([m.confidence for m in metrics]),
            "avg_duration_ms": mean([m.duration_ms for m in metrics]),
            "success_rate": sum([m.success for m in metrics]) / len(metrics),
            "total_cost_usd": sum([m.cost_usd for m in metrics]),
            "by_provider": {
                "claude": len([m for m in metrics if m.provider == "claude"]),
                "ollama": len([m for m in metrics if m.provider == "ollama"])
            }
        }
```

---

## Testing

### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_claude_analysis():
    # Mock Claude response
    mock_response = Mock()
    mock_response.content = [Mock(text=json.dumps({
        "classification": {
            "type": "invoice",
            "confidence": 0.95,
            "reasoning": "Test"
        },
        "metadata": {
            "amount": 89.99,
            "currency": "EUR"
        },
        "action_items": []
    }))]
    
    with patch.object(anthropic.Anthropic, 'messages') as mock:
        mock.create.return_value = mock_response
        
        strategy = ClaudeStrategy()
        result = await strategy.analyze_document("Test invoice")
        
        assert result.classification.type == "invoice"
        assert result.classification.confidence == 0.95
        assert result.metadata.amount == 89.99
```

### Integration Tests
```python
@pytest.mark.integration
async def test_full_pipeline():
    # Upload test document
    with open("tests/fixtures/test_invoice.pdf", "rb") as f:
        response = await client.post(
            "/documents/upload",
            files={"file": f}
        )
    
    doc_id = response.json()["document_id"]
    
    # Wait for processing
    await asyncio.sleep(5)
    
    # Check result
    doc = await db.get_document(doc_id)
    assert doc.processing_status == "done"
    assert doc.type == "invoice"
    assert doc.metadata["amount"] == 89.99
    
    # Check tasks created
    tasks = await db.get_tasks(document_id=doc_id)
    assert len(tasks) >= 1
    assert "bezahlen" in tasks[0].title.lower()
```

---

## Future Enhancements

### Learning from Corrections
```python
class FeedbackLoop:
    async def learn_from_correction(
        self,
        document_id: UUID,
        original_analysis: DocumentAnalysis,
        corrected_data: dict
    ):
        """
        Store corrections to improve future analysis
        Future: Fine-tune model or adjust prompts
        """
        await db.save_correction(
            document_id=document_id,
            original=original_analysis.dict(),
            corrected=corrected_data,
            timestamp=datetime.now()
        )
        
        # TODO: Periodically analyze corrections and adjust prompts
```

### Multi-Language Support
```python
LANGUAGE_PROMPTS = {
    "de": GERMAN_ANALYSIS_PROMPT,
    "en": ENGLISH_ANALYSIS_PROMPT,
    "fr": FRENCH_ANALYSIS_PROMPT
}

async def analyze_document(text: str, language: str = "de"):
    prompt = LANGUAGE_PROMPTS.get(language, GERMAN_ANALYSIS_PROMPT)
    # ...
```

---

## Zusammenfassung

**AI Processor Features:**
- ✅ Multi-Provider Support (Claude, Ollama)
- ✅ Vision + Text Analysis
- ✅ Structured Output (JSON)
- ✅ Confidence Scoring
- ✅ Error Handling & Retry
- ✅ Cost Optimization
- ✅ Human-in-the-Loop
- ✅ Performance Tracking

**ADHD-Optimierung:**
- Schnelle Verarbeitung (< 5s)
- Hohe Genauigkeit (> 90%)
- Klare Validierung bei Unsicherheit
- Automatische Task-Erstellung