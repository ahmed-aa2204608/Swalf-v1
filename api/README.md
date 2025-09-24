# 🎙️ AI Podcast Maker API

Generate professional Arabic podcasts with AI - from topic to audio. This API provides a complete pipeline for creating Arabic podcast content, including persona selection, content generation, cultural adaptation, script writing, and TTS audio generation.

## 🚀 Quick Start

### Development Setup

```bash
cd api
python -m venv venv

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run the API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints
- **Base URL**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Health Check**: `http://localhost:8000/health`

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/podcast
```

### Authentication
Currently no authentication required (proof of concept).

### Content Type
All endpoints expect and return `application/json` unless specified otherwise.

---

## 🔄 Workflow Overview

The AI Podcast Maker follows a sequential workflow:

1. **Submit Topic** → Get podcast ID
2. **Generate Personas** → Get host/guest suggestions  
3. **Confirm Personas** → Approve or modify personas
4. **Generate Content** → Create outlines with cultural adaptation
5. **Generate Script** → Create final dialogue script
6. **Generate Audio** → Convert script to MP3 audio
7. **Download Audio** → Get final podcast file

**Alternative**: Use the **Complete Pipeline** endpoint for automatic processing.

---

## 📋 Endpoints

### 1. Submit Topic

**`POST /api/podcast/submit-topic`**

Submit a podcast topic and create a new podcast session.

#### Request Body
```json
{
  "topic": "الذكاء الاصطناعي",
  "info": "مناقشة تطبيقات الذكاء الاصطناعي في التعليم والصحة",
  "file_content": null  // Optional: extracted PDF text
}
```

#### Response
```json
{
  "podcast_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "topic_submitted",
  "message": "Topic submitted successfully. Generating persona suggestions..."
}
```

#### Validation
- `topic`: 1-500 characters, required
- `info`: max 5000 characters, optional
- `file_content`: optional extracted PDF text

---

### 2. Submit Topic with File

**`POST /api/podcast/submit-topic-with-file`**

Submit topic with PDF file upload (form data).

#### Form Data
```
topic: "الطاقة المتجددة"
info: "معلومات إضافية عن الموضوع"
file: [PDF file] // Optional
```

#### Response
Same as submit-topic endpoint.

#### Notes
- Only PDF files accepted
- File content is automatically extracted and processed

---

### 3. Generate Personas

**`POST /api/podcast/generate-personas/{podcast_id}`**

Generate AI-suggested host and guest personas based on the topic.

#### Path Parameters
- `podcast_id`: UUID of the created podcast

#### Response
```json
{
  "podcast_id": "550e8400-e29b-41d4-a716-446655440000",
  "suggested_host": {
    "age": "Adult",
    "gender": "Male",
    "JobDescription": "أستاذ جامعي متخصص في الذكاء الاصطناعي",
    "SpeakingStyle": "أكاديمي ومتحمس للتعليم",
    "OCEAN_Persona": {
      "O": "High",
      "C": "High", 
      "E": "Medium",
      "A": "High",
      "N": "Low"
    }
  },
  "suggested_guest": {
    "age": "Adult",
    "gender": "Female",
    "JobDescription": "مطورة تطبيقات ذكية ومتخصصة في التعلم الآلي",
    "SpeakingStyle": "عملية ومتحدثة بوضوح",
    "OCEAN_Persona": {
      "O": "High",
      "C": "High",
      "E": "Low", 
      "A": "Medium",
      "N": "Medium"
    }
  },
  "classification": {
    "domain": "Technology",
    "style": "Educational",
    "sensitivity": "Low"
  }
}
```

---

### 4. Confirm Personas

**`POST /api/podcast/confirm-personas`**

Confirm or modify the suggested personas.

#### Request Body
```json
{
  "podcast_id": "550e8400-e29b-41d4-a716-446655440000",
  "host_persona": {
    "age": "Adult",
    "gender": "Male",
    "JobDescription": "أستاذ جامعي متخصص في الذكاء الاصطناعي",
    "SpeakingStyle": "أكاديمي ومتحمس للتعليم",
    "OCEAN_Persona": {
      "O": "High",
      "C": "High",
      "E": "Medium", 
      "A": "High",
      "N": "Low"
    }
  },
  "guest_persona": {
    // Same structure as host_persona
  }
}
```

#### Response
```json
{
  "message": "Personas confirmed successfully",
  "podcast_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 5. Generate Content

**`POST /api/podcast/generate-content/{podcast_id}`**

Generate podcast outline with persona and cultural adaptations.

#### Path Parameters
- `podcast_id`: UUID of the podcast

#### Response
```json
{
  "message": "Content generated successfully",
  "podcast_id": "550e8400-e29b-41d4-a716-446655440000",
  "outline": {
    "Intro1": {
      "description": "مقدمة ترحيبية للبرنامج",
      "script": ["نص المقدمة بالعربية"]
    },
    "Intro2": {
      "description": "تقديم الضيف والموضوع", 
      "script": ["نص تقديم الضيف"]
    },
    "Points": {
      "talking_points": {
        "النقطة الأولى": {
          "discussion": "محتوى النقاش",
          "questions": ["سؤال للضيف؟"],
          "response_hint": "توجيه الإجابة"
        }
      }
    },
    "Con": {
      "description": "خاتمة البرنامج",
      "script": ["نص الخاتمة"]
    }
  },
  "persona_outline": {
    // Enhanced outline with persona-specific content
  },
  "culture_outline": {
    // Culturally adapted outline for Arabic audience
  }
}
```

---

### 6. Generate Script

**`POST /api/podcast/generate-script/{podcast_id}`**

Generate final dialogue script with emotional markers.

#### Path Parameters
- `podcast_id`: UUID of the podcast

#### Response
```json
{
  "message": "Script generated successfully", 
  "podcast_id": "550e8400-e29b-41d4-a716-446655440000",
  "script": {
    "Intro1": "المقدم: أهلاً وسهلاً بكم <happy>\nالضيف: شكراً لكم <excited>",
    "Intro2": "المقدم: دعوني أرحب بضيفتنا الكريمة\nالضيف: سعيدة لوجودي معكم",
    "Points": {
      "talking_point_1": "حوار مفصل حول النقطة الأولى",
      "talking_point_2": "حوار مفصل حول النقطة الثانية"
    },
    "Con": "المقدم: في الختام، أشكركم على المتابعة\nالضيف: شكراً لكم على الاستضافة"
  }
}
```

#### Script Format
- **Speakers**: `المقدم:` (Host), `الضيف:` (Guest)
- **Emotions**: `<happy>`, `<excited>`, `<surprised>`, `<thoughtful>`
- **Language**: All content in Arabic

---

### 7. Generate Audio

**`POST /api/podcast/generate-audio/{podcast_id}`**

Convert script to MP3 audio using Edge TTS.

#### Path Parameters
- `podcast_id`: UUID of the podcast

#### Response
```json
{
  "podcast_id": "550e8400-e29b-41d4-a716-446655440000",
  "audio_file_path": "/path/to/podcast_20250918_221903_4893a162.mp3",
  "audio_duration_seconds": 180.5,
  "file_size_mb": 2.12
}
```

#### Audio Details
- **Format**: MP3, 16kHz
- **Voices**: Arabic Edge TTS voices
  - Host: `ar-SA-HamedNeural` (Male)
  - Guest: `ar-SA-ZariyahNeural` (Female)
- **Quality**: Broadcast quality with emotional prosody

---

### 8. Download Audio

**`GET /api/podcast/download-audio/{podcast_id}`**

Download the generated MP3 file.

#### Path Parameters
- `podcast_id`: UUID of the podcast

#### Response
- **Content-Type**: `audio/mpeg`
- **File**: MP3 audio file
- **Filename**: `podcast_{podcast_id}.mp3`

---

### 9. Get Status

**`GET /api/podcast/status/{podcast_id}`**

Get complete podcast status and all generated content.

#### Path Parameters
- `podcast_id`: UUID of the podcast

#### Response
```json
{
  "podcast_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "created_at": "2025-09-18T22:19:03Z",
  "updated_at": "2025-09-18T22:25:15Z", 
  "topic": "الذكاء الاصطناعي",
  "info": "مناقشة تطبيقات الذكاء الاصطناعي",
  "classification": {
    "domain": "Technology",
    "style": "Educational",
    "sensitivity": "Low"
  },
  "host_persona": { /* Full persona object */ },
  "guest_persona": { /* Full persona object */ },
  "outline": { /* Generated outline */ },
  "persona_outline": { /* Persona-enhanced outline */ },
  "culture_outline": { /* Culturally adapted outline */ },
  "script": { /* Final script */ },
  "audio_file_path": "/path/to/audio.mp3",
  "error_message": null
}
```

---

### 10. Complete Pipeline (Auto)

**`POST /api/podcast/complete-pipeline/{podcast_id}`**

Automatically execute the entire pipeline (background task).

#### Path Parameters
- `podcast_id`: UUID of the podcast (must be created first)

#### Response
```json
{
  "message": "Full pipeline started in background",
  "podcast_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Process
1. Generates personas automatically
2. Confirms suggested personas
3. Generates all content stages
4. Creates final script
5. Generates audio file

Use the status endpoint to monitor progress.

---

## 📊 Status Codes

| Status | Description |
|--------|-------------|
| `topic_submitted` | Topic received, ready for persona generation |
| `personas_suggested` | AI personas generated, waiting for confirmation |
| `personas_confirmed` | Personas approved, ready for content generation |
| `outline_generated` | Content outlines created |
| `script_generated` | Final script ready |
| `audio_generated` | MP3 audio file created |
| `completed` | Full podcast ready for download |
| `failed` | Error occurred, check error_message |

---

## ⚠️ Error Handling

### Common Error Responses

#### 404 Not Found
```json
{
  "detail": "Podcast with ID {podcast_id} not found"
}
```

#### 400 Bad Request
```json
{
  "detail": "Validation error: topic is required"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "AI service temporarily unavailable"
}
```

### Error Recovery
- Check the `/status/{podcast_id}` endpoint for `error_message`
- Most errors allow retry from the failed step
- For complete failures, restart with a new topic submission

---

## 📜 History Features

### Get Podcast History

**`GET /api/podcast/history`**

Retrieve a list of all podcast generation attempts with summary information.

#### Response
```json
[
  {
    "podcast_id": "550e8400-e29b-41d4-a716-446655440000",
    "topic": "الذكاء الاصطناعي",
    "status": "completed",
    "created_at": "2025-09-18T22:19:03Z",
    "audio_available": true,
    "error_message": null,
    "classification": {
      "domain": "Technology",
      "style": "Educational",
      "sensitivity": "Low"
    }
  },
  {
    "podcast_id": "660e8400-e29b-41d4-a716-446655440001",
    "topic": "الطاقة المتجددة",
    "status": "audio_generated",
    "created_at": "2025-09-18T23:15:00Z",
    "audio_available": true,
    "error_message": null,
    "classification": {
      "domain": "Science",
      "style": "Educational",
      "sensitivity": "Low"
    }
  }
]
```

### Frontend Implementation Guide

Here's how to implement the history feature in your frontend application:

#### 1. Fetch History List
```javascript
// Using Fetch API
async function fetchPodcastHistory() {
  try {
    const response = await fetch('http://localhost:8000/api/podcast/history');
    if (!response.ok) throw new Error('Failed to fetch history');
    const historyData = await response.json();
    
    // Sort by creation date (newest first)
    historyData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    // Render in your UI
    displayHistory(historyData);
  } catch (error) {
    console.error('Error fetching history:', error);
    showErrorMessage('Failed to load podcast history');
  }
}

// Example display function
function displayHistory(historyData) {
  const historyList = document.getElementById('history-list');
  historyList.innerHTML = historyData.map(item => `
    <div class="history-item ${item.status}">
      <h3>${item.topic}</h3>
      <p>Status: ${formatStatus(item.status)}</p>
      <p>Created: ${formatDate(item.created_at)}</p>
      ${item.audio_available ? 
        `<button onclick="downloadPodcast('${item.podcast_id}')">Download Audio</button>` : 
        ''
      }
      <button onclick="viewDetails('${item.podcast_id}')">View Details</button>
    </div>
  `).join('');
}
```

#### 2. View Detailed Information
```javascript
// Fetch and display detailed podcast information
async function viewDetails(podcastId) {
  try {
    const response = await fetch(`http://localhost:8000/api/podcast/status/${podcastId}`);
    if (!response.ok) throw new Error('Failed to fetch podcast details');
    const details = await response.json();
    
    // Display detailed information
    showPodcastDetails(details);
  } catch (error) {
    console.error('Error fetching details:', error);
    showErrorMessage('Failed to load podcast details');
  }
}

// Example details display
function showPodcastDetails(details) {
  const detailsModal = document.getElementById('details-modal');
  detailsModal.innerHTML = `
    <div class="podcast-details">
      <h2>${details.topic}</h2>
      <p>${details.info || 'No additional information'}</p>
      
      <h3>Classification</h3>
      <ul>
        <li>Domain: ${details.classification?.domain}</li>
        <li>Style: ${details.classification?.style}</li>
        <li>Sensitivity: ${details.classification?.sensitivity}</li>
      </ul>
      
      <h3>Personas</h3>
      <div class="personas">
        <div class="host">
          <h4>Host</h4>
          <pre>${JSON.stringify(details.host_persona, null, 2)}</pre>
        </div>
        <div class="guest">
          <h4>Guest</h4>
          <pre>${JSON.stringify(details.guest_persona, null, 2)}</pre>
        </div>
      </div>
      
      ${details.error_message ? 
        `<div class="error-message">Error: ${details.error_message}</div>` : 
        ''
      }
    </div>
  `;
  detailsModal.style.display = 'block';
}
```

#### 3. Download Audio Files
```javascript
// Download podcast audio
async function downloadPodcast(podcastId) {
  try {
    // Trigger download using the audio endpoint
    const response = await fetch(`http://localhost:8000/api/podcast/download-audio/${podcastId}`);
    if (!response.ok) throw new Error('Failed to download audio');
    
    // Convert response to blob
    const blob = await response.blob();
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `podcast_${podcastId}.mp3`;
    document.body.appendChild(a);
    a.click();
    
    // Cleanup
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (error) {
    console.error('Error downloading audio:', error);
    showErrorMessage('Failed to download audio file');
  }
}
```

#### 4. CSS Styling Example
```css
.history-item {
  border: 1px solid #ddd;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 5px;
}

.history-item.completed {
  border-left: 5px solid #4CAF50;
}

.history-item.failed {
  border-left: 5px solid #f44336;
}

.history-item button {
  margin: 5px;
  padding: 8px 15px;
  border-radius: 4px;
}

.podcast-details {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.error-message {
  color: #f44336;
  padding: 10px;
  margin: 10px 0;
  background: #ffebee;
  border-radius: 4px;
}
```

#### 5. Error Handling and Status Updates
```javascript
// Format status for display
function formatStatus(status) {
  const statusMap = {
    'topic_submitted': 'Topic Submitted',
    'personas_suggested': 'Personas Suggested',
    'personas_confirmed': 'Personas Confirmed',
    'outline_generated': 'Outline Generated',
    'script_generated': 'Script Generated',
    'audio_generated': 'Audio Generated',
    'completed': 'Completed',
    'failed': 'Failed'
  };
  return statusMap[status] || status;
}

// Poll for status updates if podcast is processing
function pollStatus(podcastId) {
  const interval = setInterval(async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/podcast/status/${podcastId}`);
      const data = await response.json();
      
      updateStatusDisplay(data);
      
      if (['completed', 'failed'].includes(data.status)) {
        clearInterval(interval);
        if (data.status === 'completed') {
          showSuccessMessage('Podcast generation completed!');
        }
      }
    } catch (error) {
      console.error('Error polling status:', error);
      clearInterval(interval);
    }
  }, 5000); // Poll every 5 seconds
}
```

#### Usage Tips
1. **Initial Load**: Call `fetchPodcastHistory()` when your history page loads.
2. **Auto-refresh**: Consider refreshing the history list periodically or after new podcast creation.
3. **Error States**: Always handle error states and display appropriate messages to users.
4. **Loading States**: Show loading indicators during fetch operations.
5. **Responsive Design**: Ensure your history list is responsive and works well on mobile devices.

---

## 📜 History Features

### Get Podcast History

**`GET /api/podcast/history`**

Retrieve a list of all podcast generation attempts with summary information.

#### Response Example

```json
[
  {
    "podcast_id": "550e8400-e29b-41d4-a716-446655440000",
    "topic": "الذكاء الاصطناعي",
    "status": "completed",
    "created_at": "2025-09-18T22:19:03Z",
    "audio_available": true,
    "error_message": null,
    "classification": {
      "domain": "Technology",
      "style": "Educational",
      "sensitivity": "Low"
    }
  },
  {
    "podcast_id": "660e8400-e29b-41d4-a716-446655440001",
    "topic": "الطاقة المتجددة",
    "status": "audio_generated",
    "created_at": "2025-09-18T23:15:00Z",
    "audio_available": true,
    "error_message": null,
    "classification": {
      "domain": "Science",
      "style": "Educational",
      "sensitivity": "Low"
    }
  }
]
```

### Frontend Implementation Guide

Here's how to implement the history feature in your frontend application:

#### 1. Fetch History List

```javascript
// Using Fetch API
async function fetchPodcastHistory() {
  try {
    const response = await fetch('http://localhost:8000/api/podcast/history');
    if (!response.ok) throw new Error('Failed to fetch history');
    const historyData = await response.json();
    
    // Sort by creation date (newest first)
    historyData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    // Render in your UI
    displayHistory(historyData);
  } catch (error) {
    console.error('Error fetching history:', error);
    showErrorMessage('Failed to load podcast history');
  }
}

// Example display function
function displayHistory(historyData) {
  const historyList = document.getElementById('history-list');
  historyList.innerHTML = historyData.map(item => `
    <div class="history-item ${item.status}">
      <h3>${item.topic}</h3>
      <p>Status: ${formatStatus(item.status)}</p>
      <p>Created: ${formatDate(item.created_at)}</p>
      ${item.audio_available ? 
        `<button onclick="downloadPodcast('${item.podcast_id}')">Download Audio</button>` : 
        ''
      }
      <button onclick="viewDetails('${item.podcast_id}')">View Details</button>
    </div>
  `).join('');
}
```

#### 2. View Detailed Information

```javascript
// Fetch and display detailed podcast information
async function viewDetails(podcastId) {
  try {
    const response = await fetch(`http://localhost:8000/api/podcast/status/${podcastId}`);
    if (!response.ok) throw new Error('Failed to fetch podcast details');
    const details = await response.json();
    
    // Display detailed information
    showPodcastDetails(details);
  } catch (error) {
    console.error('Error fetching details:', error);
    showErrorMessage('Failed to load podcast details');
  }
}

// Example details display
function showPodcastDetails(details) {
  const detailsModal = document.getElementById('details-modal');
  detailsModal.innerHTML = `
    <div class="podcast-details">
      <h2>${details.topic}</h2>
      <p>${details.info || 'No additional information'}</p>
      
      <h3>Classification</h3>
      <ul>
        <li>Domain: ${details.classification?.domain}</li>
        <li>Style: ${details.classification?.style}</li>
        <li>Sensitivity: ${details.classification?.sensitivity}</li>
      </ul>
      
      <h3>Personas</h3>
      <div class="personas">
        <div class="host">
          <h4>Host</h4>
          <pre>${JSON.stringify(details.host_persona, null, 2)}</pre>
        </div>
        <div class="guest">
          <h4>Guest</h4>
          <pre>${JSON.stringify(details.guest_persona, null, 2)}</pre>
        </div>
      </div>
      
      ${details.error_message ? 
        `<div class="error-message">Error: ${details.error_message}</div>` : 
        ''
      }
    </div>
  `;
  detailsModal.style.display = 'block';
}
```

#### 3. Download Audio Files

```javascript
// Download podcast audio
async function downloadPodcast(podcastId) {
  try {
    // Trigger download using the audio endpoint
    const response = await fetch(`http://localhost:8000/api/podcast/download-audio/${podcastId}`);
    if (!response.ok) throw new Error('Failed to download audio');
    
    // Convert response to blob
    const blob = await response.blob();
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `podcast_${podcastId}.mp3`;
    document.body.appendChild(a);
    a.click();
    
    // Cleanup
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (error) {
    console.error('Error downloading audio:', error);
    showErrorMessage('Failed to download audio file');
  }
}
```

#### 4. CSS Styling Example

```css
.history-item {
  border: 1px solid #ddd;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 5px;
}

.history-item.completed {
  border-left: 5px solid #4CAF50;
}

.history-item.failed {
  border-left: 5px solid #f44336;
}

.history-item button {
  margin: 5px;
  padding: 8px 15px;
  border-radius: 4px;
}

.podcast-details {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.error-message {
  color: #f44336;
  padding: 10px;
  margin: 10px 0;
  background: #ffebee;
  border-radius: 4px;
}
```

#### 5. Error Handling and Status Updates

```javascript
// Format status for display
function formatStatus(status) {
  const statusMap = {
    'topic_submitted': 'Topic Submitted',
    'personas_suggested': 'Personas Suggested',
    'personas_confirmed': 'Personas Confirmed',
    'outline_generated': 'Outline Generated',
    'script_generated': 'Script Generated',
    'audio_generated': 'Audio Generated',
    'completed': 'Completed',
    'failed': 'Failed'
  };
  return statusMap[status] || status;
}

// Poll for status updates if podcast is processing
function pollStatus(podcastId) {
  const interval = setInterval(async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/podcast/status/${podcastId}`);
      const data = await response.json();
      
      updateStatusDisplay(data);
      
      if (['completed', 'failed'].includes(data.status)) {
        clearInterval(interval);
        if (data.status === 'completed') {
          showSuccessMessage('Podcast generation completed!');
        }
      }
    } catch (error) {
      console.error('Error polling status:', error);
      clearInterval(interval);
    }
  }, 5000); // Poll every 5 seconds
}
```

#### Usage Tips

1. **Initial Load**: Call `fetchPodcastHistory()` when your history page loads.
2. **Auto-refresh**: Consider refreshing the history list periodically or after new podcast creation.
3. **Error States**: Always handle error states and display appropriate messages to users.
4. **Loading States**: Show loading indicators during fetch operations.
5. **Responsive Design**: Ensure your history list is responsive and works well on mobile devices.

---

## 🧪 Testing Examples

### JavaScript/Fetch
```javascript
// Submit topic
const response = await fetch('http://localhost:8000/api/podcast/submit-topic', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    topic: 'الذكاء الاصطناعي',
    info: 'مناقشة شاملة حول تطبيقات الذكاء الاصطناعي'
  })
});
const data = await response.json();
console.log('Podcast ID:', data.podcast_id);

// Run complete pipeline
await fetch(`http://localhost:8000/api/podcast/complete-pipeline/${data.podcast_id}`, {
  method: 'POST'
});

// Monitor status
const statusResponse = await fetch(`http://localhost:8000/api/podcast/status/${data.podcast_id}`);
const status = await statusResponse.json();
console.log('Status:', status.status);
```

### Python/Requests
```python
import requests
import time

# Submit topic
response = requests.post('http://localhost:8000/api/podcast/submit-topic', json={
    'topic': 'الطاقة المتجددة',
    'info': 'أهمية الطاقة المتجددة في المستقبل'
})
podcast_id = response.json()['podcast_id']

# Run complete pipeline
requests.post(f'http://localhost:8000/api/podcast/complete-pipeline/{podcast_id}')

# Wait and check status
while True:
    status_response = requests.get(f'http://localhost:8000/api/podcast/status/{podcast_id}')
    status_data = status_response.json()
    
    if status_data['status'] == 'completed':
        print("Podcast ready!")
        # Download audio
        audio_response = requests.get(f'http://localhost:8000/api/podcast/download-audio/{podcast_id}')
        with open(f'podcast_{podcast_id}.mp3', 'wb') as f:
            f.write(audio_response.content)
        break
    elif status_data['status'] == 'failed':
        print(f"Error: {status_data['error_message']}")
        break
    
    time.sleep(10)  # Check every 10 seconds
```

### cURL Examples
```bash
# Submit topic
curl -X POST "http://localhost:8000/api/podcast/submit-topic" \
  -H "Content-Type: application/json" \
  -d '{"topic": "الذكاء الاصطناعي", "info": "مناقشة شاملة"}'

# Get status
curl -X GET "http://localhost:8000/api/podcast/status/{podcast_id}"

# Download audio
curl -X GET "http://localhost:8000/api/podcast/download-audio/{podcast_id}" \
  --output podcast.mp3
```

---

## 🔧 Technical Details

### Dependencies
- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM  
- **Pydantic**: Data validation
- **Edge TTS**: Arabic text-to-speech
- **sentence-transformers**: Persona matching
- **Neon PostgreSQL**: Database backend

### Performance
- Typical pipeline time: 2-5 minutes
- Audio generation: ~30 seconds per minute of content
- File sizes: 1-5 MB per 3-5 minute podcast
- Concurrent requests: Supported via background tasks

### Arabic Language Support
- Full RTL text processing
- Cultural adaptation for MENA audiences  
- Native Arabic personas and speaking styles
- Professional Arabic TTS voices
- Emotional prosody and natural dialogue flow

---

## 🚀 Production Deployment

### Environment Variables
Create `.env` file with:
```
DATABASE_URL=postgresql://user:pass@host/db
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
AZURE_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=your_endpoint
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Considerations
- Add authentication middleware for production
- Configure CORS for your frontend domain
- Use HTTPS in production
- Implement rate limiting
- Secure database credentials

---

## 📞 Support

For questions or issues:
- Check the interactive docs at `/docs`
- Review error messages in status responses
- Ensure all required fields are provided
- Verify database connectivity

**Happy podcasting! 🎙️✨**
