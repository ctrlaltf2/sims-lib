from vpython import sphere, vector
import math

from PhysicalMixin import PhysicalMixin, PhysicalPrimitiveType


class PhysicalSphere(sphere, PhysicalMixin):
    def __init__(self, **args):
        if "mass" in args:
            self.mass = args["mass"]

        self.physical_primitive_type = PhysicalPrimitiveType.SPHERE

        # https://en.wikipedia.org/wiki/Drag_coefficient
        self._coeff_drag = 0.47

        # From vpython code, to support vpython shenanigans
        args["_default_size"] = vector(1, 1, 1)
        args["_objName"] = "sphere"
        super(PhysicalSphere, self).setup(args)

    @property
    def volume(self):
        return 4 / 3.0 * math.pi * self.radius**3


