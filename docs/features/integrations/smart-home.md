# Smart Home Integration

## Overview

Die Smart Home Integration bringt Task-Reminders in die physische Welt. Statt nur digitaler Benachrichtigungen können Lichter blinken, Lautsprecher Ankündigungen machen und Displays Tasks anzeigen - perfekt für ADHD, wo physische Reize oft besser funktionieren als digitale.

---

## Supported Platforms

### 1. Home Assistant

**Warum Home Assistant?**
- ✅ Open Source & Privacy-focused
- ✅ 2000+ Integrations
- ✅ Lokales Hosting möglich
- ✅ Sehr aktive Community
- ✅ Flexible Automations

**Architecture:**
```
Workmate Private
    ↓ (REST API / Webhook)
Home Assistant
    ↓ (Integrations)
Smart Devices (Lights, Speakers, etc.)
```

**Implementation:**
```python
import aiohttp
from typing import Dict, Any

class HomeAssistantIntegration:
    def __init__(self, url: str, token: str):
        self.base_url = url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def call_service(
        self,
        domain: str,
        service: str,
        entity_id: str = None,
        data: Dict[str, Any] = None
    ):
        """Call a Home Assistant service"""
        
        url = f"{self.base_url}/api/services/{domain}/{service}"
        
        payload = data or {}
        if entity_id:
            payload["entity_id"] = entity_id
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                headers=self.headers
            ) as response:
                return await response.json()
    
    async def get_states(self, entity_id: str = None):
        """Get state of entity or all entities"""
        
        if entity_id:
            url = f"{self.base_url}/api/states/{entity_id}"
        else:
            url = f"{self.base_url}/api/states"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.json()
    
    async def trigger_automation(self, automation_id: str):
        """Trigger a Home Assistant automation"""
        
        return await self.call_service(
            domain="automation",
            service="trigger",
            entity_id=automation_id
        )
```

### 2. MQTT

**Warum MQTT?**
- ✅ Lightweight Protocol
- ✅ Pub/Sub Pattern
- ✅ Perfect für IoT
- ✅ Low Bandwidth
- ✅ Flexible Topics

**Implementation:**
```python
import paho.mqtt.client as mqtt
import json

class MQTTIntegration:
    def __init__(
        self,
        broker: str,
        port: int = 1883,
        username: str = None,
        password: str = None
    ):
        self.client = mqtt.Client()
        
        if username and password:
            self.client.username_pw_set(username, password)
        
        self.client.connect(broker, port)
        self.client.loop_start()
    
    def publish_reminder(
        self,
        task_title: str,
        severity: str,
        due_date: str
    ):
        """Publish reminder to MQTT topic"""
        
        topic = "workmate/reminders"
        
        payload = {
            "title": task_title,
            "severity": severity,
            "due_date": due_date,
            "timestamp": datetime.now().isoformat()
        }
        
        self.client.publish(
            topic,
            json.dumps(payload),
            qos=1,
            retain=False
        )
    
    def subscribe_to_actions(self, callback):
        """Subscribe to action topics (e.g., task completion)"""
        
        def on_message(client, userdata, msg):
            payload = json.loads(msg.payload.decode())
            callback(msg.topic, payload)
        
        self.client.on_message = on_message
        self.client.subscribe("workmate/actions/#")
```

---

## Use Cases

### 1. Critical Reminder: Blinking Lights

**Scenario:** Rechnung ist heute fällig, User ist zuhause

**Implementation:**
```python
class SmartHomeReminderService:
    async def send_critical_reminder_lights(
        self,
        task: Task,
        user: User
    ):
        """Flash lights red for critical reminders"""
        
        ha = self._get_home_assistant_integration(user)
        
        # Get user's configured light entities
        light_entities = user.smart_home_config.get('reminder_lights', [])
        
        for light in light_entities:
            # Turn on red
            await ha.call_service(
                domain="light",
                service="turn_on",
                entity_id=light,
                data={
                    "color_name": "red",
                    "brightness": 255
                }
            )
            
            await asyncio.sleep(1)
            
            # Turn off
            await ha.call_service(
                domain="light",
                service="turn_off",
                entity_id=light
            )
            
            await asyncio.sleep(0.5)
        
        # Repeat 3 times
        for _ in range(2):
            for light in light_entities:
                await ha.call_service("light", "turn_on", light, {"color_name": "red"})
                await asyncio.sleep(1)
                await ha.call_service("light", "turn_off", light)
                await asyncio.sleep(0.5)
```

### 2. Voice Announcement

**Scenario:** User ist im anderen Zimmer, Task wird fällig

**Implementation:**
```python
async def announce_reminder(
    self,
    task: Task,
    user: User
):
    """Announce reminder via smart speaker"""
    
    ha = self._get_home_assistant_integration(user)
    
    # Build message
    message = f"Erinnerung: {task.title}"
    
    if task.amount:
        message += f", Betrag: {task.amount:.2f} Euro"
    
    if task.due_date:
        hours_left = (task.due_date - datetime.now()).total_seconds() / 3600
        if hours_left < 24:
            message += f", fällig in {int(hours_left)} Stunden"
    
    # Send to TTS service
    await ha.call_service(
        domain="tts",
        service="google_translate_say",
        entity_id="media_player.wohnzimmer_speaker",
        data={
            "message": message,
            "language": "de"
        }
    )
```

### 3. Display Dashboard

**Scenario:** Smart Display zeigt offene Tasks

**Implementation:**
```python
async def update_task_display(
    self,
    user: User
):
    """Update smart display with current tasks"""
    
    ha = self._get_home_assistant_integration(user)
    
    # Get critical and high priority tasks
    tasks = await db.query(Task).filter(
        Task.user_id == user.id,
        Task.status == TaskStatus.OPEN,
        Task.priority.in_([TaskPriority.HIGH, TaskPriority.CRITICAL])
    ).order_by(Task.due_date).limit(5).all()
    
    # Build HTML for display
    html = self._build_task_dashboard_html(tasks)
    
    # Send to Home Assistant dashboard
    await ha.call_service(
        domain="browser_mod",
        service="navigate",
        data={
            "path": "/workmate-tasks",
            "browser_id": user.smart_home_config.get('display_browser_id')
        }
    )

def _build_task_dashboard_html(self, tasks: List[Task]) -> str:
    """Build HTML dashboard for tasks"""
    
    html = """
    <html>
    <head>
        <style>
            body { background: #1a1a1a; color: #fff; font-family: Arial; padding: 20px; }
            .task { background: #2a2a2a; margin: 10px 0; padding: 15px; border-radius: 8px; }
            .critical { border-left: 5px solid #ff0000; }
            .high { border-left: 5px solid #ff6600; }
            .title { font-size: 24px; font-weight: bold; }
            .meta { color: #aaa; margin-top: 5px; }
        </style>
    </head>
    <body>
        <h1>Wichtige Tasks</h1>
    """
    
    for task in tasks:
        priority_class = task.priority.value
        due_text = task.due_date.strftime('%d.%m %H:%M') if task.due_date else 'Kein Datum'
        
        html += f"""
        <div class="task {priority_class}">
            <div class="title">{task.title}</div>
            <div class="meta">Fällig: {due_text}</div>
        </div>
        """
    
    html += "</body></html>"
    return html
```

### 4. Presence-Based Reminders

**Scenario:** Nur erinnern wenn User zuhause ist

**Implementation:**
```python
async def should_send_smart_home_reminder(
    self,
    user: User
) -> bool:
    """Check if user is home before sending smart home reminder"""
    
    ha = self._get_home_assistant_integration(user)
    
    # Get user's presence sensor
    presence_entity = user.smart_home_config.get('presence_sensor')
    
    if not presence_entity:
        return True  # No sensor configured, send anyway
    
    # Check state
    state = await ha.get_states(presence_entity)
    
    return state.get('state') == 'home'
```

---

## Automation Examples

### Home Assistant Automation YAML
```yaml
# Workmate Critical Reminder Automation
automation:
  - alias: "Workmate: Critical Reminder"
    description: "Flash lights and announce when critical reminder received"
    
    trigger:
      - platform: webhook
        webhook_id: workmate_critical_reminder
    
    condition:
      - condition: state
        entity_id: person.joshua
        state: "home"
    
    action:
      # Flash office lights red 3 times
      - repeat:
          count: 3
          sequence:
            - service: light.turn_on
              target:
                entity_id: light.office
              data:
                color_name: red
                brightness: 255
            - delay: 1
            - service: light.turn_off
              target:
                entity_id: light.office
            - delay: 0.5
      
      # Announce via speaker
      - service: tts.google_translate_say
        data:
          entity_id: media_player.office_speaker
          message: "{{ trigger.json.message }}"
          language: "de"
      
      # Send notification to phone as backup
      - service: notify.mobile_app_joshua_phone
        data:
          title: "{{ trigger.json.title }}"
          message: "{{ trigger.json.message }}"
          data:
            priority: high
            channel: workmate_critical

# Morning Task Summary
  - alias: "Workmate: Morning Summary"
    description: "Announce today's tasks in the morning"
    
    trigger:
      - platform: time
        at: "07:30:00"
    
    condition:
      - condition: state
        entity_id: person.joshua
        state: "home"
      - condition: state
        entity_id: binary_sensor.workday
        state: "on"
    
    action:
      - service: rest_command.workmate_get_todays_tasks
      - service: tts.google_translate_say
        data:
          entity_id: media_player.bedroom_speaker
          message: >
            Guten Morgen! Du hast {{ states('sensor.workmate_tasks_today') }} Tasks für heute.
            {{ state_attr('sensor.workmate_tasks_today', 'summary') }}
```

### REST Commands in Home Assistant
```yaml
rest_command:
  workmate_get_todays_tasks:
    url: "https://workmate.local/api/v1/tasks/today"
    method: GET
    headers:
      Authorization: "Bearer YOUR_API_TOKEN"
    payload: ""
  
  workmate_complete_task:
    url: "https://workmate.local/api/v1/tasks/{{ task_id }}/complete"
    method: POST
    headers:
      Authorization: "Bearer YOUR_API_TOKEN"
```

---

## Configuration UI

### Flutter Settings Screen
```dart
class SmartHomeSettings extends StatefulWidget {
  @override
  _SmartHomeSettingsState createState() => _SmartHomeSettingsState();
}

class _SmartHomeSettingsState extends State<SmartHomeSettings> {
  String _homeAssistantUrl = '';
  String _homeAssistantToken = '';
  List<String> _selectedLights = [];
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Smart Home Integration')),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          // Home Assistant Setup
          Text('Home Assistant', style: Theme.of(context).textTheme.headline6),
          TextField(
            decoration: InputDecoration(labelText: 'URL (z.B. http://homeassistant.local:8123)'),
            value: _homeAssistantUrl,
            onChanged: (value) => setState(() => _homeAssistantUrl = value),
          ),
          TextField(
            decoration: InputDecoration(labelText: 'Access Token'),
            obscureText: true,
            onChanged: (value) => setState(() => _homeAssistantToken = value),
          ),
          ElevatedButton(
            onPressed: _testConnection,
            child: Text('Verbindung testen'),
          ),
          
          SizedBox(height: 20),
          
          // Light Selection
          Text('Reminder Lichter', style: Theme.of(context).textTheme.headline6),
          Text('Welche Lichter sollen für kritische Reminders blinken?'),
          FutureBuilder<List<String>>(
            future: _fetchAvailableLights(),
            builder: (context, snapshot) {
              if (!snapshot.hasData) return CircularProgressIndicator();
              
              return Column(
                children: snapshot.data!.map((light) => CheckboxListTile(
                  title: Text(light),
                  value: _selectedLights.contains(light),
                  onChanged: (selected) {
                    setState(() {
                      if (selected!) {
                        _selectedLights.add(light);
                      } else {
                        _selectedLights.remove(light);
                      }
                    });
                  },
                )).toList(),
              );
            },
          ),
          
          SizedBox(height: 20),
          
          // Test Button
          ElevatedButton(
            onPressed: _testReminder,
            child: Text('Test-Reminder senden'),
          ),
        ],
      ),
    );
  }
  
  Future<void> _testConnection() async {
    // Test Home Assistant connection
    try {
      final response = await http.get(
        Uri.parse('$_homeAssistantUrl/api/'),
        headers: {'Authorization': 'Bearer $_homeAssistantToken'},
      );
      
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('✅ Verbindung erfolgreich!'))
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('❌ Fehler: $e'))
      );
    }
  }
  
  Future<List<String>> _fetchAvailableLights() async {
    // Fetch available lights from Home Assistant
    // ...
  }
  
  Future<void> _testReminder() async {
    // Send test reminder
    await api.post('/smart-home/test-reminder');
  }
}
```

---

## Advanced Features

### Adaptive Reminders
```python
class AdaptiveSmartHomeReminder:
    async def send_reminder(
        self,
        task: Task,
        user: User
    ):
        """Send smart home reminder adapted to context"""
        
        ha = self._get_home_assistant_integration(user)
        
        # Check time of day
        now = datetime.now()
        
        if 22 <= now.hour or now.hour < 7:
            # Night time: Only critical, visual only (no sound)
            if task.priority == TaskPriority.CRITICAL:
                await self._send_silent_visual_reminder(task, user, ha)
        
        elif 7 <= now.hour < 9:
            # Morning: Gentle voice reminder
            await self._send_voice_reminder(task, user, ha, volume=0.3)
        
        elif 9 <= now.hour < 18:
            # Work hours: Visual + notification
            await self._send_visual_reminder(task, user, ha)
            await self._send_push_notification(task, user)
        
        elif 18 <= now.hour < 22:
            # Evening: Full experience (lights + voice)
            await self._send_full_reminder(task, user, ha)
```

### Room-Based Reminders
```python
async def send_room_based_reminder(
    self,
    task: Task,
    user: User
):
    """Send reminder to room where user currently is"""
    
    ha = self._get_home_assistant_integration(user)
    
    # Detect user's current room
    current_room = await self._detect_user_room(user, ha)
    
    if not current_room:
        # User not home or location unknown
        return
    
    # Get devices in that room
    room_config = user.smart_home_config.get('rooms', {}).get(current_room, {})
    
    # Send to devices in current room
    if 'lights' in room_config:
        await self._flash_lights(room_config['lights'], ha)
    
    if 'speaker' in room_config:
        await self._announce_on_speaker(task, room_config['speaker'], ha)

async def _detect_user_room(self, user: User, ha: HomeAssistantIntegration) -> str:
    """Detect which room user is currently in"""
    
    # Check motion sensors
    motion_sensors = user.smart_home_config.get('motion_sensors', {})
    
    for room, sensor in motion_sensors.items():
        state = await ha.get_states(sensor)
        if state.get('state') == 'on':
            # Motion detected in this room
            last_changed = state.get('last_changed')
            if (datetime.now() - last_changed).seconds < 300:  # Within last 5 minutes
                return room
    
    return None
```

---

## Security & Privacy

### Secure Token Storage
```python
from cryptography.fernet import Fernet

class SecureHomeAssistantConfig:
    def save_token(self, user_id: UUID, token: str, encryption_key: bytes):
        """Save Home Assistant token encrypted"""
        
        fernet = Fernet(encryption_key)
        encrypted_token = fernet.encrypt(token.encode()).decode()
        
        integration = Integration(
            user_id=user_id,
            integration_type="home_assistant",
            credentials_encrypted=encrypted_token
        )
        
        await db.save(integration)
    
    def get_token(self, user_id: UUID, encryption_key: bytes) -> str:
        """Get decrypted Home Assistant token"""
        
        integration = await db.query(Integration).filter(
            Integration.user_id == user_id,
            Integration.integration_type == "home_assistant"
        ).first()
        
        if not integration:
            return None
        
        fernet = Fernet(encryption_key)
        decrypted = fernet.decrypt(integration.credentials_encrypted.encode()).decode()
        
        return decrypted
```

### Local Network Only
```python
def validate_home_assistant_url(url: str) -> bool:
    """Ensure Home Assistant URL is local network only"""
    
    import ipaddress
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    # Check if it's a local IP
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private
    except ValueError:
        # Not an IP, check if it's .local domain
        return hostname.endswith('.local')
```

---

## Testing
```python
@pytest.mark.asyncio
async def test_home_assistant_integration():
    # Mock Home Assistant
    with aioresponses() as m:
        m.post(
            'http://homeassistant.local:8123/api/services/light/turn_on',
            payload={'state': 'ok'}
        )
        
        ha = HomeAssistantIntegration(
            url='http://homeassistant.local:8123',
            token='test_token'
        )
        
        result = await ha.call_service(
            domain='light',
            service='turn_on',
            entity_id='light.office',
            data={'color_name': 'red'}
        )
        
        assert result['state'] == 'ok'
```

---

## Zusammenfassung

**Smart Home Integration Features:**
- ✅ Home Assistant Support
- ✅ MQTT Protocol
- ✅ Blinking Lights
- ✅ Voice Announcements
- ✅ Smart Displays
- ✅ Presence Detection
- ✅ Room-Based Reminders
- ✅ Time-Adaptive Behavior

**ADHD-Benefit:**
- Physische Reize statt nur Screen
- Multisensorisch (Sehen + Hören)
- Im Raum präsent
- Schwerer zu ignorieren
- Kontextabhängig (Raum, Zeit)