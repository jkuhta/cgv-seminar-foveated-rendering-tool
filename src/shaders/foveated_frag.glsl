#version 330 core

in vec2 v_uv;

uniform sampler2D u_tex;
uniform vec2 u_resolution;
uniform float u_blur_strength;  // multiplier: 1.0 = approx. paper ideal foveation
uniform vec2 u_gaze;           // gaze point in UV [0..1]

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
// AI Disclaimer: this method was assisted with AI
vec3 gaussian_blur(vec2 uv, float sigma_px) {
    if (sigma_px < 0.5) return texture(u_tex, uv).rgb;  // skip blur if sigma is tiny
    vec2 texel = 1.0 / u_resolution;
    int r = min(int(ceil(sigma_px * 2.0)), 32);
    vec3 accum = vec3(0.0);
    float wsum = 0.0;
    for (int x = -r; x <= r; x++) {
        float wx = exp(- float(x * x) / (2.0 * sigma_px * sigma_px));
        for (int y = -r; y <= r; y++) {
            float w = wx * exp(- float(y * y) / (2.0 * sigma_px * sigma_px));
            accum += texture(u_tex, uv + vec2(float(x), float(y)) * texel).rgb * w;
            wsum += w;
        }
    }
    return accum / wsum;  // normalise so brightness is preserved
}

void main() {
    // pixel distance from gaze point — determines eccentricity
    vec2 px = (v_uv - u_gaze) * u_resolution;
    float dist_px = length(px);

    // look up paper blur sigma for this eccentricity and apply strength multiplier
    float sigma = lookup_sigma(dist_px) * u_blur_strength;

    frag_color = vec4(gaussian_blur(v_uv, sigma), 1.0);
}