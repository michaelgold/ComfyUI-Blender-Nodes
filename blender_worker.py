import argparse
from pathlib import Path


def apply_scene_transforms():
    import bpy

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="DESELECT")

    for obj in bpy.context.scene.objects:
        if obj.library is not None:
            continue

        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.select_set(False)


def fbx_to_glb(source_path: str, output_path: str):
    import bpy

    bpy.ops.wm.read_factory_settings(use_empty=True)

    import_result = bpy.ops.import_scene.fbx(filepath=source_path)
    if "FINISHED" not in import_result:
        raise RuntimeError(f"Failed to import FBX: {source_path}")

    apply_scene_transforms()

    pack_result = bpy.ops.file.pack_all()
    if "FINISHED" not in pack_result:
        raise RuntimeError("Failed to pack resources into Blender data")

    export_result = bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format="GLB",
        export_image_format="AUTO",
        check_existing=False,
    )
    if "FINISHED" not in export_result:
        raise RuntimeError(f"Failed to export GLB: {output_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Isolated Blender worker operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fbx_to_glb_parser = subparsers.add_parser("fbx-to-glb", help="Convert FBX to GLB")
    fbx_to_glb_parser.add_argument("source_path", help="Path to input FBX file")
    fbx_to_glb_parser.add_argument("output_path", help="Path to output GLB file")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "fbx-to-glb":
        source_path = str(Path(args.source_path).expanduser().resolve())
        output_path = str(Path(args.output_path).expanduser().resolve())
        fbx_to_glb(source_path, output_path)
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())