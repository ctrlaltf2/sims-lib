from vpython import vector, box

from PhysicalMixin import PhysicalMixin, PhysicalPrimitiveType


class PhysicalBox(box, PhysicalMixin):
    def __init__(self, **args):
        if "mass" in args:
            self.mass = args["mass"]

        self.physical_primitive_type = PhysicalPrimitiveType.BOX

        # https://en.wikipedia.org/wiki/Drag_coefficient
        self._coeff_drag = 1.05  # assumes velocity is normal to a face
        # limitation: the above doesn't support rotations technically, that requires a whole fluid simulation

        # From vpython code, to support vpython shenanigans
        args["_default_size"] = vector(1, 1, 1)
        args["_objName"] = "box"
        super(PhysicalBox, self).setup(args)

    @property
    def volume(self):
        sz = self.size
        return sz.x * sz.y * sz.z
