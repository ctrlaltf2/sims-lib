import numpy as np

from IForceApplicator import IForceApplicator

# Gravity as it appears in a locally flat region (like from the reference point of a person on the surface of the Earth)
# A constant "field" that doesn't feel like it changes anywhere
class StaticLocalGravity(IForceApplicator):
    # Gravity vector to apply to all objects
    _gravity_vec = np.array([0, 0, 0])

    def __init__(self, gravity_vec):
        self._gravity_vec = np.array(gravity_vec)
        super().__init__()

    def apply_forces(self, world):
        for obj in world:
            obj.add_force(obj.mass * self._gravity_vec)
