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

    kokoro_language: str = "es"
    kokoro_voice: str = "ef_dora"
    kokoro_rate: int = 24000
    kokoro_play_speed: float = 1.0

    def __post_init__(self):
        ...
