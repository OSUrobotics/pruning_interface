# version 140 
attribute highp vec3 vertexPos; 

void main(void)
{
    gl_Position = vec4(vertexPos, 1.0);
}