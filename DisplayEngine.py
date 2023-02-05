from vpython import canvas

from PhysicalMixin import np2vpy

# Class that is solely responsible for rendering the world to VPython
# Unfortunately has some side effects because of the way VPython works (it's a global singleton)
class DisplayEngine:
    # Vpython scene
    scene = None

    _objects: list = None

    # constructor
    def __init__(self, **kwargs):
        if "scene" in kwargs:
            self.scene = scene
        else:
            self.scene = canvas()

        self._objects = []

    # Run one iteration of the display loop
    def iterate(self):
        for obj in self._objects:
            obj.pos = np2vpy(obj.position)  # sample numpy position and set vpy position

    def register_object(self, obj):
        self._objects.append(obj)

    def register_canvas(self, c):
        self.scene = c
