"""
Manim Code Execution Tool
Runs Manim Community Edition in a sandboxed subprocess and captures outputs.
"""
import os
import sys
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any

def render_manim_code(code: str, output_dir: str = "_output/scenes") -> Dict[str, Any]:
    """
    Renders the provided Manim code.
    Returns:
        {
            "success": bool,
            "video_path": Optional[str],
            "error": Optional[str],
            "stdout": str,
            "stderr": str
        }
    """
    out_path = Path(output_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)
    
    unique_id = uuid.uuid4().hex[:8]
    scene_file = out_path / f"scene_{unique_id}.py"
    scene_file.write_text(code, encoding="utf-8")
    
    media_dir = out_path / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    
    # Use python -m manim to ensure it works across all Windows/Mac/Linux environments
    cmd = [
        sys.executable, "-m", "manim",
        "-ql",  # Low quality for ultra-fast rendering (ideal for live hackathon demos)
        "--media_dir", str(media_dir),
        str(scene_file),
        "StemationScene"
    ]
    
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=90  # 90-second timeout guardrail
        )
        
        stdout = proc.stdout
        stderr = proc.stderr
        
        if proc.returncode != 0:
            return {
                "success": False,
                "video_path": None,
                "error": stderr or stdout or f"Process failed with exit code {proc.returncode}",
                "stdout": stdout,
                "stderr": stderr
            }
            
        # Search for the rendered .mp4 file
        rendered_videos = list(media_dir.glob("**/StemationScene.mp4"))
        if not rendered_videos:
            # Fallback search for any mp4 created
            rendered_videos = list(media_dir.glob("**/*.mp4"))
            
        if rendered_videos:
            return {
                "success": True,
                "video_path": str(rendered_videos[-1]),
                "error": None,
                "stdout": stdout,
                "stderr": stderr
            }
        else:
            return {
                "success": False,
                "video_path": None,
                "error": "Manim completed but no output .mp4 file was found.",
                "stdout": stdout,
                "stderr": stderr
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "video_path": None,
            "error": "Manim rendering timed out (>90s). The scene may be too long or complex.",
            "stdout": "",
            "stderr": ""
        }
    except Exception as e:
        return {
            "success": False,
            "video_path": None,
            "error": str(e),
            "stdout": "",
            "stderr": str(e)
        }
