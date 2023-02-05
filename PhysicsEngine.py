from math import isclose

from PhysicalMixin import PhysicalMixin
from IForceApplicator import IForceApplicator
from Collision import does_collide, could_collide


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
    _force_applicators: list = None

    _do_collisions: bool

    # References to objects in the world
    _objects: list = None

    # Coefficient of restitution for all collisions in the world
    _coeff_restitution: float

    def __init__(self, **kwargs):
        self._objects = []
        self._force_applicators = []

        if "coeff_restitution" in kwargs:
            self._coeff_restitution = kwargs["coeff_restitution"]
        else:
            self._coeff_restitution = 1.0

        if "do_collisions" in kwargs:
            self._do_collisions = kwargs["do_collisions"]
        else:
            self._do_collisions = False

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
        # print('position before collisions =', obj.position)
        self.apply_collisions(dt)
        # print('position after collisions =', obj.position)
        # print()

        for force_applicator in self._force_applicators:
            force_applicator.apply_forces(self._objects, dt)

        # Apply the forces for each object (O(n)) as some movement
        # forward euler for now
        for obj in self:
            if obj.immovable:
                obj.pop_force()
                continue

            # must be done post-collision-resolution, pre next-frame-movement-update
            # the only time that the object is guaranteed not to be colliding
            # print(obj.position)
            obj.update_average_movement()

            # get acceleration vector (F = ma)
            net_accel = obj.net_force / obj.mass

            # print('net_force = ', obj.net_force)

            # print()

            # move according to integration scheme* (add a way to swap this)
            # optimization: this is also parallelizable (independent objects)
            # print('velocity before =', obj.velocity)
            net_vel = dt * net_accel
            obj.add_velocity(net_vel)
            # print('velocity after  =', obj.velocity)

            # print()

            # print('position before =', obj.position)

            # prev_position = obj.position
            obj.position = obj.position + dt * obj.velocity
            # print('position after =', obj.position)

            # print()

            # Prevent continuous collision detections being picked up for a gravity-bound object resting on a static object
            """
            # Use average speed
            avg_speed = obj._average_dist / dt

            if(not obj.grounded):
                if(isclose(avg_speed, 0.0, abs_tol=6e-03)):
                    print('Grounding', obj, ' from low speed.')
                    print('obj.average_speed = ', avg_speed)
                    obj.grounded = True
                    obj.velocity = np.array([0.0, 0.0, 0.0])
                else:
                    # print('not grounding, threshold not hit.')
                    # print('obj.average_speed = ', obj._average_speed)
                    pass
            elif(isclose(avg_speed, 0.0, abs_tol=6e-03)):
                print('Could\'ve grounded but didn\'t because apparently already was')
                pass
            else:
                # print('No grounding.')
                pass
            """

            obj.pop_force()  # clear accumulated net force
            obj.on_update(dt)

    def register_object(self, physical_object):
        if not isinstance(physical_object, PhysicalMixin):
            raise UserWarning(
                "Didn't receive a physical object in world object registration function."
            )

        # push a reference
        self._objects.append(physical_object)

        # Allow for chaining
        return self

    def apply_collisions(self, dt):
        for a in range(len(self._objects)):
            for b in range(a + 1, len(self._objects)):
                aObj = self._objects[a]
                bObj = self._objects[b]

                a_grounded = aObj.grounded or aObj.immovable or aObj.static
                b_grounded = bObj.grounded or bObj.immovable or bObj.static

                if a_grounded and b_grounded:
                    # print('Skipping because both grounded')
                    continue

                if a_grounded:
                    pass
                    # print('a is grounded')

                # If the two objects *could* collide (cheap), then check if they actually do (expensive)
                if not could_collide(aObj, bObj):
                    # print(a, b, 'could not collide.')
                    # print(aObj.position, bObj.position, 'could not collide.')
                    continue

                possible_collision = does_collide(aObj, bObj)

                if possible_collision is not None:
                    # print('Collision found')
                    # Solve two-body linear collision, applying force to both objects
                    # ref: PHYS 0174
                    # and https://phys.libretexts.org/Courses/Muhlenberg_College/MC%3A_Physics_121_-_General_Physics_I/10%3A_Linear_Momentum_and_Collisions/10.08%3A_Collisions_in_Multiple_Dimensions

                    """Old inelastic equations
                    aObj_vel_f = (
                        (aObj.mass - bObj.mass) * aObj.velocity
                        + 2 * bObj.mass * bObj.velocity
                    ) / (aObj.mass + bObj.mass)

                    bObj_vel_f = (
                        (bObj.mass - aObj.mass) * bObj.velocity
                        + 2 * aObj.mass * aObj.velocity
                    ) / (aObj.mass + bObj.mass)
                    """

                    # New elastic equations
                    # ref: https://en.wikipedia.org/wiki/Coefficient_of_restitution#Speeds_after_impact
                    total_initial_momentum = (
                        aObj.mass * aObj.velocity + bObj.mass * bObj.velocity
                    )
                    aObj_vel_f = (
                        total_initial_momentum
                        + bObj.mass
                        * self._coeff_restitution
                        * (bObj.velocity - aObj.velocity)
                    ) / (aObj.mass + bObj.mass)

                    bObj_vel_f = (
                        total_initial_momentum
                        + aObj.mass
                        * self._coeff_restitution
                        * (aObj.velocity - bObj.velocity)
                    ) / (aObj.mass + bObj.mass)

                    # Correct x vel
                    aObj_vel_f[0] = -aObj_vel_f[0]
                    bObj_vel_f[0] = -bObj_vel_f[0]

                    # Correct positions too
                    # basic idea: if(overlapping) { don't() }

                    # Rewind overlapping objects by a little bit more than one dt
                    # Kinda a hack but good enough
                    rewind_dt = 1.01 * dt

                    if (not a_grounded) and (not b_grounded):  # a and b can move
                        while does_collide(aObj, bObj) is not None:
                            aObj.position = (
                                aObj.position - rewind_dt / 2 * aObj.velocity
                            )
                            bObj.position = (
                                bObj.position - rewind_dt / 2 * bObj.velocity
                            )

                        # print('Ungrounding both')
                        # aObj.grounded = False
                        # bObj.grounded = False
                    elif a_grounded:  # -> just b can move, so b moves
                        while does_collide(aObj, bObj) is not None:
                            bObj.position = bObj.position - rewind_dt * bObj.velocity

                        # print('Ungrounding bObj')
                        # bObj.grounded = False
                    elif b_grounded:  # -> just a can move, so a moves
                        while does_collide(aObj, bObj) is not None:
                            aObj.position = aObj.position - rewind_dt * aObj.velocity

                        # print('Ungrounding aObj')
                        # aObj.grounded = False
                    else:
                        # print('oops two objects that are grounded just collided- undefined behavior; moving both')
                        pass

                    aObj.velocity = aObj_vel_f
                    bObj.velocity = bObj_vel_f

                    # print('after collide: a, b vels = ', aObj_vel_f, bObj_vel_f)

                    """
                    bToa = possible_collision.aPos - possible_collision.bPos

                    # print('before a pos, b pos = ', aObj.position, bObj.position)
                    if (not a_grounded) and (not b_grounded): # a and b can move
                        # * 1.05 for some nice leeway
                        # in case of floating point errors causing the displacement not to be enough (and making a collision loop)
                        aObj.position = aObj.position + (1.05 * bToa) / 2
                        bObj.position = bObj.position - (1.05 * bToa) / 2
                    elif a_grounded: # -> just b can move, so b moves
                        bObj.position = bObj.position - (1.05 * bToa)
                    elif b_grounded: # -> just a can move, so a moves
                        aObj.position = aObj.position + (1.05 * bToa)
                    else:
                        # print('oops two objects that are grounded just collided- undefined behavior; moving both')
                        aObj.position = aObj.position + (1.05 * bToa) / 2
                        bObj.position = bObj.position - (1.05 * bToa) / 2
                    """

                    # print('after  a pos, b pos = ', aObj.position, bObj.position)

    # make this class support the Python collections API for ease of use
    def __iter__(self):
        # Do a simple iterator delegation, nothing fancy needed in this case
        # ref: Python Cookbook 3rd Ed., Chapter 4.2
        return iter(self._objects)

    # Get reference to objects set
    @property
    def objects(self):
        return self._objects
