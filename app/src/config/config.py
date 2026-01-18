"""Configuration file.

Configuration of project variables that we want to have available
everywhere and considered configuration.
"""
import os
from dataclasses import dataclass

@dataclass 
class Configuration:
    """Configuration class for the project."""

    DATA_PATH: str = os.path.join("..", "data")
    OUTPUT_PATH: str = os.path.join("..", "output")

    audio_path: str = os.path.join(DATA_PATH, "audios")
    pdf_path: str = os.path.join(DATA_PATH, "pdfs")
    db_path: str = os.path.join(DATA_PATH, "db_data")

    audio_name: str = None

    whisper_version: str = "medium"

    rag_model_name: str = "llama3.1"
    rag_embedding_model: str = "nomic-embed-text"
    
    kokoro_language: str = "es"
    kokoro_voice: str = "ef_dora"
    kokoro_rate: int = 24000
    kokoro_play_speed: float = 1.0

    def __post_init__(self):
        self.audio_name = os.path.join(self.audio_path, self.audio_name)
