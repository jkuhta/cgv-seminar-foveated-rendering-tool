#version 330 core

in vec2 v_uv;

// two textures: stereo side (real IPD) and flat side (IPD=0, no depth)
uniform sampler2D u_stereo;
uniform sampler2D u_flat;
uniform int u_stereo_left;    // 1 = stereo is on the left half, 0 = right
uniform vec2 u_resolution;
uniform float u_blur_strength;
uniform float u_divider_width;  // black centre strip half-width in px (= 1deg fovea radius)
uniform float u_fovea_px;       // blackout circle radius in px (= 5deg eccentricity)

out vec4 frag_color;

// TODO: make these dynamic for different screen sizes
// Values hold for 27" 2560x1440 at 60cm: 1 arcmin = 0.747px

// p2 model: sigma_arcmin = 8.85 * exp(0.04 * deg) - 7.5
float lookup_sigma(float dist_px) {
    float deg = dist_px / 44.8; // 44.8 px = 1 degree
    float sigma_arcmin = 8.85 * exp(0.04 * deg) - 7.5;
    return sigma_arcmin * 0.747; // arcmin -> px
}

// using sigma*2 as radius covers ~95% of the Gaussian so quality is good
// clamps x to stay within one screen half so blur doesn't bleed across the divider
// AI Disclaimer: this method was assisted with AI
vec3 gaussian_blur(sampler2D tex, vec2 uv, float sigma_px, float x_min, float x_max) {
    if (sigma_px < 0.5) return texture(tex, uv).rgb;
    vec2 texel = 1.0 / u_resolution;
    int r = min(int(ceil(sigma_px * 2.0)), 32);
    vec3 accum = vec3(0.0);
    float wsum = 0.0;
    for (int x = -r; x <= r; x++) {
        float wx = exp(- float(x * x) / (2.0 * sigma_px * sigma_px));
        for (int y = -r; y <= r; y++) {
            float w = wx * exp(- float(y * y) / (2.0 * sigma_px * sigma_px));
            vec2 s = uv + vec2(float(x), float(y)) * texel;
            s.x = clamp(s.x, x_min, x_max);
            accum += texture(tex, s).rgb * w;
            wsum += w;
        }
    }
    return accum / wsum;  // normalise so brightness is preserved
}

// AI Disclaimer: this method was assisted with AI
void main() {
    // pixel coordinates from screen centre
    vec2 px = (v_uv - vec2(0.5)) * u_resolution;
    float dist = length(px);

    // black centre divider — separates the two halves visually
    if (abs(px.x) < u_divider_width) { frag_color = vec4(0.0, 0.0, 0.0, 1.0); return; }

    // black fovea circle — forces peripheral-only depth judgment (paper experiment design)
    if (dist < u_fovea_px) { frag_color = vec4(0.0, 0.0, 0.0, 1.0); return; }

    // decide which half of the screen this pixel is on and which texture to use
    bool is_left = v_uv.x < 0.5;
    bool use_stereo = is_left == (u_stereo_left == 1);

    // x clamp range keeps blur sampling within this half only
    float div_uv = u_divider_width / u_resolution.x;
    float x_min = is_left ? 0.0 : (0.5 + div_uv);
    float x_max = is_left ? (0.5 - div_uv) : 1.0;

    float sigma = lookup_sigma(dist) * u_blur_strength;
    vec3 stereo_col = gaussian_blur(u_stereo, v_uv, sigma, x_min, x_max);
    vec3 flat_col = gaussian_blur(u_flat, v_uv, sigma, x_min, x_max);

    frag_color = vec4(use_stereo ? stereo_col : flat_col, 1.0);
}