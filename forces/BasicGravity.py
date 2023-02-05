from IForceApplicator import IForceApplicator


class BasicGravity(IForceApplicator):
    # Mean radius of the Earth
    R_E = 6.3781 * 10**6  # m

    # Earth standard gravity
    g0 = 9.80665  # m/s^2

    # Gravity felt at height h meters above sea level (https://en.wikipedia.org/wiki/Gravity_of_Earth#Altitude)
    def g(self, h):
        return self.g0 * (self.R_E / (self.R_E + h)) ** 2

    def __init__(self):
        return

    def apply_forces(self, objects, dt):
        for obj in objects:
            h = obj.position[1]  # y-axis == h
            F_G = np.array([0, obj.mass * -self.g(h), 0])
            obj.add_force(F_G)
