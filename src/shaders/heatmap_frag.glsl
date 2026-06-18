#version 330 core

in vec2 v_uv;

uniform vec2 u_resolution;
uniform vec2 u_gaze;
uniform float u_opacity;   // 0..1 blend with scene

out vec4 frag_color;

// Same constants as foveated.frag
const float FOVEA_RADIUS = 0.0305;

vec3 heatmap(float t) {
    // 0 = deep blue (sharp), 0.5 = green, 1 = red (max blur)
    vec3 a = mix(vec3(0.0, 0.0, 1.0), vec3(0.0, 1.0, 0.0), smoothstep(0.0, 0.5, t));
    vec3 b = mix(vec3(0.0, 1.0, 0.0), vec3(1.0, 0.0, 0.0), smoothstep(0.5, 1.0, t));
    return t < 0.5 ? a : b;
}

void main() {
    vec2 delta = v_uv - u_gaze;
    float aspect = u_resolution.x / u_resolution.y;
    delta.x *= aspect;
    float half_diag = 0.5 * sqrt(aspect * aspect + 1.0);
    float dist = length(delta) / half_diag;

    float outside = clamp((dist - FOVEA_RADIUS) / (1.0 - FOVEA_RADIUS + 0.001), 0.0, 1.0);
    float blur_t = outside * outside;  // matches blur_px curve in foveated.frag

    vec3 color = heatmap(blur_t);

    // Fade opacity toward centre so scene is still readable in fovea
    float alpha = u_opacity * (0.3 + 0.7 * blur_t);

    frag_color = vec4(color, alpha);
}
