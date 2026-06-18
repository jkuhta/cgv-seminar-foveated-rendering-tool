#version 330 core

in vec2 v_uv;

uniform sampler2D u_tex;
uniform vec2 u_resolution;
uniform float u_blur_strength;
uniform vec2 u_gaze;

// Fovea radius from literature (Wandell 1995; Kergassner et al. 2025):
// 2deg visual angle total (1deg radius), viewer at 60cm, 27" monitor (2560x1440).
// fovea_radius_px = tan(1deg) * 60cm * (2560px / 59.8cm) = 44.8px
// Expressed as fraction of screen half-diagonal (1468px): 44.8/1468 = 0.0305
const float FOVEA_RADIUS = 0.0305;

out vec4 frag_color;

void main() {
    vec2 delta = v_uv - u_gaze;
    float aspect = u_resolution.x / u_resolution.y;
    delta.x *= aspect;
    float half_diag = 0.5 * sqrt(aspect * aspect + 1.0);
    float dist = length(delta) / half_diag;

    float outside = clamp((dist - FOVEA_RADIUS) / (1.0 - FOVEA_RADIUS + 0.001), 0.0, 1.0);
    float blur_px = outside * outside * u_blur_strength;

    vec3 color = texture(u_tex, v_uv).rgb;

    if (blur_px >= 0.5) {
        vec2 texel = 1.0 / u_resolution;
        vec3 accum = vec3(0.0);
        float count = 0.0;
        int r = min(int(ceil(blur_px)), 64);
        for (int x = -r; x <= r; x++) {
            for (int y = -r; y <= r; y++) {
                float d2 = float(x * x + y * y);
                if (d2 <= blur_px * blur_px) {
                    accum += texture(u_tex, v_uv + vec2(float(x), float(y)) * texel).rgb;
                    count += 1.0;
                }
            }
        }
        color = accum / count;
    }

    frag_color = vec4(color, 1.0);
}
