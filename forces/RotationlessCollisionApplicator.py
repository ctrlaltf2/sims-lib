from IForceApplicator import IForceApplicator
from Collision import could_collide, does_collide

# Applies collision forces to objects, no rotations or fancy moment of inertia stuff supported.
# Elastic collisions only.
class RotationlessCollisionApplicator(IForceApplicator):
    def __init__(self):
        return

    # Apply forces to world objects as relevant
    def apply_forces(self, objects, dt):
        # optimization: this is parallelizable
        for a in range(len(objects)):
            for b in range(a + 1, len(objects)):
                aObj = objects[a]
                bObj = objects[b]

                # If the two objects *could* collide (cheap), then check if they actually do (expensive)
                if not could_collide(aObj, bObj):
                    continue

                if does_collide(aObj, bObj):
                    # Solve two-body linear collision, applying force to both objects
                    # ref: PHYS 0174
                    # and https://phys.libretexts.org/Courses/Muhlenberg_College/MC%3A_Physics_121_-_General_Physics_I/10%3A_Linear_Momentum_and_Collisions/10.08%3A_Collisions_in_Multiple_Dimensions

                    aObj_vel_f = (
                        (aObj.mass - bObj.mass) * aObj.velocity
                        + 2 * bObj.mass * bObj.velocity
                    ) / (aObj.mass + bObj.mass)

                    bObj_vel_f = (
                        (bObj.mass - aObj.mass) * bObj.velocity
                        + 2 * aObj.mass * aObj.velocity
                    ) / (aObj.mass + bObj.mass)

                    aObj_momentum_st = aObj.mass * aObj.velocity
                    aObj_momentum_after = aObj.mass * (aObj.velocity + aObj_vel_f)

                    bObj_momentum_st = bObj.mass * bObj.velocity
                    bObj_momentum_after = bObj.mass * (bObj.velocity + bObj_vel_f)

                    # F = dp/dt
                    aObj_force = (aObj_momentum_after - aObj_momentum_st) / dt
                    bObj_force = (bObj_momentum_after - bObj_momentum_st) / dt

                    aObj.add_force(aObj_force)
                    bObj.add_force(bObj_force)
