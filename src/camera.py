import numpy as np
import math
import pyrr


class Camera:

    def __init__(self):
        self.target = np.array([0.0, -0.9, 0.0], dtype=np.float32)
        self.distance = 1.8
        self.yaw = 0.0
        self.pitch = 10.0
        self.fov_y = 60.0
        self.near = 0.1
        self.far = 100.0

    def rotate(self, delta_yaw_degrees):
        self.yaw = (self.yaw + delta_yaw_degrees + 180.0) % 360.0 - 180.0
        # print(f"yaw: {self.yaw:.1f}")

    # AI Disclaimer: this method was assisted with AI
    def eye_world_pos(self, lateral_offset=0.0):
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        # spherical to cartesian
        eye_position = self.target + self.distance * np.array([
            math.cos(pitch_rad) * math.sin(yaw_rad),
            math.sin(pitch_rad),
            math.cos(pitch_rad) * math.cos(yaw_rad),
        ], dtype=np.float32)

        # shift left/right for stereo separation
        if lateral_offset:
            forward_dir = self.target - eye_position
            forward_dir /= np.linalg.norm(forward_dir)
            right_dir = np.cross(forward_dir, [0, 1, 0])
            right_dir /= np.linalg.norm(right_dir)
            eye_position += right_dir * lateral_offset

        return eye_position

    def view_matrix(self, lateral_offset=0.0):
        eye_position = self.eye_world_pos(lateral_offset)

        view = pyrr.matrix44.create_look_at(
            eye=eye_position,
            target=self.target,
            up=np.array([0.0, 1.0, 0.0], dtype=np.float32),
            dtype=np.float32,
        )

        return view

    def projection_matrix(self, aspect_ratio):

        proj = pyrr.matrix44.create_perspective_projection(
            fovy=self.fov_y,
            aspect=aspect_ratio,
            near=self.near,
            far=self.far,
            dtype=np.float32,
        )

        return proj
