from PhysicalMixin import PhysicalMixin
from IForceApplicator import IForceApplicator


"""
Physics loop:
    Find collisions
    Sum net forces
    Numerically integrate next positions (& rotations?) from accelerations
        Calculate accelerations
        ???
        compute and set next positions
"""


class PhysicsEngine:
    # List of force applicators
    _force_applicators = []

    # What to multiply world scale by.
    # World space is vpython space
    # By default, one unit of world space == 1 meter
    # If world_scalar == 1000 ...
    # (TODO: define what this actually means in a sane way- current assignments its not needed)
    _world_scalar = 1.0

    # References to objects in the world
    _objects = []

    def __init__(self, world_scalar=1.0):
        self._world_scalar = world_scalar

        # TODO: everything else

    # Add a global force applicator
    # This should be applied in order that forces should be calculated (which really shouldn't matter- net force and all that)
    def add_force_applicator(self, force_applicator):
        # if not isinstance(force_applicator, IForceApplicator):
        #    raise UserWarning(
        #        "Got a force applicator that wasn't derived from force applicator base class."
        #    )

        self._force_applicators.append(force_applicator)

    # Iterate for dt. Designed in such a way that this whole process is parallelizable & vertically scalable with more cores.
    def iterate(self, dt):
        # Sweep through force applicators (incl collision applicator), adding a net force for this dt to each object (O(k*n))
        # optimization: this is parallelizable (independent objects for at least gravity and such)
        for force_applicator in self._force_applicators:
            force_applicator.apply_forces(self._objects, dt)

        # Apply the forces for each object (O(n)) as some movement
        # forward euler for now
        for obj in self:
            # get acceleration vector (F = ma)
            net_accel = obj.net_force / obj.mass

            # move according to integration scheme* (add a way to swap this)
            # optimization: this is also parallelizable (independent objects)
            net_vel = dt * net_accel
            obj.add_velocity(net_vel)

            obj.position = obj.position + dt * obj.velocity

            obj.pop_force()  # clear accumulated net force

    def register_object(self, physical_object):
        if not isinstance(physical_object, PhysicalMixin):
            raise UserWarning(
                "Didn't receive a physical object in world object registration function."
            )

        # push a reference
        self._objects.append(physical_object)

        # Allow for chaining
        return self

    # make this class support the Python collections API for ease of use
    def __iter__(self):
        # Do a simple iterator delegation, nothing fancy needed in this case
        # ref: Python Cookbook 3rd Ed., Chapter 4.2
        return iter(self._objects)

    # Get reference to objects set
    @property
    def objects(self):
        return self._objects
