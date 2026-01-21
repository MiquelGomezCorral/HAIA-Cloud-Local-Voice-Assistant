"""Gradio Web UI for the audio pipeline."""

import os
import sys
import gradio as gr
import dotenv
import datetime
import shutil

# Import from main.py (same directory)
from main import cmd_read_audio

# Get paths relative to where the script is launched (from ./app)
# Config expects to be run from app/ so paths work the same way
AUDIO_INPUT_DIR = os.path.abspath(os.path.join("..", "data", "audios"))
OUTPUT_DIR = os.path.abspath(os.path.join("..", "output"))

# Ensure directories exist
os.makedirs(AUDIO_INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"📁 Current working directory: {os.getcwd()}")
print(f"📁 Audio input directory: {AUDIO_INPUT_DIR}")
print(f"📁 Output directory: {OUTPUT_DIR}")


def process_audio(audio_input):
    """Process the recorded audio through the pipeline.
    
    Args:
        audio_input: Audio file path from Gradio
        
    Returns:
        Tuple: (output_audio, status_message, button_state)
    """
    print(f"\n🔍 DEBUG: process_audio called")
    print(f"🔍 DEBUG: audio_input type: {type(audio_input)}")
    print(f"🔍 DEBUG: audio_input value: {audio_input}")
    
    if audio_input is None:
        return None, "⚠️ No audio recorded", gr.Button(interactive=False)
    
    try:
        # Handle both string paths and potential tuple (sample_rate, data) formats
        if isinstance(audio_input, tuple):
            print(f"🔍 DEBUG: Received tuple - likely (sample_rate, data)")
            # If it's a tuple, Gradio might have changed - try to get the path from sources
            return None, "❌ Unexpected audio format (tuple). Please check Gradio audio component settings.", gr.Button(interactive=False)
        
        # In Gradio with type="filepath", it should return a string path
        audio_filepath = str(audio_input) if audio_input else None
        
        print(f"🔍 DEBUG: audio_filepath: {audio_filepath}")
        print(f"🔍 DEBUG: File exists: {os.path.exists(audio_filepath) if audio_filepath else 'N/A'}")
        
        if not audio_filepath or not os.path.exists(audio_filepath):
            return None, f"❌ Audio file not found at: {audio_filepath}", gr.Button(interactive=False)
        
        # Wait a moment to ensure the file is fully written (especially for recordings)
        import time
        time.sleep(0.1)
        
        # Verify file size is reasonable
        file_size = os.path.getsize(audio_filepath)
        print(f"🔍 DEBUG: File size: {file_size} bytes")
        
        if file_size == 0:
            return None, "❌ Audio file is empty", gr.Button(interactive=False)
        
        # Copy the file to our data/audios directory with a proper name
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        target_path = os.path.join(AUDIO_INPUT_DIR, filename)
        
        shutil.copy2(audio_filepath, target_path)
        print(f"✅ Audio copied to: {target_path}")
        
        # Create a minimal args namespace-like object with required configuration
        class Args:
            def __init__(self, audio_path):
                self.audio_name = audio_path
                self.verbose = True
                self.seed = 42
        
        # Create args object
        args = Args(target_path)
        
        print("🚀 Starting pipeline processing...")
        # Run the full pipeline
        final_audio, save_path = cmd_read_audio(args)
        
        print(f"✅ Pipeline complete. Output: {save_path}")
        
        # Return the save path for Gradio to play
        # If save_path is available, use it; otherwise return final_audio
        if save_path and os.path.exists(save_path):
            return save_path, "✅ Processing complete!", gr.Button(interactive=False)
        else:
            return final_audio, "✅ Processing complete!", gr.Button(interactive=False)
            
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return None, error_msg, gr.Button(interactive=False)


def on_audio_upload(audio_input):
    """Enable/disable process button based on audio availability."""
    print(f"\n🔍 DEBUG: on_audio_upload called")
    print(f"🔍 DEBUG: audio_input type: {type(audio_input)}")
    print(f"🔍 DEBUG: audio_input value: {audio_input}")
    
    if audio_input is not None:
        print("✅ Audio detected - enabling button")
        return gr.Button(interactive=True), "🎤 Audio ready to process"
    else:
        print("⚠️ No audio - disabling button")
        return gr.Button(interactive=False), "⏺️ Record audio first"


def create_ui():
    """Create and configure the Gradio interface."""
    
    with gr.Blocks(title="Audio Pipeline") as demo:
        gr.Markdown("# 🎙️ Audio Processing Pipeline")
        gr.Markdown("**Whisper** (transcription) → **RAG** (response) → **Kokoro** (audio generation)")
        gr.Markdown("---")
        gr.Markdown("🎤 **Step 1:** Click the microphone icon to record, or upload an audio file")
        gr.Markdown("🚀 **Step 2:** After stopping the recording, click 'Process Audio' to run the pipeline")
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(
                    label="🎤 Record or Upload Audio",
                    type="filepath",
                    sources=["microphone", "upload"],
                    show_label=True
                )
                status_text = gr.Textbox(
                    label="Status",
                    value="⏺️ Record or upload audio first",
                    interactive=False
                )
                process_btn = gr.Button(
                    "🚀 Process Audio",
                    variant="primary"
                )
            
            with gr.Column():
                audio_output = gr.Audio(
                    label="🔊 Output Audio"
                )
        
        # Enable button when audio is uploaded/recorded
        audio_input.upload(
            fn=on_audio_upload,
            inputs=audio_input,
            outputs=[process_btn, status_text]
        )
        
        audio_input.stop_recording(
            fn=on_audio_upload,
            inputs=audio_input,
            outputs=[process_btn, status_text]
        )
        
        # Process audio when button is clicked
        process_btn.click(
            fn=process_audio,
            inputs=audio_input,
            outputs=[audio_output, status_text, process_btn]
        )
    
    return demo


if __name__ == "__main__":
    # Load environment variables
    dotenv.load_dotenv()
    
    # Create and launch the interface
    demo = create_ui()
    demo.launch(
        share=False, 
        server_name="0.0.0.0", 
        server_port=7860,
        allowed_paths=[OUTPUT_DIR, AUDIO_INPUT_DIR]
    )
