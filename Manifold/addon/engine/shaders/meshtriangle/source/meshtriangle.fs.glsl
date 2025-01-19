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
    vec3 toLight = lightPosition-positionWS;
    float dist = length(toLight);
    toLight = normalize(toLight);

    vec3 toEye = normalize(eyePosition-positionWS);
    vec3 reflectedLightDir = normalize(reflect(-toLight, normalWS));
    float spec = pow(max(dot(toEye, reflectedLightDir), 0.0), shinyness);

    float falloff_strength = (512/(512-shinyness));
    spec *= 1/(dist/falloff_strength);

    return spec;
}

void main()
{
    float ambient_strength = .7;
    vec3 ambient = ambientColor * ambient_strength;

    vec3 lightPos;
    float lightEnergy;
    vec3 lightColor;

    vec3 surfaceColor = ModelBlock.surface_color_roughness.xyz;
    float surfaceRoughness = ModelBlock.surface_color_roughness.w;

    vec3 diffuse = vec3(0.0, 0.0, 0.0);
    vec3 specular = vec3(0.0, 0.0, 0.0);

    float specCurve = 10;
    float specularity = 1.0-surfaceRoughness;
    // from https://math.stackexchange.com/questions/297768/how-would-i-create-a-exponential-ramp-function-from-0-0-to-1-1-with-a-single-val
    float specExponent = (exp(specCurve*specularity)-1.0)/(exp(specCurve)-1.0)*512;
    specExponent += 0.0001;

    for(int i=0; i<NumLights; i++)
    {
        lightPos = LightBlock[i].lightPos_Energy.xyz;
        lightEnergy = LightBlock[i].lightPos_Energy.w;
        lightColor = LightBlock[i].lightColor.xyz;   

        float diff = diffuse_light(positionWS, normalWS, lightPos);     
        diffuse += diff*lightEnergy*lightColor;

        float spec = specular_light(positionWS, normalWS, lightPos, viewPos, specExponent);
        float specularStrength = lightEnergy*(specExponent/128);
        specular += specularStrength*spec*lightColor;
    }
    
    vec3 color = (ambient+diffuse+specular)*surfaceColor;
    FragColor = vec4(color, 1.0);
}
