import numpy as np

from IForceApplicator import IForceApplicator


class AirResistanceApplicator(IForceApplicator):
    # ideal gas constant
    R = 8.31445  # J/(mol K)

    M = 0.0289652  # kg/mol

    # Sea level standard atmospheric pressure
    p0 = 101325  # Pa

    # Temperature lapse rate
    L = 0.0065  # K/m

    # sea level standard temperature
    T0 = 288.15  # K

    # Mean radius of the Earth
    R_E = 6.3781 * 10**6  # m

    # Earth standard gravity
    g0 = 9.80665  # m/s^2

    # Equations for density of air as a function of altitude above sea level
    # https://en.wikipedia.org/wiki/Density_of_air#Variation_with_altitude

    # Gravity felt at height h meters above sea level (https://en.wikipedia.org/wiki/Gravity_of_Earth#Altitude)
    def g(self, h):  # m/s^2
        return self.g0 * (self.R_E / (self.R_E + h)) ** 2

    # Pressure at altitude h
    def p(self, h):  # pressure
        return self.p0 * (1 - self.L * h / self.T0) ** (
            self.g(h) * self.M / (self.R * self.L)
        )

    # Temperature at altitude h
    def T(self, h):
        return self.T0 - self.L * h

    # Air density
    def rho(self, h):
        return self.p(h) * self.M / (self.R * self.T(h))

    def __init__(self):
        return

    def apply_forces(self, objects, dt):
        for obj in objects:
            C_D = obj.coeff_drag
            A = obj.crossectional_area
            h = obj.position[1]

            vel_mag = np.linalg.norm(obj.velocity)

            F_D_magnitude = (
                (1 / 2) * self.rho(h) * np.linalg.norm(obj.velocity) ** 2 * C_D * A
            )

            if vel_mag != 0.0:
                vel_unit = obj.velocity / np.linalg.norm(obj.velocity)
            else:
                vel_unit = np.array([0, 0, 0])

            F_D = -vel_unit * F_D_magnitude

            # print('AirResistance: Applying a force of ', F_D)
            obj.add_force(F_D)
