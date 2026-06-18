#version 330 core

in vec3 in_position;
in vec3 in_normal;
in vec3 in_color;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_proj;

out vec3 v_color;
out vec3 v_normal;
out vec3 v_frag_pos;

void main() {

    vec4 world_pos = u_model * vec4(in_position, 1.0);
    v_frag_pos = world_pos.xyz;
    v_normal = mat3(transpose(inverse(u_model))) * in_normal;
    v_color = in_color;

    gl_Position = u_proj * u_view * world_pos;
}
