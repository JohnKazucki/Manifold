
class BaseMaterial:
    """Minimal representation needed to shade a surface"""
    def __init__(self, name, color, roughness):
        self.name = name
        self.surface_color = color
        self.surface_roughness = roughness
