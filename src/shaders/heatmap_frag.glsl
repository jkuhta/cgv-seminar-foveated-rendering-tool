#version 330 core

in vec2 v_uv;

uniform vec2  u_resolution;
uniform vec2  u_gaze;
uniform float u_opacity;

out vec4 frag_color;

// TODO: make these dynamic for different screen sizes
// hardcoded for 27" 2560x1440 at 60cm viewing distance
const float R_FOVEA = 45.0;
const float R_10DEG = 453.0;
const float R_20DEG = 935.0;
const float RING_W  = 2.0;

// p2 model: sigma_arcmin = 8.85 * exp(0.04 * deg) - 7.5
float lookup_sigma(float dist_px) {
    float deg = dist_px / 44.8; // 44.8 px = 1 degree
    float sigma_arcmin = 8.85 * exp(0.04 * deg) - 7.5;
    return sigma_arcmin * 0.747; // arcmin -> px
}

const float MAX_SIGMA = 9.11;  // sigma at 20deg in px — used to normalise t

vec3 heatmap(float t) {
    if (t < 0.5)
        return mix(vec3(0.0, 0.0, 1.0), vec3(0.0, 1.0, 0.0), t * 2.0);
    return mix(vec3(0.0, 1.0, 0.0), vec3(1.0, 0.0, 0.0), (t - 0.5) * 2.0);
}

void main() {
    vec2  px      = (v_uv - u_gaze) * u_resolution;
    float dist_px = length(px);

    // t follows the actual paper blur curve, not linear distance
    float sigma = lookup_sigma(dist_px);
    float t     = clamp(sigma / MAX_SIGMA, 0.0, 1.0);
    vec3  color = heatmap(t);

    // more transparent near centre so the scene is still readable in the fovea
    float alpha = u_opacity * (0.2 + 0.8 * t);

    // draw eccentricity rings on top — white at fovea, yellow at 10deg, orange at 20deg
    if (abs(dist_px - R_FOVEA) < RING_W) { color = vec3(1.0);           alpha = 0.95; }
    if (abs(dist_px - R_10DEG) < RING_W) { color = vec3(1.0, 0.9, 0.0); alpha = 0.95; }
    if (abs(dist_px - R_20DEG) < RING_W) { color = vec3(1.0, 0.5, 0.0); alpha = 0.95; }

    frag_color = vec4(color, alpha);
}