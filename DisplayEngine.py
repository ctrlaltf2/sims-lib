from vpython import canvas

from PhysicalMixin import np2vpy

# Class that is solely responsible for rendering the world to VPython
# Unfortunately has some side effects because of the way VPython works (it's a global singleton)
class DisplayEngine:
    # Vpython scene
    scene = None

    _objects = []

    # constructor
    def __init__(self):
        self.scene = canvas()

    # Run one iteration of the display loop
    def iterate(self):
        for obj in self._objects:
            obj.pos = np2vpy(obj.position)  # sample numpy position and set vpy position

    def register_object(self, obj):
        self._objects.append(obj)
