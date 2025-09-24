// AI Podcast Maker Frontend JavaScript
// Automatically detect the API base URL from current page
const currentPort = window.location.port || (window.location.protocol === 'https:' ? '443' : '80');
const currentHost = window.location.hostname;
let API_BASE = `http://${currentHost}:${currentPort}/api/podcast`;

console.log('🌐 Detected API_BASE:', API_BASE);

let currentPodcastId = null;
let suggestedHost = null;
let suggestedGuest = null;

// Utility Functions
function log(message, type = 'info') {
    const logElement = document.getElementById('debug-log');
    const timestamp = new Date().toLocaleTimeString();
    const color = type === 'error' ? '#ff6b6b' : type === 'success' ? '#00c851' : '#00ff00';
    logElement.innerHTML += `<div style="color: ${color}">[${timestamp}] ${message}</div>`;
    logElement.scrollTop = logElement.scrollHeight;
}

function clearLog() {
    document.getElementById('debug-log').innerHTML = 'Log cleared...';
}

function showLoading(elementId, show = true) {
    const element = document.getElementById(elementId);
    if (show) {
        element.classList.remove('hidden');
    } else {
        element.classList.add('hidden');
    }
}

function updateProgress(percentage) {
    document.getElementById('progress').style.width = percentage + '%';
}

function showStep(stepNumber) {
    // Hide all steps
    for (let i = 1; i <= 4; i++) {
        document.getElementById(`step${i}`).classList.add('hidden');
        document.getElementById(`step${i}`).classList.remove('active');
    }
    
    // Show and activate the specified step
    const targetStep = document.getElementById(`step${stepNumber}`);
    targetStep.classList.remove('hidden');
    targetStep.classList.add('active');
}

function markStepCompleted(stepNumber) {
    const step = document.getElementById(`step${stepNumber}`);
    step.classList.add('completed');
    step.classList.remove('active');
}

function markStepError(stepNumber) {
    const step = document.getElementById(`step${stepNumber}`);
    step.classList.add('error');
    step.classList.remove('active');
}

// Step 1: Topic Submission
async function submitTopic() {
    log('🔄 submitTopic function started');
    
    const topic = document.getElementById('topic').value.trim();
    const info = document.getElementById('info').value.trim();
    const pdfFile = document.getElementById('pdfFile').files[0];
    
    log('📝 Getting submit button...');
    const submitButton = document.querySelector('button[onclick="submitTopic()"]');
    
    if (!submitButton) {
        log('❌ Submit button not found!', 'error');
        alert('Error: Submit button not found');
        return;
    }
    
    log('✅ Submit button found');

    log('📝 Topic validation starting...');
    
    if (!topic) {
        log('❌ No topic provided', 'error');
        alert('Please enter a topic');
        return;
    }

    log('📝 Topic validation passed: ' + topic);

    // Disable button to prevent multiple clicks
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="loading"></span> Submitting...';
    
    showLoading('submit-loading', true);
    log('Submitting topic: ' + topic);

    try {
        let response;
        const apiUrl = window.API_BASE || API_BASE;
        log('🌐 Using API URL: ' + apiUrl);
        
        // Add a simple test request first
        log('🧪 Testing API connection...');
        try {
            const testResponse = await fetch(`${apiUrl.replace('/api/podcast', '')}/health`);
            log('🧪 API test response status: ' + testResponse.status);
        } catch (testError) {
            log('❌ API test failed: ' + testError.message, 'error');
        }
        
        if (pdfFile) {
            log('📄 Submitting with PDF file: ' + pdfFile.name);
            // Submit with file
            const formData = new FormData();
            formData.append('topic', topic);
            formData.append('info', info);
            formData.append('file', pdfFile);

            log('🔄 Making request to: ' + apiUrl + '/submit-topic-with-file');
            response = await fetch(`${apiUrl}/submit-topic-with-file`, {
                method: 'POST',
                body: formData
            });
        } else {
            log('📝 Submitting without file');
            // Submit without file
            const requestBody = { topic, info };
            log('🔄 Making request to: ' + apiUrl + '/submit-topic');
            log('📤 Request body: ' + JSON.stringify(requestBody));
            
            response = await fetch(`${apiUrl}/submit-topic`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
        }

        log('📥 Received response, status: ' + response.status);

        // Check if response is ok
        if (!response.ok) {
            const errorText = await response.text();
            log('❌ Response not ok: ' + errorText, 'error');
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        log('🔄 Parsing response JSON...');
        const data = await response.json();
        log('✅ Response parsed successfully: ' + JSON.stringify(data), 'success');
        
        currentPodcastId = data.podcast_id;
        log(`✅ Topic submitted successfully! ID: ${currentPodcastId}`, 'success');
        
        // Update UI
        log('🔄 Updating UI elements...');
        document.getElementById('current-podcast-id').textContent = currentPodcastId;
        document.getElementById('podcast-id-display').classList.remove('hidden');
        
        log('🔄 Marking step 1 as completed...');
        markStepCompleted(1);
        log('🔄 Showing step 2...');
        showStep(2);
        
        log('🔄 Updating status...');
        updateStatus(`Topic submitted: ${topic}`);
        log('✅ submitTopic completed successfully!', 'success');
        
    } catch (error) {
        log(`❌ Error in submitTopic: ${error.message}`, 'error');
        log(`❌ Error stack: ${error.stack}`, 'error');
        markStepError(1);
        alert(`Error submitting topic: ${error.message}`);
        
    } finally {
        log('🔄 Finally block: Re-enabling submit button...');
        // Re-enable button
        submitButton.disabled = false;
        submitButton.innerHTML = 'Submit Topic';
        showLoading('submit-loading', false);
        log('✅ Submit button re-enabled');
    }
}

// Step 2: Generate Personas
async function generatePersonas() {
    if (!currentPodcastId) {
        alert('Please submit a topic first');
        return;
    }

    showLoading('personas-loading', true);
    log('Generating persona suggestions...');

    try {
        const response = await fetch(`${API_BASE}/generate-personas/${currentPodcastId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            suggestedHost = data.suggested_host;
            suggestedGuest = data.suggested_guest;
            
            log('✅ Personas generated successfully!', 'success');
            displayPersonas(data.suggested_host, data.suggested_guest, data.classification);
            
            document.getElementById('confirm-personas-btn').classList.remove('hidden');
            
        } else {
            throw new Error(data.detail || 'Failed to generate personas');
        }
    } catch (error) {
        log(`❌ Error: ${error.message}`, 'error');
        markStepError(2);
    } finally {
        showLoading('personas-loading', false);
    }
}

function displayPersonas(host, guest, classification) {
    const container = document.getElementById('persona-suggestions');
    
    container.innerHTML = `
        <div class="grid">
            <div class="persona-card selected">
                <h4>🎙️ Host</h4>
                <p><strong>Job:</strong> ${host.JobDescription}</p>
                <p><strong>Style:</strong> ${host.SpeakingStyle}</p>
                <p><strong>Age:</strong> ${host.age} | <strong>Gender:</strong> ${host.gender}</p>
                <p><strong>Personality:</strong> E=${host.OCEAN_Persona.E}, O=${host.OCEAN_Persona.O}</p>
            </div>
            <div class="persona-card selected">
                <h4>🎤 Guest</h4>
                <p><strong>Job:</strong> ${guest.JobDescription}</p>
                <p><strong>Style:</strong> ${guest.SpeakingStyle}</p>
                <p><strong>Age:</strong> ${guest.age} | <strong>Gender:</strong> ${guest.gender}</p>
                <p><strong>Personality:</strong> E=${guest.OCEAN_Persona.E}, O=${guest.OCEAN_Persona.O}</p>
            </div>
        </div>
        <div style="margin-top: 15px; padding: 15px; background: #f0f8ff; border-radius: 8px;">
            <h4>📊 Classification</h4>
            <p><strong>Domain:</strong> ${classification.domain}</p>
            <p><strong>Style:</strong> ${classification.style}</p>
            <p><strong>Sensitivity:</strong> ${classification.sensitivity}</p>
        </div>
    `;
}

async function confirmPersonas() {
    if (!currentPodcastId || !suggestedHost || !suggestedGuest) {
        alert('Please generate personas first');
        return;
    }

    log('Confirming persona selection...');

    try {
        const response = await fetch(`${API_BASE}/confirm-personas`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                podcast_id: currentPodcastId,
                host_persona: suggestedHost,
                guest_persona: suggestedGuest
            })
        });

        const data = await response.json();

        if (response.ok) {
            log('✅ Personas confirmed!', 'success');
            markStepCompleted(2);
            showStep(3);
            updateStatus('Personas confirmed, ready to generate content');
        } else {
            throw new Error(data.detail || 'Failed to confirm personas');
        }
    } catch (error) {
        log(`❌ Error: ${error.message}`, 'error');
        markStepError(2);
    }
}

// Step 3: Generate Content
async function generateContent() {
    if (!currentPodcastId) {
        alert('Please complete previous steps first');
        return;
    }

    showLoading('content-loading', true);
    log('Generating content (outline, persona enhancement, cultural context)...');
    updateProgress(10);

    try {
        // Generate content (outline + enhancements)
        const contentResponse = await fetch(`${API_BASE}/generate-content/${currentPodcastId}`, {
            method: 'POST'
        });

        if (!contentResponse.ok) {
            throw new Error('Failed to generate content');
        }

        log('✅ Content generated!', 'success');
        updateProgress(50);
        
        // Generate script
        log('Generating script...');
        const scriptResponse = await fetch(`${API_BASE}/generate-script/${currentPodcastId}`, {
            method: 'POST'
        });

        if (!scriptResponse.ok) {
            throw new Error('Failed to generate script');
        }

        log('✅ Script generated!', 'success');
        updateProgress(100);
        
        document.getElementById('generation-status').innerHTML = '✅ Content and script generated successfully!';
        markStepCompleted(3);
        showStep(4);
        
        updateStatus('Content and script ready, ready for audio generation');

    } catch (error) {
        log(`❌ Error: ${error.message}`, 'error');
        markStepError(3);
        document.getElementById('generation-status').innerHTML = `❌ Error: ${error.message}`;
    } finally {
        showLoading('content-loading', false);
    }
}

// Step 4: Generate Audio
async function generateAudio() {
    if (!currentPodcastId) {
        alert('Please complete previous steps first');
        return;
    }

    showLoading('audio-loading', true);
    log('Generating TTS audio... This may take a few minutes.');
    document.getElementById('audio-status').innerHTML = '🎵 Generating audio... Please wait...';

    try {
        const response = await fetch(`${API_BASE}/generate-audio/${currentPodcastId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            log('✅ Audio generated successfully!', 'success');
            document.getElementById('audio-status').innerHTML = '✅ Audio generation completed!';
            
            // Show audio player
            const audioPlayer = document.getElementById('audio-player');
            const audioSource = document.getElementById('audio-source');
            audioSource.src = `${API_BASE.replace('/api/podcast', '')}/api/podcast/download-audio/${currentPodcastId}`;
            audioPlayer.classList.remove('hidden');
            
            markStepCompleted(4);
            updateStatus('Podcast completed! Audio ready for download.');
            
        } else {
            throw new Error(data.detail || 'Failed to generate audio');
        }
    } catch (error) {
        log(`❌ Error: ${error.message}`, 'error');
        markStepError(4);
        document.getElementById('audio-status').innerHTML = `❌ Error: ${error.message}`;
    } finally {
        showLoading('audio-loading', false);
    }
}

function downloadAudio() {
    if (!currentPodcastId) {
        alert('No audio available');
        return;
    }
    
    const downloadUrl = `${API_BASE}/download-audio/${currentPodcastId}`;
    window.open(downloadUrl, '_blank');
    log('📥 Downloading audio file...', 'success');
}

// Auto-complete pipeline
async function runFullPipeline() {
    if (!currentPodcastId) {
        alert('Please submit a topic first');
        return;
    }

    log('🚀 Starting full pipeline automation...');
    
    try {
        const response = await fetch(`${API_BASE}/complete-pipeline/${currentPodcastId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            log('✅ Full pipeline started! Monitoring progress...', 'success');
            
            // Start monitoring
            monitorPipeline();
        } else {
            throw new Error(data.detail || 'Failed to start pipeline');
        }
    } catch (error) {
        log(`❌ Error: ${error.message}`, 'error');
    }
}

// Pipeline monitoring
async function monitorPipeline() {
    const statusElement = document.getElementById('generation-status');
    let checkCount = 0;
    const maxChecks = 60; // Max 5 minutes of monitoring
    
    const monitor = setInterval(async () => {
        checkCount++;
        
        try {
            const response = await fetch(`${API_BASE}/status/${currentPodcastId}`);
            const data = await response.json();
            
            if (response.ok) {
                const status = data.status;
                log(`Status: ${status}`);
                
                updateStatus(`Pipeline Status: ${status}`);
                
                // Update progress based on status
                const statusProgress = {
                    'topic_submitted': 10,
                    'personas_suggested': 20,
                    'personas_confirmed': 30,
                    'outline_generated': 60,
                    'script_generated': 80,
                    'audio_generated': 95,
                    'completed': 100
                };
                
                updateProgress(statusProgress[status] || 0);
                
                if (status === 'completed') {
                    clearInterval(monitor);
                    log('🎉 Pipeline completed successfully!', 'success');
                    statusElement.innerHTML = '🎉 Full pipeline completed!';
                    
                    // Show audio player
                    const audioPlayer = document.getElementById('audio-player');
                    const audioSource = document.getElementById('audio-source');
                    audioSource.src = `${API_BASE.replace('/api/podcast', '')}/api/podcast/download-audio/${currentPodcastId}`;
                    audioPlayer.classList.remove('hidden');
                    
                    markStepCompleted(4);
                } else if (status === 'failed') {
                    clearInterval(monitor);
                    log(`❌ Pipeline failed: ${data.error_message}`, 'error');
                    statusElement.innerHTML = `❌ Pipeline failed: ${data.error_message}`;
                    markStepError(3);
                }
            }
        } catch (error) {
            log(`❌ Status check error: ${error.message}`, 'error');
        }
        
        if (checkCount >= maxChecks) {
            clearInterval(monitor);
            log('⏰ Monitoring timeout reached', 'error');
        }
    }, 5000); // Check every 5 seconds
}

// Status functions
async function checkStatus() {
    if (!currentPodcastId) {
        log('No podcast ID available');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/status/${currentPodcastId}`);
        const data = await response.json();

        if (response.ok) {
            updateStatus(`Status: ${data.status} (Updated: ${new Date(data.updated_at).toLocaleString()})`);
            log(`📊 Status check: ${data.status}`, 'success');
            
            // Log detailed info
            if (data.classification) {
                log(`Domain: ${data.classification.domain}, Style: ${data.classification.style}`);
            }
            if (data.audio_file_path) {
                log(`Audio file: ${data.audio_file_path}`);
            }
        } else {
            throw new Error(data.detail || 'Failed to get status');
        }
    } catch (error) {
        log(`❌ Status error: ${error.message}`, 'error');
    }
}

function updateStatus(message) {
    document.getElementById('current-status').innerHTML = `
        <span class="status-indicator status-processing">${message}</span>
    `;
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    log('🎙️ AI Podcast Maker initialized');
    log('Enter a topic in Arabic to get started!');
    
    // Check if API is running
    fetch('http://localhost:8000/health')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            log('✅ API connection established', 'success');
            log(`API Status: ${data.status}`, 'success');
        })
        .catch(error => {
            log('❌ Cannot connect to API. Make sure it\'s running on localhost:8000', 'error');
            log(`Connection Error: ${error.message}`, 'error');
            
            // Try alternative port
            fetch('http://localhost:3000/health')
                .then(response => response.json())
                .then(data => {
                    log('✅ Found API on port 3000!', 'success');
                    // Update API_BASE to use port 3000
                    window.API_BASE = 'http://localhost:3000/api/podcast';
                })
                .catch(() => {
                    log('❌ API not found on port 3000 either', 'error');
                    alert('API Server not running! Please start the API server first.\n\nRun: uvicorn main:app --reload --port 8000');
                });
        });
});

// Example topics for testing
function loadExampleTopic(topicName) {
    const examples = {
        'renewable_energy': {
            topic: 'الطاقة المتجددة',
            info: 'مناقشة أهمية الطاقة المتجددة في المستقبل والتحديات التي تواجهها في العالم العربي'
        },
        'ai_education': {
            topic: 'الذكاء الاصطناعي في التعليم',
            info: 'كيف يمكن للذكاء الاصطناعي أن يغير طريقة التعلم والتعليم في المدارس والجامعات'
        },
        'cybersecurity': {
            topic: 'الأمن السيبراني',
            info: 'التحديات والحلول في مجال الأمن السيبراني للشركات والأفراد'
        }
    };
    
    if (examples[topicName]) {
        document.getElementById('topic').value = examples[topicName].topic;
        document.getElementById('info').value = examples[topicName].info;
        log(`📝 Loaded example: ${examples[topicName].topic}`, 'success');
    }
}

// Add example buttons
document.addEventListener('DOMContentLoaded', function() {
    const step1 = document.getElementById('step1');
    const examplesDiv = document.createElement('div');
    examplesDiv.innerHTML = `
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
            <small style="color: #666;">Quick Examples:</small><br>
            <button class="btn btn-secondary" onclick="loadExampleTopic('renewable_energy')" style="margin: 5px; font-size: 12px;">
                الطاقة المتجددة
            </button>
            <button class="btn btn-secondary" onclick="loadExampleTopic('ai_education')" style="margin: 5px; font-size: 12px;">
                الذكاء الاصطناعي في التعليم
            </button>
            <button class="btn btn-secondary" onclick="loadExampleTopic('cybersecurity')" style="margin: 5px; font-size: 12px;">
                الأمن السيبراني
            </button>
        </div>
    `;
    step1.appendChild(examplesDiv);
});
