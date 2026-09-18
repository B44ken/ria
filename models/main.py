#!/usr/bin/env python3
"""Build ria's head and two upper-leg/knee assemblies. Run `python main.py --help`."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--import-source", type=Path, help="Import unchanged reference geometry once from the original ria.zip or its extracted directory.")
    result.add_argument("--assets", type=Path, default=ROOT / "assets/reference", help="Reference B-rep cache directory.")
    result.add_argument("--output", type=Path, default=ROOT / "build", help="Generated files directory (default: build/ beside main.py).")
    result.add_argument("--knee-only", action="store_true", help="Build one local leg assembly, without the head or installed pair.")
    result.add_argument("--no-render", action="store_true", help="Skip VTK previews; CAD and meshes are still exported.")
    result.add_argument("--no-animation", action="store_true", help="Render stills and print contact sheet, without the motion GIF.")
    result.add_argument("--no-validate", action="store_true", help="Skip assembly/motion audit (export integrity checks still run).")
    result.add_argument("--compare-source", type=Path, help="Additionally regress against the original source archive and supplied build.")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    # Imports stay here: importing main has no CAD, filesystem, or viewer side effects.
    try:
        from src.assets import AssetLibrary, import_assets
        from src.config import RobotConfig
        from src.export import export_models
        from src.knee import build_knee
        from src.robot import build_robot

        if args.import_source:
            print("Importing unchanged reference geometry", flush=True)
            import_assets(args.import_source, args.assets)
        assets = AssetLibrary(args.assets)
        config = RobotConfig()
        print("Building 18T / 12T / 42T knee; total reduction 10:1", flush=True)
        knee = build_knee(assets, config)
        robot = None if args.knee_only else build_robot(knee, assets, config)
        exported = export_models(knee, robot, config, args.output)
        passed = True
        if not args.no_validate:
            from src.validate import validate_build
            passed = validate_build(knee, robot, config, exported, args.output)["pass"]
        if args.compare_source:
            from src.regression import compare_source
            passed &= compare_source(knee, robot, assets, args.compare_source, args.output)["pass"]
        if not args.no_render:
            from src.render import render_build
            render_build(args.output, config, animate=not args.no_animation)
        print("Outputs: " + str(args.output.resolve()), flush=True)
        if not passed:
            print("Geometry checks failed. Read validation.json / regression.json before using the model.", file=sys.stderr)
            return 1
        print("Build complete." if args.no_validate else "Build and geometry checks complete.", flush=True)
        return 0
    except (ImportError, OSError, ValueError, KeyError) as error:
        print(f"ria: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
