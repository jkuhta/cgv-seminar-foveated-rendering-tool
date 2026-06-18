import numpy as np
import math


class Camera:
    def __init__(self):
        self.target = np.array([0.0, -0.9, 0.0])
        self.distance = 1.8
        self.yaw = 0.0
        self.pitch = 10.0
        self.fov_y = 60.0
        self.near = 0.1
        self.far = 100.0

    def rotate(self, delta_yaw_degrees):
        self.yaw = (self.yaw + delta_yaw_degrees + 180.0) % 360.0 - 180.0
        # print(f"yaw: {self.yaw:.1f}")

    def eye_world_pos(self, lateral_offset=0.0):
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        # spherical to cartesian
        eye_position = self.target + self.distance * np.array([
            math.cos(pitch_rad) * math.sin(yaw_rad),
            math.sin(pitch_rad),
            math.cos(pitch_rad) * math.cos(yaw_rad),
        ])

        # shift left/right for stereo separation
        # TODO: maybe expose right_dir so renderer doesn't have to recompute it
        if lateral_offset:
            forward_dir = self.target - eye_position
            forward_dir /= np.linalg.norm(forward_dir)
            right_dir = np.cross(forward_dir, [0, 1, 0])
            right_dir /= np.linalg.norm(right_dir)
            eye_position += right_dir * lateral_offset

        return eye_position

    def view_matrix(self, lateral_offset=0.0):
        eye_position = self.eye_world_pos(lateral_offset)

        forward_dir = self.target - eye_position
        forward_dir /= np.linalg.norm(forward_dir)
        right_dir = np.cross(forward_dir, [0, 1, 0])
        right_dir /= np.linalg.norm(right_dir)
        up_dir = np.cross(right_dir, forward_dir)

        view_matrix = np.eye(4, dtype=np.float32)
        view_matrix[0, :3] = right_dir
        view_matrix[1, :3] = up_dir
        view_matrix[2, :3] = -forward_dir
        view_matrix[0, 3] = -np.dot(right_dir, eye_position)
        view_matrix[1, 3] = -np.dot(up_dir, eye_position)
        view_matrix[2, 3] = np.dot(forward_dir, eye_position)

        # print(view_matrix)
        return view_matrix.T  # numpy is row-major, glsl expects column-major

    def projection_matrix(self, aspect_ratio):
        focal_length = 1.0 / math.tan(math.radians(self.fov_y) / 2.0)

        proj_matrix = np.zeros((4, 4), dtype=np.float32)
        proj_matrix[0, 0] = focal_length / aspect_ratio
        proj_matrix[1, 1] = focal_length
        proj_matrix[2, 2] = (self.far + self.near) / (self.near - self.far)
        proj_matrix[2, 3] = (2 * self.far * self.near) / (self.near - self.far)
        proj_matrix[3, 2] = -1.0

        return proj_matrix.T  # numpy is row-major, glsl expects column-major