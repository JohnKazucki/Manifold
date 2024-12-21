float diffuse_light(vec3 positionWS, vec3 normalWS, vec3 lightPosition)
{
    vec3 lightDirection = lightPosition-positionWS;
    float dist = length(lightDirection);
    lightDirection = normalize(lightDirection);

    float diff = dot(normalWS,lightDirection);
    diff = clamp(diff,0.,1.); 

    diff *= 1/(dist*dist);

    return diff;
}

float specular_light(vec3 positionWS, vec3 normalWS, vec3 lightPosition, vec3 eyePosition, float shinyness)
{
    vec3 toLight = normalize(lightPosition-positionWS);
    vec3 toEye = normalize(eyePosition-positionWS);
    vec3 reflectedLightDir = normalize(reflect(-toLight, normalWS));
    float spec = pow(max(dot(toEye, reflectedLightDir), 0.0), shinyness);
    return spec;
}

void main()
{
    vec3 surface_col = vec3(.4, .7, .5);
    vec3 ambient_col = vec3(0.2, 0.2, 0.3);
    float ambient_strength = .7;
    vec3 ambient = ambient_col * ambient_strength;

    float diff = diffuse_light(positionWS, normalWS, lightPos);
    vec3 diffuse = diff*lightColor*lightEnergy;

    float spec = specular_light(positionWS, normalWS, lightPos, viewPos, 64);
    float specularStrength = lightEnergy;
    vec3 specular = specularStrength * spec*lightColor;
    
    vec3 color = (ambient+diffuse+specular)*surface_col;
    FragColor = vec4(color, 1.0);
}
