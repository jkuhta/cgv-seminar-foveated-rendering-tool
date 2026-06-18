from pathlib import Path
import numpy as np

OBJ_PATH = Path(__file__).parent.parent / "external_code/assets/island.obj"
MTL_PATH = Path(__file__).parent.parent / "external_code/assets/island.mtl"
FALLBACK_COLOR = (0.55, 0.50, 0.45)

_cache = None


def parse_mtl(mtl_path):
    material_colors = {}
    current_material = None

    with open(mtl_path) as mtl_file:
        for line in mtl_file:
            tokens = line.strip().split()
            if not tokens:
                continue
            if tokens[0] == "newmtl":
                current_material = tokens[1]
            elif tokens[0] == "Kd" and current_material is not None:
                r, g, b = float(tokens[1]), float(tokens[2]), float(tokens[3])
                material_colors[current_material] = (r, g, b)

    return material_colors


def load_obj(obj_path, material_colors):
    positions = []
    normals = []
    triangles = []
    current_color = FALLBACK_COLOR
    # TODO: handle missing normals more gracefully — currently just uses (0,1,0) as fallback

    with open(obj_path) as obj_file:
        for raw_line in obj_file:
            line = raw_line.strip()
            tokens = line.split()
            if not tokens or line.startswith("#"):
                continue

            if tokens[0] == "v":
                positions.append((float(tokens[1]), float(tokens[2]), float(tokens[3])))

            elif tokens[0] == "vn":
                normals.append((float(tokens[1]), float(tokens[2]), float(tokens[3])))

            elif tokens[0] == "usemtl":
                material_name = tokens[1] if len(tokens) > 1 else ""
                current_color = material_colors.get(material_name, FALLBACK_COLOR)

            elif tokens[0] == "f":
                # parse face verts — format is v/vt/vn or v//vn
                face_vertices = []
                for token in tokens[1:]:
                    parts = token.split("/")
                    position_index = int(parts[0]) - 1
                    normal_index = int(parts[2]) - 1 if len(parts) >= 3 and parts[2] else -1
                    vertex_position = positions[position_index]
                    vertex_normal = normals[normal_index] if normal_index >= 0 else (0.0, 1.0, 0.0)
                    face_vertices.append((vertex_position, vertex_normal))

                # fan triangulation for quads and ngons
                color = list(current_color)
                for i in range(1, len(face_vertices) - 1):
                    for k in (0, i, i + 1):
                        vertex_pos, vertex_nrm = face_vertices[k]
                        triangles.append(list(vertex_pos) + list(vertex_nrm) + color)

    print(len(positions))
    print(len(normals))
    print(len(triangles))


    return np.array(triangles, dtype=np.float32)


def build_scene():
    global _cache
    if _cache is not None:
        return _cache
    # TODO: maybe reload if the obj file changes? probably not needed for demo

    material_colors = parse_mtl(MTL_PATH)
    # print(f"loaded {len(material_colors)} materials")
    scene_data = load_obj(OBJ_PATH, material_colors)
    # print(f"scene has {len(scene_data)} vertices")

    # centre and scale the mesh to fit nicely in the camera view
    positions = scene_data[:, :3]
    mesh_centre = (positions.max(axis=0) + positions.min(axis=0)) * 0.5
    mesh_extent = (positions.max(axis=0) - positions.min(axis=0)).max()
    scale = 12.0 / mesh_extent
    # print(f"scale factor: {scale:.4f}, centre: {mesh_centre}")

    scene_data[:, :3] = (positions - mesh_centre) * scale

    _cache = scene_data
    return _cache


def fullscreen_quad():
    quad_vertices = np.array([
        -1.0, -1.0, 0.0, 0.0,
        1.0, -1.0, 1.0, 0.0,
        1.0, 1.0, 1.0, 1.0,
        -1.0, 1.0, 0.0, 1.0,
    ], dtype=np.float32)
    quad_indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)
    return quad_vertices, quad_indices