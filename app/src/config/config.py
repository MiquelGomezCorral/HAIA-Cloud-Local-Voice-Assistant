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
    OUTPUT_PATH: str = os.path.join("..", "logs")


    def __post_init__(self):
        ...
