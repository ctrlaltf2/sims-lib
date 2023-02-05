import numpy as np

from PhysicalMixin import PhysicalPrimitiveType


# Class to represent a collision event
class Collision:
    def __init__(self, aPos, bPos, depth):
        self.aPos = aPos  # Vector of location of farthest point of A into B
        self.bPos = bPos  # Vector of location of farthest point of B into A
        self.depth = depth  # length of overlap A to B


# Check axis-aligned bounding box intersection before dispatching to more fine-grained collision checks
def could_collide(aObj, bObj):
    aBbox = aObj.bounding_box()
    bBbox = bObj.bounding_box()

    # Figured out 1D case with visualization as aid https://www.desmos.com/calculator/3otpyjpx3y
    #   & moving two dice around in real life to help extend to the 3D case

    # Unoptimized case (optimized involves interleaving the axis checks with the axis min/max finding)
    # TODO: If performance issues still after typechecking removal, optimize this as well
    a_min_x, a_max_x = aBbox[0].x, aBbox[7].x
    a_min_y, a_max_y = aBbox[0].y, aBbox[7].y
    a_min_z, a_max_z = aBbox[0].z, aBbox[7].z

    b_min_x, b_max_x = bBbox[0].x, bBbox[7].x
    b_min_y, b_max_y = bBbox[0].y, bBbox[7].y
    b_min_z, b_max_z = bBbox[0].z, bBbox[7].z

    return (
        a_max_x >= b_min_x
        and a_min_x <= b_max_x
        and a_max_y >= b_min_y
        and a_min_y <= b_max_y
        and a_max_z >= b_min_z
        and a_min_z <= b_max_z
    )


def unitv(v):
    mag = np.linalg.norm(v)
    if mag != 0:
        return v / mag
    else:
        return np.array([0, 0, 0])


def does_collide(aObj, bObj):
    if not could_collide(aObj, bObj):
        return None

    # Double dispatch to simplify code below https://en.wikipedia.org/wiki/Double_dispatch
    if aObj.physical_primitive_type > bObj.physical_primitive_type:
        return does_collide(bObj, aObj)

    # Collision checks between any two primitives
    if aObj.physical_primitive_type == PhysicalPrimitiveType.SPHERE:  # Sphere v. x
        if (
            bObj.physical_primitive_type == PhysicalPrimitiveType.SPHERE
        ):  # Sphere v. Sphere

            # Worked out on paper for equations, email me if you need them
            dist = np.linalg.norm(bObj.position - aObj.position)

            min_radius = aObj.radius + bObj.radius

            if dist < min_radius:  # Collided
                # y-x
                # y-z
                d = bObj.position - aObj.position
                d_hat = unitv(d)

                a_far = aObj.position + aObj.radius * d_hat
                b_far = bObj.position - bObj.radius * d_hat

                depth = np.linalg.norm(b_far - a_far)

                return Collision(a_far, b_far, dist)
            else:
                return None
        elif bObj.physical_primitive_type == PhysicalPrimitiveType.BOX:  # Sphere v. box
            # TODO: Support rotated boxes.
            # Optimization for rotated case: coord xform sphere and box such that box appears axis-aligned then run this same code :)

            # This code assumes that box is axis-aligned
            # Get the box's closest point to the center of the Sphere
            # ref: https://developer.mozilla.org/en-US/docs/Games/Techniques/3D_collision_detection#sphere_vs._aabb
            box_closest = np.array(
                [
                    max(
                        bObj.position[0] - bObj.size.x / 2,
                        min(aObj.position[0], bObj.position[0] + bObj.size.x / 2),  #
                    ),
                    max(
                        bObj.position[1] - bObj.size.y / 2,
                        min(aObj.position[1], bObj.position[1] + bObj.size.y / 2),
                    ),
                    max(
                        bObj.position[2] - bObj.size.z / 2,
                        min(aObj.position[2], bObj.position[2] + bObj.size.z / 2),
                    ),
                ]
            )

            distance_box_to_sphere_center = np.linalg.norm(box_closest - aObj.position)

            if distance_box_to_sphere_center < aObj.radius:
                # Equations (drawings?) again worked out on paper, email me if you need them.
                # Vector from closest box coordinate to sphere center to box center
                black = bObj.position - box_closest

                # Location of farthest sphere point into box
                green = aObj.position + aObj.radius * unitv(black)

                # Depth of shapes relative to their farthest-intersection points
                d = np.linalg.norm(green - box_closest)

                return Collision(box_closest, green, d)
            else:
                return None

    elif aObj.physical_primitive_type == PhysicalPrimitiveType.BOX:
        # Box v. x checks (none thus far)
        raise UserWarning(
            "Code shouldn't reach here, unless new primitives added or bug in param swapping code."
        )

    pass
