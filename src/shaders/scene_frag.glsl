#version 330 core

in vec3 v_color;
in vec3 v_normal;
in vec3 v_frag_pos;

uniform vec3 u_light_pos;
uniform vec3 u_view_pos;
uniform int u_grayscale;

out vec4 frag_color;

void main() {
    vec3 N = normalize(v_normal);
    vec3 L = normalize(u_light_pos - v_frag_pos);

    float ambient = 0.25;
    float diff = max(dot(N, L), 0.0);

    vec3 V = normalize(u_view_pos - v_frag_pos);
    vec3 R = reflect(-L, N);
    float spec = pow(max(dot(V, R), 0.0), 32.0) * 0.4;

    vec3 lit = v_color * (ambient + diff) + vec3(spec);

    if (u_grayscale == 1) {
        float lum = dot(lit, vec3(0.299, 0.587, 0.114));
        lit = vec3(lum);
    }

    frag_color = vec4(lit, 1.0);
}
