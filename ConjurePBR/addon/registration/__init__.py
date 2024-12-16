import bpy


def register_addon():
    from ..engine import register_render_engines
    register_render_engines()


def unregister_addon():
    from ..engine import unregister_render_engines
    unregister_render_engines()
