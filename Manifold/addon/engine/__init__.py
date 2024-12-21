import bpy

from .renderer import ManifoldRenderEngine


classes = (
    ManifoldRenderEngine,
)


def get_panels():

    from bl_ui import(
        properties_data_light
    )

    exclude_panels = {
        'VIEWLAYER_PT_filter',
        'VIEWLAYER_PT_layer_passes',
        'RENDER_PT_freestyle',
        'RENDER_PT_simplify',
        'RENDER_PT_gpencil',

        'DATA_PT_camera_stereoscopy'
        'DATA_PT_camera_dof',
        'DATA_PT_camera_dof_aperture'

        'DATA_PT_preview',
        'DATA_PT_light',
        'NODE_DATA_PT_light',
    }

    include_panels = {
        properties_data_light.DATA_PT_EEVEE_light, #piggybacking off of Eevee TODO : don't, write bespoke panel to draw light data
    }

    panels = []
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels + list(include_panels)


def register_render_engines():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    for panel in get_panels():
        panel.COMPAT_ENGINES.add('MANIFOLD')

def unregister_render_engines():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    for panel in get_panels():
        if 'MANIFOLD' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('MANIFOLD')
