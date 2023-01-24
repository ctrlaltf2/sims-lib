import numpy as np

from PhysicalMixin import PhysicalPrimitiveType


# Class to represent a collision event
class Collision:
    def __init__(self, aPos, bPos, vAtoB, depth):
        self.aPos = aPos  # Vector (tensor..?) of location of farthest point of A into B
        self.bPos = bPos  # Vector of location of farthest point of B into A
        self.vAtoB = vAtoB  # Direction vector pointing from A to B
        self.depth = depth  # Length of A to B essentally


# Check axis-aligned bounding box intersection before dispatching to more fine-grained collision checks
def could_collide(aObj, bObj):
    # list in format [x0, y0, z0, x1, y1, z1]
    aBbox = aObj.bounding_box()
    bBbox = bObj.bounding_box()

    # Figured out 1D case with visualization as aid https://www.desmos.com/calculator/3otpyjpx3y
    #   & moving two dice around in real life to help extend to the 3D case

    # Unoptimized case (optimized involves interleaving the axis checks with the axis min/max finding)
    # TODO: If performance issues still after typechecking removal, optimize this as well
    a_min_x, a_max_x = sorted([aBbox[0], aBbox[3]])
    a_min_y, a_max_y = sorted([aBbox[1], aBbox[4]])
    a_min_z, a_max_z = sorted([aBbox[2], aBbox[5]])

    b_min_x, b_max_x = sorted([bBbox[0], bBbox[3]])
    b_min_y, b_max_y = sorted([bBbox[1], bBbox[4]])
    b_min_z, b_max_z = sorted([bBbox[2], bBbox[5]])

    return (
        a_max_x >= b_min_x
        and a_min_x <= b_max_x
        and a_max_y >= b_min_y
        and a_min_y <= b_max_y
        and a_max_z >= b_min_z
        and a_min_z <= b_max_z
    )


def does_collide(aObj, bObj):
    if not could_collide(aObj, bObj):
        return None

    # Double dispatch to simplify code below https://en.wikipedia.org/wiki/Double_dispatch
    if aObj.physical_primitive_type > bObj.primitive_type:
        return does_collide(bObj, aObj)

    # Collision checks between any two primitives
    if aObj.physical_primitive_type == PhysicalPrimitiveType.SPHERE:  # Sphere v. x
        if (
            bObj.physical_primitive_type == PhysicalPrimitiveType.SPHERE
        ):  # Sphere v. Sphere
            dist = np.linalg.norm(bObj.position - aObj.position)

            min_radius = aObj.radius + bObj.radius

            if dist < min_radius:  # Collided
                # y-x
                # y-z

                return True
        elif bObj.physical_primitive_type == PhysicalPrimitiveType.BOX:  # Sphere v. box
            # TODO: Support rotated boxes.
            # Optimization for rotated case: coord xform sphere and box such that box appears axis-aligned then run this same code :)

            # This code assumes that box is axis-aligned
            # Get the box's closest point to the center of the Sphere
            # ref: https://developer.mozilla.org/en-US/docs/Games/Techniques/3D_collision_detection#sphere_vs._aabb
            box_closest = np.array(
                [
                    max(
                        bObj.position[0] - bObj.size[0] / 2,
                        min(aObj.position[0], bObj.position[0] + bObj.size[0] / 2),  #
                    ),
                    max(
                        bObj.position[1] - bObj.size[1] / 2,
                        min(aObj.position[1], bObj.position[1] + bObj.size[1] / 2),
                    ),
                    max(
                        bObj.position[2] - bObj.size[2] / 2,
                        min(aObj.position[2], bObj.position[2] + bObj.size[2] / 2),
                    ),
                ]
            )

            distance_box_to_sphere = np.linalg.norm(box_closest - aObj.position)

            return distance_box_to_sphere < aObj.radius

    elif aObj.physical_primitive_type == PhysicalPrimitiveType.BOX:
        # Box v. x checks (none thus far)
        raise UserWarning(
            "Code shouldn't reach here, unless new primitives added or bug in param swapping code."
        )

    pass
