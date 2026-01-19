# Contributing Guidelines

## Welcome! 🎉

Thank you for your interest in contributing to Workmate Private! This project was created by a neurodivergent developer for the neurodivergent community, and we welcome all contributions that help make this tool better for everyone.

---

## Code of Conduct

### Our Values

- **Inclusivity:** Everyone is welcome, regardless of background or experience level
- **Empathy:** We understand ADHD and neurodivergence challenges
- **Collaboration:** "Miteinander statt führend" (Together rather than leading)
- **Pragmatism:** Solutions that work > Perfect solutions
- **Kindness:** Be kind to yourself and others

### Expected Behavior

✅ **Do:**
- Be respectful and constructive
- Assume good intentions
- Share your ADHD/neurodivergence experiences if relevant
- Ask questions - there are no "stupid" questions
- Help others when you can
- Give credit where it's due

❌ **Don't:**
- Use discriminatory or offensive language
- Shame people for mistakes or lack of knowledge
- Gatekeep or be elitist
- Be dismissive of ADHD-related struggles

---

## How to Contribute

### Ways to Contribute

You don't need to be a developer to contribute!

**Non-Code Contributions:**
- 📝 Improve documentation
- 🐛 Report bugs
- 💡 Suggest features
- 🎨 Design UI/UX improvements
- 🌍 Translate to other languages
- 📢 Share your experience using Workmate
- ⭐ Star the repository

**Code Contributions:**
- 🔧 Fix bugs
- ✨ Implement features
- 🧪 Write tests
- ⚡ Performance improvements
- 🔒 Security fixes

---

## Getting Started

### 1. Fork & Clone
```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/workmate-private.git
cd workmate-private

# Add upstream remote
git remote add upstream https://github.com/commanderphu/workmate-private.git
```

### 2. Create Branch
```bash
# Update main
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bugfix:
git checkout -b fix/bug-description
```

**Branch Naming Convention:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `chore/` - Maintenance

### 3. Make Changes
```bash
# Setup development environment
# See docs/development/setup.md

# Make your changes
# Test locally
# Commit with good messages
```

### 4. Commit

**Commit Message Format:**
```
<type>: <short summary>

<optional detailed description>

<optional footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Code style (formatting)
- `refactor:` - Refactoring
- `test:` - Tests
- `chore:` - Maintenance

**Examples:**
```
feat: add document scanner with OCR

Implements document scanning using camera or file upload.
Uses Tesseract OCR for text extraction.

Closes #42
```
```
fix: reminder not triggering for high priority tasks

The scheduler was skipping tasks with priority=high due to
a comparison bug. Fixed by correcting the priority enum order.

Fixes #89
```

### 5. Push & PR
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# Fill in the PR template
```

---

## Pull Request Process

### Before Submitting

**Checklist:**
- [ ] Code follows style guidelines (black, flake8)
- [ ] Tests added/updated
- [ ] Tests pass locally (`pytest`)
- [ ] Documentation updated if needed
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main
- [ ] No merge conflicts

### PR Template

When you create a PR, fill in:
```markdown
## Description
<!-- What does this PR do? Why? -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Related Issues
Closes #issue_number

## Testing
<!-- How did you test this? -->

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code formatted
```

### Review Process

1. **Automated Checks:** CI runs tests, linting
2. **Code Review:** Maintainer reviews code
3. **Feedback:** Address comments if any
4. **Approval:** PR gets approved
5. **Merge:** Maintainer merges

**Expected Timeline:**
- Initial review: 1-3 days
- Feedback rounds: as needed
- Merge: after approval

---

## Coding Standards

### Python (Backend)

**Style Guide:** PEP 8 + Black
```python
# Good
async def process_document(
    document_id: UUID,
    user_id: UUID,
    options: ProcessingOptions = None
) -> ProcessedDocument:
    """
    Process a document with AI analysis.
    
    Args:
        document_id: UUID of the document
        user_id: UUID of the user
        options: Optional processing options
    
    Returns:
        ProcessedDocument with analysis results
    
    Raises:
        DocumentNotFoundError: If document doesn't exist
        ProcessingError: If processing fails
    """
    doc = await db.get_document(document_id)
    
    if not doc:
        raise DocumentNotFoundError(f"Document {document_id} not found")
    
    return await ai_service.analyze(doc)
```

**Type Hints:**
```python
# Always use type hints
def calculate_priority(
    days_left: int,
    amount: float,
    doc_type: str
) -> TaskPriority:
    ...
```

**Async/Await:**
```python
# Use async for I/O operations
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

### Dart/Flutter (Frontend)

**Style Guide:** Effective Dart
```dart
// Good
class TaskCard extends StatelessWidget {
  final Task task;
  final VoidCallback onTap;
  
  const TaskCard({
    Key? key,
    required this.task,
    required this.onTap,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: Text(task.title),
        subtitle: Text(task.dueDate.toString()),
        onTap: onTap,
      ),
    );
  }
}
```

**Naming:**
```dart
// Classes: PascalCase
class DocumentScanner { }

// Variables/methods: camelCase
void processDocument() { }

// Constants: camelCase or lowerCamelCase
const apiUrl = 'http://localhost:8000';
```

### Testing

**Backend Tests:**
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "due_date": "2026-01-25T12:00:00Z"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        assert response.json()["title"] == "Test Task"
```

**Frontend Tests:**
```dart
testWidgets('TaskCard displays task title', (WidgetTester tester) async {
  final task = Task(
    id: '123',
    title: 'Test Task',
    dueDate: DateTime.now(),
  );
  
  await tester.pumpWidget(
    MaterialApp(
      home: TaskCard(
        task: task,
        onTap: () {},
      ),
    ),
  );
  
  expect(find.text('Test Task'), findsOneWidget);
});
```

---

## Documentation

### Code Comments

**When to comment:**
- ✅ Complex algorithms
- ✅ Non-obvious decisions
- ✅ ADHD-specific considerations
- ✅ Workarounds for bugs/limitations

**When NOT to comment:**
- ❌ Obvious code
- ❌ What the code does (code should be self-explanatory)

**Good:**
```python
# Calculate priority with ADHD bias towards urgency
# We weight time more heavily than amount because ADHD brains
# respond better to immediate deadlines than abstract importance
priority_score = (time_weight * 2) + amount_weight
```

**Bad:**
```python
# Add 1 to counter
counter += 1
```

### Docstrings

**Python:**
```python
def calculate_reminder_schedule(task: Task) -> List[ReminderEvent]:
    """
    Generate multi-stage reminder schedule for a task.
    
    Creates reminders with escalating frequency as deadline approaches:
    - 7 days: info (once)
    - 2 days: warning (daily)
    - 1 day: urgent (4x daily)
    - overdue: critical (hourly)
    
    Args:
        task: Task to create reminders for. Must have due_date set.
    
    Returns:
        List of ReminderEvent objects scheduled at appropriate times.
        Empty list if task has no due_date.
    
    Example:
        >>> task = Task(title="Pay rent", due_date=datetime.now() + timedelta(days=10))
        >>> reminders = calculate_reminder_schedule(task)
        >>> len(reminders)
        8  # 1 info + 5 warning + 4 urgent
    """
    ...
```

**Dart:**
```dart
/// Calculates the priority color for a task.
///
/// Returns different colors based on priority and due date:
/// - Critical: red
/// - High: orange
/// - Medium: yellow
/// - Low: green
///
/// Takes into account both the set priority and time until due date.
Color getPriorityColor(Task task) {
  ...
}
```

---

## ADHD-Friendly Contributing

### Take Your Time

- No pressure to finish quickly
- It's okay to take breaks
- Ask for help if stuck
- Start small, build confidence

### Communication Tips

**For Contributors:**
- Be clear about your availability
- It's okay to say "I can't finish this"
- Ask for clarification if confused
- Update the PR even if not done ("WIP" is fine)

**For Reviewers:**
- Be patient and constructive
- Explain *why*, not just *what*
- Offer alternatives, not just criticism
- Celebrate progress, not just completion

### Managing Context Switching

If you need to step away from a PR:
```markdown
## Status Update

I need to pause work on this PR for [reason].

**Current State:**
- ✅ Implemented X
- ⏳ Working on Y (50% done)
- ❌ Not started: Z

**Next Steps:**
1. Finish Y
2. Add tests for X and Y
3. Update docs

**Blockers:**
- Need clarification on [thing]

**Timeline:**
I'll be able to return to this [timeframe].
```

---

## Issue Reporting

### Bug Reports

**Template:**
```markdown
## Bug Description
Clear description of what's wrong

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.11]
- Version: [e.g. 0.1.0]

## Screenshots
If applicable

## Additional Context
Any other relevant info
```

### Feature Requests

**Template:**
```markdown
## Feature Description
What feature do you want?

## Problem it Solves
What problem does this solve?

## ADHD Context
How does this help ADHD users specifically?

## Proposed Solution
How might this work?

## Alternatives Considered
Other approaches you thought of

## Additional Context
Any other relevant info
```

---

## Recognition

### Contributors

All contributors are listed in:
- README.md
- CONTRIBUTORS.md
- Release notes

**Types of Recognition:**
- Code contributions
- Documentation
- Bug reports
- Feature ideas
- Community support

---

## Questions?

- **GitHub Discussions:** Ask anything
- **Issues:** For specific bugs/features
- **Discord:** (Coming soon)

---

## Thank You! ❤️

Every contribution, no matter how small, makes Workmate Private better for the ADHD community. Thank you for being part of this journey!

**Remember:** This project is by neurodivergent people, for neurodivergent people. Your perspective and experience are valuable. Don't hesitate to contribute!

---

**Happy Contributing! 🚀**