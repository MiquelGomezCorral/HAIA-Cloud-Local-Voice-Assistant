import torch
from transformers import AutoProcessor, AutoModelForTextToWaveform
import soundfile as sf

from src.config import Configuration



def generate_audio(text, CONFIG: Configuration):
    # Load Model (Runs on your GPU)
    print(">>> Loading Qwen3-TTS...")
    processor = AutoProcessor.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base")
    model = AutoModelForTextToWaveform.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base")
    model.to("cuda")
    
    # Process text
    print(f"Generating: {text}...")
    inputs = processor(text=text, return_tensors="pt").to("cuda")
    
    # Generate audio
    with torch.no_grad():
        # The model generates audio directly
        output = model.generate(**inputs)
    
    # Save to file
    sampling_rate = model.config.sample_rate
    audio_data = output.cpu().numpy().squeeze()
    
    sf.write(CONFIG.audio_name, audio_data, sampling_rate)
    print(f"Saved to {CONFIG.audio_name}")