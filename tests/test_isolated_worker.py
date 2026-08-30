import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "blender_fbx_to_glb_node.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("blender_fbx_to_glb_node", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_blender_worker_subprocess_drops_open3d_preload(tmp_path, monkeypatch):
    module = _load_module()
    source = tmp_path / "input.fbx"
    source.write_bytes(b"fixture")
    monkeypatch.setenv("LD_PRELOAD", "/app/.venv/open3d/libOpen3D.so")
    monkeypatch.setenv("KEEP_ME", "yes")
    captured = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        Path(args[-1]).write_bytes(b"glb")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    result = module.BlenderFBXToGLB().convert(str(source))

    assert Path(result[0]).is_file()
    worker_env = captured["kwargs"]["env"]
    assert "LD_PRELOAD" not in worker_env
    assert worker_env["KEEP_ME"] == "yes"
    assert os.environ["LD_PRELOAD"] == "/app/.venv/open3d/libOpen3D.so"
