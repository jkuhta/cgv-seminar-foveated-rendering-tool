import numpy as np
import trimesh
from pathlib import Path

# OBJ file is in external_code/assets — kept separate from src code
OBJ_PATH = Path(__file__).parent.parent / "external_code/assets/island.obj"


def build_scene():
    # we use trimesh for OBJ parsing
    scene = trimesh.load(str(OBJ_PATH), force='scene')
    # print(f"loaded {len(scene.geometry)} meshes")

    triangles = []

    # each material group in the OBJ becomes a separate mesh in trimesh
    for mesh_name, mesh in scene.geometry.items():

        # print(len(mesh.faces))
        if len(mesh.faces) == 0:  # skip empty meshes
            continue

        vertices = np.array(mesh.vertices, dtype=np.float32)
        normals = np.array(mesh.vertex_normals, dtype=np.float32)

        # transform color from uint to float
        try:
            diffuse_uint8 = mesh.visual.material.diffuse[:3]
            color = np.array(diffuse_uint8, dtype=np.float32) / 255.0

        except Exception:
            color = np.array([0.55, 0.50, 0.45], dtype=np.float32)

        # same colour for all vertices in this material group
        colors = np.tile(color, (len(vertices), 1))

        # flatten faces into a triangle vertex list: pos(3) normal(3) color(3)
        # indexing by face_indices expands the indexed mesh into a flat array
        face_indices = mesh.faces.flatten()
        block = np.hstack([
            vertices[face_indices],
            normals[face_indices],
            colors[face_indices],
        ])

        triangles.append(block)

    scene_data = np.vstack(triangles)

    # center and scale to fit camera
    positions = scene_data[:, :3]
    mesh_centre = (positions.max(axis=0) + positions.min(axis=0)) * 0.5
    mesh_extent = (positions.max(axis=0) - positions.min(axis=0)).max()
    scale = 12.0 / mesh_extent
    # print(f"scale: {scale:.4f}")

    scene_data[:, :3] = (positions - mesh_centre) * scale

    return scene_data


def fullscreen_quad():

    quad_vertices = np.array([
        -1.0, -1.0, 0.0, 0.0,
        1.0, -1.0, 1.0, 0.0,
        1.0, 1.0, 1.0, 1.0,
        -1.0, 1.0, 0.0, 1.0,
    ], dtype=np.float32)

    quad_indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

    return quad_vertices, quad_indices
