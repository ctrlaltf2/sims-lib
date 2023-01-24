# Base class for defining force applicators (e.g. Electromagnetism, Friction, Gravity, Gravity but with general relativity, etc)
class IForceApplicator:
    def __init__(self):
        return

    # Apply forces to world objects as relevant to whatever force applicator type this is
    def apply_forces(self, objects, dt):
        raise UserWarning("Please define apply_force.")
