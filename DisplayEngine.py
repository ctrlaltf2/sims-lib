# Class that is solely responsible for rendering the world to VPython
# Unfortunately has some side effects because of the way VPython works (it's a global singleton)
class DisplayEngine:
    _display_rate = 60  # Hz

    _objects = []

    # constructor
    def __init__(self, **kwargs):
        if "display_rate" in kwargs:
            assert kwargs["display_rate"] > 0  # display rates are positive.
            self._display_rate = kwargs["display_rate"]

    # Run one iteration of the display loop
    def iterate(self):
        for obj in self._objects:
            obj.pos = obj.position  # sample numpy position and set vpy position

    def add_object(self, obj):
        self._objects.append(obj)
