void main()
{
    positionWS = (ModelMatrix * vec4(Position, 1.0)).xyz;

    gl_Position = MVP * vec4(Position, 1.0);
    gl_Position.z = gl_Position.z - 0.000001 * gl_Position.w;

    normalWS = (ModelMatrix * vec4(Normal, 0)).xyz;
}