import whisper

def whisper_transcribe(path:str, whisper_model:str = "medium") -> str:
    """Función para llamar a whisper y transcribir el audio.

    Args:
        path (str): Ruta al audio.
        whisper_model (str, optional): Variante de whisper a utilizar. Defaults to "medium".

    Returns:
        str: Transcripción de whisper.
    """
    model = whisper.load_model(whisper_model)

    result = model.transcribe(path)

    return result["text"]