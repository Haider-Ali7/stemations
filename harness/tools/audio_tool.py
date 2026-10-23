"""
Neural Audio Voiceover Tool using edge-tts
Free, ultra-fast, high-quality neural narration with zero external API fees.
"""
import asyncio
import os
import uuid
from pathlib import Path
from typing import Dict, Any

DEFAULT_VOICE = "en-US-ChristopherNeural"  # Professional, natural educational tone

async def _generate_audio_async(text: str, output_file: str, voice: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def generate_voiceover(
    text: str,
    output_dir: str = "_output/audio",
    voice: str = DEFAULT_VOICE
) -> Dict[str, Any]:
    """
    Synthesizes neural speech for the given narration script.
    Returns:
        {
            "success": bool,
            "audio_path": Optional[str],
            "error": Optional[str]
        }
    """
    out_path = Path(output_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)
    
    unique_id = uuid.uuid4().hex[:8]
    audio_file = out_path / f"voice_{unique_id}.mp3"
    
    try:
        try:
            # Handle existing event loop if called inside async framework or streamlit
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Run in worker thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _generate_audio_async(text, str(audio_file), voice))
                    future.result()
            else:
                loop.run_until_complete(_generate_audio_async(text, str(audio_file), voice))
        except RuntimeError:
            asyncio.run(_generate_audio_async(text, str(audio_file), voice))
            
        if audio_file.exists() and audio_file.stat().st_size > 0:
            return {
                "success": True,
                "audio_path": str(audio_file),
                "error": None
            }
        else:
            return {
                "success": False,
                "audio_path": None,
                "error": "Audio file was not created."
            }
            
    except Exception as e:
        return {
            "success": False,
            "audio_path": None,
            "error": f"Audio synthesis failed: {str(e)}"
        }
