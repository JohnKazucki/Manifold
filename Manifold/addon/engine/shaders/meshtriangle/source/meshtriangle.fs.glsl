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
    vec3 lightPos = LightBlock[0].lightPos_Energy.xyz;
    float lightEnergy = LightBlock[0].lightPos_Energy.w;
    vec3 lightColor = LightBlock[0].lightColor.xyz;

    float ambient_strength = .7;
    vec3 ambient = ambientColor * ambient_strength;

    float diff = diffuse_light(positionWS, normalWS, lightPos);
    vec3 diffuse = diff*lightColor*lightEnergy;

    float specCurve = 10;
    float specularity = 1.0-surfaceRoughness;
    // from https://math.stackexchange.com/questions/297768/how-would-i-create-a-exponential-ramp-function-from-0-0-to-1-1-with-a-single-val
    float specExponent = (exp(specCurve*specularity)-1.0)/(exp(specCurve)-1.0)*512;
    specExponent += 0.0001;

    float spec = specular_light(positionWS, normalWS, lightPos, viewPos, specExponent);
    float specularStrength = lightEnergy*(specExponent/128);
    vec3 specular = specularStrength*spec * lightColor;
    
    vec3 color = (ambient+diffuse+specular)*surfaceColor;
    FragColor = vec4(color, 1.0);
}
