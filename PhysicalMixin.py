import numpy as np

from enum import IntEnum

from vpython import vector


def np2vpy(np_vec):
    return vector(np_vec[0], np_vec[1], np_vec[2])


def vpy2np(vpy_vec):
    return np.array([vpy_vec.x, vpy_vec.y, vpy_vec.z])


# Enum for a quick differentiation between Physical* classes
PhysicalPrimitiveType = IntEnum(
    "physical_primitive_type",
    [
        "SPHERE",
        "BOX",
    ],
)


class PhysicalMixin:
    # Mass, kg
    _mass: float

    # Coefficient of restitution, e.g. bounciness. dimensionless
    _coeff_restitution: float

    # Net force vector
    # World engine accumulates this over a time period(s) before eventually clearing it and applying
    # the acceleration
    _net_force: np.ndarray

    # Coefficient of drag. None by default for this shapeless class
    _coeff_drag: float

    # Real position, numpy
    _position: np.ndarray

    # Previous position
    _prev_position: np.ndarray

    # Real velocity, numpy
    _velocity: np.ndarray

    # No force interaction at all
    _static: bool

    # Force interaction, but this object can't be moved.
    # If it's moving to start though, it keeps moving.
    _immovable: bool

    # Crossectional area in drag. Limitation, assumed to be static.
    _crosssectional_area: float

    # Used for collision optimization, if the object is considered grounded or not and collisions
    # should (temporarily) not apply.
    grounded: bool

    # Average speed over n iterations
    _average_dist: float

    # Average window size
    _n_averages: int = 7

    # Visitor function run by the engine on every iteration
    _visitor = None

    # Visitor state
    _vistior_state = None

    def __init__(self, **kwargs):
        # print('PhysicalMixin::__init__')
        if "mass" in kwargs:
            if kwargs["mass"] < 0:
                raise UserWarning(
                    "Negative mass detected; sorry, but no Alcubierre drives are allowed in this universe!"
                )

            self.mass = kwargs["mass"]
        else:
            self.mass = 1

        # Setup numpy "shadow" versions of physical constants
        # These can be updated out of tune with vpython-related things
        # vpython loop will sample this for display out of sync with the actual updates
        if "pos" in kwargs:
            self._position = vpy2np(kwargs["pos"])
        else:
            self._position = np.array([0.0, 0.0, 0.0])

        if "velocity" in kwargs:
            self._velocity = kwargs["velocity"]
        else:
            self._velocity = np.array([0.0, 0.0, 0.0])

        self._average_dist = 10.0  # hack but it works

        if "static" in kwargs:
            self._static = kwargs["static"]
        else:
            self._static = False

        if "immovable" in kwargs:
            self.immovable = kwargs["immovable"]
        else:
            self.immovable = False

        if "visitor" in kwargs:
            self._visitor = kwargs["visitor"]
            self._visitor_state = {}

        self._net_force = np.array([0.0, 0.0, 0.0])
        self._prev_position = np.array([0.0, 0.0, 0.0])
        self.grounded = False

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

    # get numpy (physics) position
    @property
    def position(self):
        return self._position

    # get numpy (physics) velocity
    @property
    def velocity(self):
        return self._velocity

    # set numpy (physics) velocity
    @velocity.setter
    def velocity(self, value):
        if not self._immovable:
            self._velocity = value

    # Add velocity to the object
    def add_velocity(self, value):
        if not self._immovable:
            self._velocity += value

    # set numpy (physics) position
    @position.setter
    def position(self, value):
        # Update actual position
        self._position = value

    def add_force(self, np_vec):
        self._net_force += np_vec

    # get numpy (physics) net force
    @property
    def net_force(self):
        return self._net_force

    def pop_force(self):
        self._net_force = np.array([0.0, 0.0, 0.0])

    # Cross-sectional area normal to the velocity
    # Used for drag
    @property
    def crosssectional_area(self):
        return self._crosssectional_area

    @crosssectional_area.setter
    def crosssectional_area(self, value):
        self._crosssectional_area = value

    @property
    def coeff_drag(self):
        return self._coeff_drag

    # get if the object is static (unaffected by forces)
    @property
    def static(self):
        return self._static

    # set if object is static
    @static.setter
    def static(self, value):
        self._static = value

    # get if the object is immovable or not
    @property
    def immovable(self):
        return self._immovable

    @immovable.setter
    def immovable(self, value):
        self._immovable = value

    def update_average_movement(self):
        # Update average speed
        dp = self._position - self._prev_position
        dist = np.linalg.norm(dp)
        self._average_dist = (1 / self._n_averages) * dist + (
            1 - 1 / self._n_averages
        ) * self._average_dist

        self._prev_position = self._position

    def on_update(self, dt):
        if self._visitor:
            self._visitor(self._visitor_state, self, dt)
