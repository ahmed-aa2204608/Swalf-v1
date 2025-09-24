"""
API Usage Examples
==================

This file shows how to use the AI Podcast Maker API endpoints.
Run these examples after starting the API server.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000/api/podcast"

def example_1_simple_topic():
    """Example 1: Submit simple topic and run full pipeline"""
    print("=== Example 1: Simple Topic Submission ===")
    
    # Step 1: Submit topic
    response = requests.post(f"{BASE_URL}/submit-topic", json={
        "topic": "الطاقة المتجددة",
        "info": "مناقشة أهمية الطاقة المتجددة في المستقبل والتحديات التي تواجهها"
    })
    
    if response.status_code != 200:
        print("Failed to submit topic:", response.text)
        return
    
    podcast_id = response.json()["podcast_id"]
    print(f"Podcast created with ID: {podcast_id}")
    
    # Step 2: Run full pipeline automatically
    response = requests.post(f"{BASE_URL}/complete-pipeline/{podcast_id}")
    if response.status_code != 200:
        print("Failed to start pipeline:", response.text)
        return
    
    print("Pipeline started! Checking status...")
    
    # Step 3: Monitor progress
    while True:
        response = requests.get(f"{BASE_URL}/status/{podcast_id}")
        if response.status_code != 200:
            print("Failed to get status:", response.text)
            break
            
        status_data = response.json()
        status = status_data["status"]
        print(f"Current status: {status}")
        
        if status == "completed":
            print("✅ Podcast generation completed!")
            print(f"Audio file: {status_data['audio_file_path']}")
            break
        elif status == "failed":
            print("❌ Podcast generation failed!")
            print(f"Error: {status_data['error_message']}")
            break
        
        time.sleep(10)  # Check every 10 seconds


def example_2_manual_persona_selection():
    """Example 2: Manual persona selection workflow"""
    print("\n=== Example 2: Manual Persona Selection ===")
    
    # Step 1: Submit topic
    response = requests.post(f"{BASE_URL}/submit-topic", json={
        "topic": "التكنولوجيا في التعليم",
        "info": "كيف تغير التكنولوجيا طريقة التعلم والتعليم"
    })
    
    podcast_id = response.json()["podcast_id"]
    print(f"Podcast ID: {podcast_id}")
    
    # Step 2: Generate persona suggestions
    response = requests.post(f"{BASE_URL}/generate-personas/{podcast_id}")
    if response.status_code != 200:
        print("Failed to generate personas:", response.text)
        return
    
    personas_data = response.json()
    print("Suggested Host:", personas_data["suggested_host"]["JobDescription"])
    print("Suggested Guest:", personas_data["suggested_guest"]["JobDescription"])
    
    # Step 3: Confirm personas (or modify them)
    response = requests.post(f"{BASE_URL}/confirm-personas", json={
        "podcast_id": podcast_id,
        "host_persona": personas_data["suggested_host"],
        "guest_persona": personas_data["suggested_guest"]
    })
    
    print("Personas confirmed!")
    
    # Step 4: Generate content
    response = requests.post(f"{BASE_URL}/generate-content/{podcast_id}")
    print("Content generated!")
    
    # Step 5: Generate script
    response = requests.post(f"{BASE_URL}/generate-script/{podcast_id}")
    print("Script generated!")
    
    # Step 6: Generate audio
    response = requests.post(f"{BASE_URL}/generate-audio/{podcast_id}")
    if response.status_code == 200:
        print("✅ Audio generated!")
        audio_data = response.json()
        print(f"Audio file: {audio_data['audio_file_path']}")


def example_3_with_pdf_file():
    """Example 3: Submit topic with PDF file"""
    print("\n=== Example 3: Topic with PDF File ===")
    
    # Create a test text file (simulate PDF)
    test_content = "هذا محتوى تجريبي من ملف PDF يحتوي على معلومات إضافية عن الموضوع"
    
    # For real PDF, you would do:
    # with open("your_file.pdf", "rb") as f:
    #     files = {"file": ("document.pdf", f, "application/pdf")}
    
    data = {
        "topic": "الذكاء الاصطناعي",
        "info": "نظرة عامة على الذكاء الاصطناعي"
    }
    
    response = requests.post(f"{BASE_URL}/submit-topic-with-file", data=data)
    
    if response.status_code == 200:
        podcast_id = response.json()["podcast_id"]
        print(f"Topic with file submitted! ID: {podcast_id}")


def example_4_download_audio():
    """Example 4: Download completed audio"""
    print("\n=== Example 4: Download Audio ===")
    
    # Replace with actual podcast ID
    podcast_id = "your-podcast-id-here"
    
    response = requests.get(f"{BASE_URL}/download-audio/{podcast_id}")
    
    if response.status_code == 200:
        with open(f"downloaded_podcast_{podcast_id}.mp3", "wb") as f:
            f.write(response.content)
        print("Audio downloaded successfully!")
    else:
        print("Failed to download audio:", response.text)


if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API is running!")
            
            # Run examples
            example_1_simple_topic()
            # example_2_manual_persona_selection()
            # example_3_with_pdf_file()
            
        else:
            print("❌ API is not responding correctly")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on localhost:8000")
        print("Run: uvicorn main:app --reload")
