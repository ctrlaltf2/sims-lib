from vpython import standardAttributes, rate

from PhysicsEngine import PhysicsEngine
from DisplayEngine import DisplayEngine

from PhysicalMixin import PhysicalMixin

# This class marries physics to the display, managing the physics loop and the display loop
# It takes care of synchronization between the two
class SimulationEngine:
    # Physics part of the simulation
    _world_engine = None

    # Display part of the simulation
    _display_engine = None

    def __init__(self):
        # Setup world engine
        self._world_engine = WorldEngine()

        # Setup display engine
        self._display_engine = DisplayEngine()

    def iterate(self, dt):
        pass

    # Main function, blocks, runs canvas and display
    def run(self):
        pass

    # Add an object to the simulation
    def add_object(self, obj):
        # Make sure obj is an instance of PhysicalMixin
        if not isinstance(obj, PhysicalMixin):
            raise UserWarning('Objects added to the simulation must subclass PhysicalMixin!')

        if not isinstance(obj, standardAttributes):
            raise UserWarning('Objects added to the simulation must be derived from the VPython object based class!')

        # Add reference to object to the world engine and physics engine
        self._world_engine.add_object(obj)
        self._display_engine.add_object(obj)
