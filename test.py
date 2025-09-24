import scipy
import torch
from diffusers import AudioLDM2Pipeline
import os

# Check if CUDA is available
device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if device == "cuda" else torch.float32

print(f"Using device: {device}")

repo_id = "anhnct/audioldm2_gigaspeech"
pipe = AudioLDM2Pipeline.from_pretrained(repo_id, torch_dtype=torch_dtype)
pipe = pipe.to(device)

# Define prompts for Arabic/English speech
prompts = [
    {
        "prompt": "A professional Arabic female voice speaking clearly",
        "transcript": "مرحباً بكم في بودكاست التقنية المستدامة",
        "filename": "arabic_intro.wav"
    },
    {
        "prompt": "A professional English male voice speaking with enthusiasm",
        "transcript": "Welcome to our sustainable technology podcast",
        "filename": "english_intro.wav"
    }
]

negative_prompt = "low quality, distorted, noisy, unclear speech"

# Generate audio for each prompt
for i, config in enumerate(prompts):
    print(f"Generating audio {i+1}/{len(prompts)}: {config['filename']}")
    
    generator = torch.Generator(device).manual_seed(42)
    
    audio = pipe(
        config["prompt"],
        negative_prompt=negative_prompt,
        transcription=config["transcript"],
        num_inference_steps=50,  # Reduced for faster generation
        audio_length_in_s=10.0,
        num_waveforms_per_prompt=1,
        generator=generator,
        max_new_tokens=512
    ).audios
    
    # Save audio
    scipy.io.wavfile.write(config["filename"], rate=16000, data=audio[0])
    print(f"✅ Saved: {config['filename']}")

print("🎵 Audio generation complete!")