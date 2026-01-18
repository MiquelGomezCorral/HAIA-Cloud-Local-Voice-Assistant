import os

from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
from datetime import datetime

from src.config import Configuration


def kokoro_generate_audio(text, CONFIG: Configuration, print_output: bool = True):
    """
    Generate audio using Kokoro TTS model and configuration.
    
    :param text: Text to be converted to speech
    :type text: str
    :param CONFIG: Configuration object containing TTS settings
    :type CONFIG: Configuration
    
    """
    pipeline = KPipeline(lang_code=CONFIG.kokoro_language)

    generator = pipeline(
        text, 
        voice=CONFIG.kokoro_voice,
        speed=CONFIG.kokoro_play_speed,
    )

    all_audio = []

    for i, (gs, ps, audio) in enumerate(generator):
        if print_output:
            print(i, gs, ps)
            display(Audio(data=audio, rate=CONFIG.kokoro_rate, autoplay=i==0))

        all_audio.append(audio)

        save_path = os.path.join(
            CONFIG.OUTPUT_PATH, 
            f'kokoro-{CONFIG.kokoro_voice}-{CONFIG.kokoro_language}-'
            f'{datetime.today().strftime("%Y-%m-%d")}.wav'
        )
        sf.write(save_path, audio, CONFIG.kokoro_rate)


    return all_audio