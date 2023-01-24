import numpy as np

from enum import Enum

from vpython import vector


def np2vpy(np_vec):
    return vector(np_vec[0], np_vec[1], np_vec[2])


def vpy2np(vpy_vec):
    return np.array([vpy_vec.x, vpy_vec.y, vpy_vec.z])


# Enum for a quick differentiation between Physical* classes
PhysicalPrimitiveType = Enum(
    "physical_primitive_type",
    [
        "SPHERE",
        "BOX",
    ],
)


class PhysicalMixin:
    # Mass, kg
    _mass = 0.0

    # Coefficient of static friction, dimensionless
    _coeff_static_friction = 0.0

    # Coefficient of dynamic friction, dimensionless
    _coeff_dynamic_friction = 0.0

    # Coefficient of restitution, e.g. bounciness. dimensionless
    _coeff_restitution = 0.0

    # Net force vector
    # World engine accumulates this over a time period(s) before eventually clearing it and applying
    # the acceleration
    _net_force = np.array([0.0, 0.0, 0.0])

    # Coefficient of drag. None by default for this shapeless class
    _coeff_drag = 0.0

    # Real position, numpy
    _position = np.array([0.0, 0.0, 0.0])

    # Real velocity, nump
    _velocity = np.array([0.0, 0.0, 0.0])

    _static = False

    # Crossectional area in drag. Limitation, assumed to be static.
    _crosssectional_area = 0

    def __init__(self, **kwargs):
        # print('PhysicalMixin::__init__')
        if "mass" in kwargs:
            if kwargs["mass"] < 0:
                raise UserWarning(
                    "Negative mass detected; sorry, but no Alcubierre drives are allowed in this universe!"
                )

            self.mass = kwargs["mass"]

        # https://en.wikipedia.org/wiki/Friction#Coefficient_of_friction
        # Static friction
        if "coeff_static_friction" in kwargs:
            self._coeff_static_friction = kwargs["coeff_static_friction"]

        # Dynamic friction
        if "coeff_dynamic_friction" in kwargs:
            self._coeff_dynamic_friction = kwargs["coeff_dynamic_friction"]

        # https://en.wikipedia.org/wiki/Coefficient_of_restitution
        # Bounciness
        if "coeff_restitution" in kwargs:
            self._coeff_restitution = kwargs["coeff_restitution"]

        # Setup numpy "shadow" versions of physical constants
        # These can be updated out of tune with vpython-related things
        # vpython loop will sample this for display out of sync with the actual updates
        if "pos" in kwargs:
            self.position = vpy2np(kwargs["pos"])

        if "velocity" in kwargs:
            self._velocity = kwargs["velocity"]

        if "static" in kwargs:
            self._static = kwargs["static"]

    @property
    def mass(self):  # get mass
        return self._mass

    @mass.setter
    def mass(self, value):  # Set mass
        if value < 0:
            raise UserWarning(
                "Negative mass detected; sorry, but no Alcubierre drives are allowed in this universe!"
            )

        self._mass = value

    # get vpy position for visualization
    # TODO: Should this class know what VPython is?
    @property
    def vpy_pos(self):
        return np2vpy(self._position)

    # set numpy (physics) position
    @property
    def position(self):
        return self._position

    # get numpy (physics) position
    @position.setter
    def position(self, value):
        self._position = value

    def add_force(self, np_vec):
        self._net_force += np_vec

    # get numpy (physics) net force
    @property
    def net_force(self):
        return self._net_force

    # Add velocity to the object
    def add_velocity(self, value):
        self._velocity += value
