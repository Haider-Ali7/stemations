"""
Video & Audio Composition Tool
Merges the rendered vertical Manim MP4 with the generated neural voiceover.
"""
import os
import uuid
import subprocess
from pathlib import Path
from typing import Dict, Any

def compose_video_and_audio(
    video_path: str,
    audio_path: str,
    output_dir: str = "_output/final"
) -> Dict[str, Any]:
    """
    Combines video and audio into a final .mp4 file.
    If the audio is longer than the animation, extends the last frame smoothly.
    Returns:
        {
            "success": bool,
            "final_video_path": Optional[str],
            "error": Optional[str]
        }
    """
    backend_dir = Path(__file__).resolve().parent.parent.parent
    p = Path(output_dir)
    out_dir = p if p.is_absolute() else (backend_dir / p).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    
    unique_id = uuid.uuid4().hex[:8]
    final_output = out_dir / f"stemation_{unique_id}.mp4"
    
    # 1. Primary Strategy: Try MoviePy (v1 editor API or v2 top-level imports)
    try:
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
        except ImportError:
            from moviepy import VideoFileClip, AudioFileClip
            from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips

        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)

        v_dur = video_clip.duration
        a_dur = audio_clip.duration

        if a_dur > v_dur:
            freeze_duration = a_dur - v_dur + 0.5
            last_frame = video_clip.to_ImageClip(max(0, v_dur - 0.05))
            if hasattr(last_frame, "with_duration"):
                last_frame = last_frame.with_duration(freeze_duration)
            else:
                last_frame = last_frame.set_duration(freeze_duration)
            combined_video = concatenate_videoclips([video_clip, last_frame])
        else:
            combined_video = video_clip

        if hasattr(combined_video, "with_audio"):
            final_clip = combined_video.with_audio(audio_clip)
        else:
            final_clip = combined_video.set_audio(audio_clip)

        try:
            final_clip.write_videofile(
                str(final_output),
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=str(out_dir / f"temp_{unique_id}.m4a"),
                remove_temp=True,
                verbose=False,
                logger=None,
            )
        except TypeError:
            final_clip.write_videofile(
                str(final_output),
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=str(out_dir / f"temp_{unique_id}.m4a"),
                remove_temp=True,
                logger=None,
            )

        video_clip.close()
        audio_clip.close()
        
        if final_output.exists():
            return {
                "success": True,
                "final_video_path": str(final_output),
                "error": None
            }
    except Exception as moviepy_err:
        # 2. Fallback Strategy: Direct FFmpeg command
        try:
            import shutil
            import imageio_ffmpeg
            ffmpeg_exe = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()
            cmd = [
                ffmpeg_exe, "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(final_output)
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0 and final_output.exists():
                return {
                    "success": True,
                    "final_video_path": str(final_output),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "final_video_path": None,
                    "error": f"MoviePy failed ({moviepy_err}) and FFmpeg failed ({res.stderr})"
                }
        except Exception as ffmpeg_err:
            return {
                "success": False,
                "final_video_path": None,
                "error": f"Composition failed: {moviepy_err} | {ffmpeg_err}"
            }
            
    return {
        "success": False,
        "final_video_path": None,
        "error": "Failed to create composed video."
    }
