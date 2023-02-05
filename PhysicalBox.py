from vpython import vector, box

from PhysicalMixin import PhysicalMixin, PhysicalPrimitiveType


class PhysicalBox(PhysicalMixin, box):
    def __init__(self, **kwargs):
        # print('PhysicalBox::__init__')
        if "mass" in kwargs:
            self.mass = kwargs["mass"]

        self.physical_primitive_type = PhysicalPrimitiveType.BOX

        # https://en.wikipedia.org/wiki/Drag_coefficient
        self._coeff_drag = 1.05  # assumes velocity is normal to a face
        # limitation: the above doesn't support rotations technically, that requires a whole fluid simulation

        # From vpython code, to support vpython shenanigans
        kwargs["_default_size"] = vector(1, 1, 1)
        kwargs["_objName"] = "box"

        super(PhysicalBox, self).__init__(**kwargs)
        super(PhysicalBox, self).setup(kwargs)

        # Very bad approximation
        self.crosssectional_area = self.size.x * self.size.z

    @property
    def volume(self):
        sz = self.size
        return sz.x * sz.y * sz.z
