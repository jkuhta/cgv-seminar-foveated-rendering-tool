#version 330 core

in vec2 v_uv;

uniform sampler2D u_left;   // left eye render
uniform sampler2D u_right;  // right eye render

out vec4 frag_color;

void main() {

    vec3 left = texture(u_left, v_uv).rgb;
    vec3 right = texture(u_right, v_uv).rgb;

    // Use luminance for left (avoids color clashes through the red lens)
    float left_lum = dot(left, vec3(0.299, 0.587, 0.114));

    // render anaglyph
    frag_color = vec4(left_lum, right.g, right.b, 1.0);
}
