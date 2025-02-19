# Manifold
 Rendering engine for Blender 4.3 Purely a testing project.<br/> 
 Gets sluggish when editing meshes with ~50k triangles or more.<br/> 

 ![image](https://github.com/user-attachments/assets/28011a1d-c4d0-4a4e-980e-f0b6f9f59823)

## Requirements
* Blender 4.3 (may work on any version since 4.0)
* Windows/Linux (MacOS might work as well, let me know!)

## Features
* Non PBR rendering
* F12 rendering (stills and animations)
* Multiple Meshes
* One Material per Mesh
* Per Material color and roughness
* Supported Light Types: Point
* Multiple Lights
* Per Light color and power

## Planned Features
* Multiple materials per mesh
* Sun and Spot light types
* Cast shadows
* PBR (maybe)
* Basic transparency (maybe)

## Special Thanks
* McManning for the <code>micro.py</code> version of his Scratchpad rendering engine (written in Blender bgl API)<br/> 
  it served as a guide for this gpu API version<br/> 
  https://github.com/McManning/Scratchpad
