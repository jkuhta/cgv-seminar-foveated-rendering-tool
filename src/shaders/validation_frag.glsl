#version 330 core

in vec2 v_uv;

uniform sampler2D u_stereo;
uniform sampler2D u_flat;
uniform int u_stereo_left;
uniform vec2 u_resolution;
uniform float u_blur_strength;
uniform float u_divider_width;  // half-width of black strip in pixels
uniform float u_fovea_px;       // radius of black fovea circle in pixels

out vec4 frag_color;

// Box blur clamped to stay within x bounds [x_min, x_max] in UV space
vec3 box_blur_clamped(sampler2D tex, vec2 uv, float radius_px,
                      float x_min_uv, float x_max_uv) {
    vec2 texel = 1.0 / u_resolution;
    vec3 accum = vec3(0.0);
    float count = 0.0;
    int r = min(int(ceil(radius_px)), 48);
    for (int x = -r; x <= r; x++) {
        for (int y = -r; y <= r; y++) {
            if (float(x * x + y * y) <= radius_px * radius_px) {
                vec2 s = uv + vec2(float(x), float(y)) * texel;
                s.x = clamp(s.x, x_min_uv, x_max_uv);
                accum += texture(tex, s).rgb;
                count += 1.0;
            }
        }
    }
    return accum / count;
}

void main() {
    vec2 px = (v_uv - vec2(0.5)) * u_resolution;
    float divider_uv = u_divider_width / u_resolution.x;

    // Black centre divider
    if (abs(px.x) < u_divider_width) {
        frag_color = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    // Black fovea circle
    float dist_center = length(px);
    if (dist_center < u_fovea_px) {
        frag_color = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    // Foveated blur — grows from screen centre outward
    float aspect = u_resolution.x / u_resolution.y;
    vec2 delta = v_uv - vec2(0.5);
    delta.x *= aspect;
    float half_diag = 0.5 * sqrt(aspect * aspect + 1.0);
    float dist_norm = length(delta) / half_diag;
    // 27" monitor at 60cm: fovea = 1deg radius = 44.8px / 1468px half-diag = 0.0305
    const float FOVEA_RADIUS = 0.0305;
    float outside = clamp((dist_norm - FOVEA_RADIUS) / (1.0 - FOVEA_RADIUS + 0.001), 0.0, 1.0);
    float blur_px = outside * outside * u_blur_strength;

    // Clamp blur sampling to stay within the correct screen half
    bool is_left = (v_uv.x < 0.5);
    float x_min = is_left ? 0.0 : (0.5 + divider_uv);
    float x_max = is_left ? (0.5 - divider_uv) : 1.0;
    bool use_stereo = (is_left == (u_stereo_left == 1));

    vec3 stereo_color, flat_color;
    if (blur_px < 0.5) {
        stereo_color = texture(u_stereo, v_uv).rgb;
        flat_color = texture(u_flat, v_uv).rgb;
    } else {
        stereo_color = box_blur_clamped(u_stereo, v_uv, blur_px, x_min, x_max);
        flat_color = box_blur_clamped(u_flat, v_uv, blur_px, x_min, x_max);
    }

    vec3 color = use_stereo ? stereo_color : flat_color;

    frag_color = vec4(color, 1.0);
}
