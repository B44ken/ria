"""Off-screen previews of the actual exported geometry (VTK/EGL, no Blender).

GLB is reloaded and converted back from metres/Y-up to CAD mm/Z-up. Cutaway
views deliberately remove the input pulley, exposing its integral sun below.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray

from .export import CAD_TO_GLTF
from .model import COLOURS, Part
from .config import RobotConfig
from .robot import motion_transform


def load_meshes(path: Path) -> dict[str, trimesh.Trimesh]:
    scene = trimesh.load(path, force="scene", process=True)
    meshes = {}
    for node in scene.graph.nodes_geometry:
        transform, geometry = scene.graph[node]
        mesh = scene.geometry[geometry].copy()
        mesh.apply_transform(np.linalg.inv(CAD_TO_GLTF) @ transform)
        meshes[node] = mesh
    return meshes


def polydata(mesh: trimesh.Trimesh) -> vtk.vtkPolyData:
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(np.ascontiguousarray(mesh.vertices), deep=True))
    cells = vtk.vtkCellArray()
    indexed = np.column_stack((np.full(len(mesh.faces), 3), mesh.faces))
    cells.SetCells(len(mesh.faces), numpy_to_vtkIdTypeArray(indexed.astype(np.int64).ravel(), deep=True))
    data = vtk.vtkPolyData()
    data.SetPoints(points)
    data.SetPolys(cells)
    return data


def render_image(meshes: dict, materials: dict, path: Path, *, target=(0, 40, 15),
                 camera=(170, -150, 250), up=(0, 1, 0), scale=90,
                 size=(1400, 1400), cutaway=False) -> None:
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.94, 0.95, 0.97)
    renderer.SetBackground2(1, 1, 1)
    renderer.GradientBackgroundOn()
    for name, mesh in meshes.items():
        if cutaway and (name == "belt" or name == "motor_pulley" or name.startswith("hip_")):
            continue
        data = polydata(mesh)
        if cutaway and name in ("sun_pulley", "upper_leg"):
            is_sun = name == "sun_pulley"
            # Remove the pulley and hub above the sun, closing the section face.
            plane = vtk.vtkPlane()
            plane.SetOrigin(0, 0, 23.09 if is_sun else 18.09)
            plane.SetNormal(0, 0, -1 if is_sun else 1)
            planes = vtk.vtkPlaneCollection()
            planes.AddItem(plane)
            clip = vtk.vtkClipClosedSurface()
            clip.SetInputData(data)
            clip.SetClippingPlanes(planes)
            clip.Update()
            data = clip.GetOutput()
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(data)
        normals.SetFeatureAngle(35)
        normals.ConsistencyOn()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        colour = COLOURS.get(materials.get(name, "purple"), COLOURS["purple"])
        actor.GetProperty().SetColor(*colour)
        actor.GetProperty().SetAmbient(0.22)
        actor.GetProperty().SetDiffuse(0.72)
        actor.GetProperty().SetSpecular(0.24)
        actor.GetProperty().SetSpecularPower(35)
        renderer.AddActor(actor)
    cam = renderer.GetActiveCamera()
    cam.SetPosition(*camera)
    cam.SetFocalPoint(*target)
    cam.SetViewUp(*up)
    cam.ParallelProjectionOn()
    cam.SetParallelScale(scale)
    renderer.ResetCameraClippingRange()
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(*size)
    window.SetMultiSamples(8)
    window.AddRenderer(renderer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGB()
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    path.parent.mkdir(parents=True, exist_ok=True)
    writer.SetFileName(str(path))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    with Image.open(path) as image:
        image.verify()


def contact_sheet(items: list[tuple[Path, str]], path: Path, columns: int = 3) -> None:
    width, height = 480, 430
    rows = (len(items) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * width, rows * height), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=16)
    for index, (image_path, label) in enumerate(items):
        x, y = (index % columns) * width, (index // columns) * height
        image = Image.open(image_path).convert("RGB")
        image.thumbnail((width - 12, height - 42))
        sheet.paste(image, (x + (width - image.width) // 2, y))
        draw.text((x + 12, y + height - 32), label, fill=(30, 34, 42), font=font)
    sheet.save(path)


def render_build(build: Path, config: RobotConfig, *, animate: bool = True) -> None:
    metadata = json.loads((build / "model.json").read_text())
    knee = load_meshes(build / "knee.glb")
    materials = {p["name"]: p["material"] for p in metadata["knee_parts"]}
    output = build / "previews"
    output.mkdir(parents=True, exist_ok=True)
    render_image(knee, materials, output / "knee.png")
    render_image(knee, materials, output / "knee_front.png", target=(0, 40, 15),
                 camera=(0, 40, 280), scale=90)
    render_image(knee, materials, output / "gears_cutaway.png", cutaway=True,
                 target=(0, -3, 18), camera=(0, -3, 250), scale=38)
    render_image(knee, materials, output / "gears_cutaway_iso.png", cutaway=True,
                 target=(0, -3, 18), camera=(90, -125, 260), scale=44)
    if metadata["robot_parts"] and (build / "robot.glb").exists():
        robot = load_meshes(build / "robot.glb")
        colour = {p["name"]: p["material"] for p in metadata["robot_parts"]}
        render_image(robot, colour, output / "robot.png", target=(0, 0, -34),
                     camera=(230, 320, 180), up=(0, 0, 1), scale=128, size=(1600, 1600))
        render_image(robot, colour, output / "robot_front.png", target=(0, 0, -34),
                     camera=(300, 0, -34), up=(0, 0, 1), scale=128)
    manifest = json.loads((build / "print_manifest.json").read_text())
    tiles = []
    for record in manifest:
        name = record["name"]
        mesh = trimesh.load_mesh(build / record["file"], process=True)
        target = mesh.bounds.mean(axis=0)
        scale = max(mesh.extents) * 0.75
        target = target.tolist()
        camera = (np.array(target) + np.array([1.3, -1.5, 2.4]) * scale).tolist()
        path = output / "parts" / (name + ".png")
        render_image({name: mesh}, {name: materials.get(name, "head" if name.startswith("head") else "purple")},
                     path, target=target, camera=camera, up=(0, 0, 1), scale=scale, size=(600, 520))
        tiles.append((path, name))
    contact_sheet(tiles, output / "all_printables.png")
    if animate:
        frames, tiles = [], []
        for index, angle in enumerate(np.linspace(-120, 120, 25)):
            meshes = {}
            for record in metadata["knee_parts"]:
                name = record["name"]
                part = Part(name, None, motion=record["motion"], centre=tuple(record["centre_mm"]))
                meshes[name] = knee[name].copy().apply_transform(motion_transform(part, float(angle), config))
            path = output / "motion_frames" / f"{index:02d}.png"
            render_image(meshes, materials, path, cutaway=True,
                         target=(0, 0, 18), camera=(0, 0, 260), scale=46, size=(700, 700))
            frames.append(Image.open(path).convert("RGB"))
            tiles.append((path, f"carrier {angle:+.0f} deg"))
        # Ping-pong, rather than jumping discontinuously between travel limits.
        sequence = frames + frames[-2:0:-1]
        sequence[0].save(output / "knee_motion.gif", save_all=True, append_images=sequence[1:],
                         duration=90, loop=0, disposal=2)
        contact_sheet(tiles, output / "motion_contact_sheet.png", columns=5)
    print("  rendered previews, print contact sheet and motion", flush=True)
