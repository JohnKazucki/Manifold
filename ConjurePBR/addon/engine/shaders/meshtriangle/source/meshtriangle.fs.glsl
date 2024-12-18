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

void main()
{
    float diff = diffuse_light(positionWS, normalWS, normalize(vec3(3, 3, 3)) );

    vec3 color = mix(vec3(0,0,0), vec3(.4, .7, .5), diff);
    color = mix(color, vec3(1,1,1), pow(diff, 32));

    FragColor = vec4(color, 1.0);
}