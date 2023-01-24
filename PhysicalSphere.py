from vpython import sphere, vector
import math

from PhysicalMixin import PhysicalMixin, PhysicalPrimitiveType


class PhysicalSphere(PhysicalMixin, sphere):
    def __init__(self, **kwargs):
        # print('PhysicalSphere::__init__')
        if "mass" in kwargs:
            self.mass = kwargs["mass"]

        self.physical_primitive_type = PhysicalPrimitiveType.SPHERE

        # https://en.wikipedia.org/wiki/Drag_coefficient
        self._coeff_drag = 0.47

        self.crosssectional_area = math.pi * self.radius**2

        # From vpython code, to support vpython shenanigans
        kwargs["_default_size"] = vector(1, 1, 1)
        kwargs["_objName"] = "sphere"

        super(PhysicalSphere, self).__init__(**kwargs)
        super(PhysicalSphere, self).setup(kwargs)

    @property
    def volume(self):
        return 4 / 3.0 * math.pi * self.radius**3
