import bpy

from .renderer import ConjurePBRRenderEngine


classes = (
    ConjurePBRRenderEngine,
)


def get_panels():
    exclude_panels = {
        'VIEWLAYER_PT_filter',
        'VIEWLAYER_PT_layer_passes',
    }

    panels = []
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels


def register_render_engines():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    for panel in get_panels():
        panel.COMPAT_ENGINES.add('CONJUREPBR')


def unregister_render_engines():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    for panel in get_panels():
        if 'CONJUREPBR' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('CONJUREPBR')
