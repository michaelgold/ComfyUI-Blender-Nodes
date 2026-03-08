import os
from pathlib import Path

import bpy


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

        bpy.ops.wm.read_factory_settings(use_empty=True)

        import_result = bpy.ops.import_scene.fbx(filepath=str(source_path))
        if "FINISHED" not in import_result:
            raise RuntimeError(f"Failed to import FBX: {source_path}")

        pack_result = bpy.ops.file.pack_all()
        if "FINISHED" not in pack_result:
            raise RuntimeError("Failed to pack resources into Blender data")

        export_result = bpy.ops.export_scene.gltf(
            filepath=str(output_path),
            export_format="GLB",
            export_image_format="AUTO",
            check_existing=False,
        )
        if "FINISHED" not in export_result:
            raise RuntimeError(f"Failed to export GLB: {output_path}")

        return (str(output_path),)


NODE_CLASS_MAPPINGS = {
    "BlenderFBXToGLB": BlenderFBXToGLB,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BlenderFBXToGLB": "Blender: FBX to GLB",
}
