import os
from pathlib import Path
import subprocess
import sys


class BlenderFBXToGLB:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fbx_file_path": ("STRING", {"multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("glb_file_path",)
    FUNCTION = "convert"
    CATEGORY = "blender"

    def convert(self, fbx_file_path):
        source_path = Path(os.path.expanduser(str(fbx_file_path))).resolve()

        if not source_path.exists():
            raise FileNotFoundError(f"FBX file not found: {source_path}")
        if source_path.suffix.lower() != ".fbx":
            raise ValueError(f"Input file must be an FBX: {source_path}")

        output_path = source_path.with_suffix(".glb")
        worker_path = Path(__file__).with_name("blender_worker.py").resolve()

        # Run bpy work in an isolated interpreter so Blender crashes do not terminate ComfyUI.
        process = subprocess.run(
            [
                sys.executable,
                str(worker_path),
                "fbx-to-glb",
                str(source_path),
                str(output_path),
            ],
            capture_output=True,
            text=True,
        )
        if process.returncode != 0:
            error_details = (process.stderr or process.stdout or "Unknown error").strip()
            raise RuntimeError(
                "Failed to convert FBX to GLB in isolated bpy process "
                f"(exit code {process.returncode}): {error_details}"
            )

        return (str(output_path),)


NODE_CLASS_MAPPINGS = {
    "BlenderFBXToGLB": BlenderFBXToGLB,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BlenderFBXToGLB": "Blender: FBX to GLB",
}
