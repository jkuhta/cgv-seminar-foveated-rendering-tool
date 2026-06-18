#version 330 core

in vec2 v_uv;

uniform vec2 u_resolution;
uniform vec2 u_gaze;
uniform float u_dot_radius;

out vec4 frag_color;

void main() {
    vec2 px = (v_uv - u_gaze) * u_resolution;
    px.y *= -1.0;
    float dist = length(px);

    // render a red dot at gaze center (in a radius and blended with smoothstep)
    if (dist <= u_dot_radius) {
        float edge = smoothstep(u_dot_radius, u_dot_radius - 1.5, dist);
        frag_color = vec4(1.0, 0.1, 0.1, edge);

        return;
    }

    discard;
}
