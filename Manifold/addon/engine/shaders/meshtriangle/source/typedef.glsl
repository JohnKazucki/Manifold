struct LightData // 8 floats
{
    vec4 lightPos_Energy;

    vec4 lightColor;
};

struct ModelData // 36 floats
{
    mat4 MVP;
    
    mat4 ModelMatrix;

    vec4 surface_color_roughness;
};
