from vpython import standardAttributes, rate

from PhysicsEngine import PhysicsEngine
from DisplayEngine import DisplayEngine

from PhysicalMixin import PhysicalMixin

# This class marries physics to the display, managing the physics loop and the display loop
# It takes care of synchronization between the two
class SimulationEngine:
    # Physics part of the simulation
    _physics_engine = None

    # Display part of the simulation
    _display_engine = None

    # Objects in the simulation
    # Must be subclass of PhysicalMixin AND standardAttributes (vpython base class)
    _objects: list = None

    # display_rate: Hz, how many times per second to update the display
    _display_rate: int

    # physics rate: scalar, how much faster (multiplier) to run the physics loop than the display loop
    _physics_scalar: int

    # timestamp
    _t: float

    def __init__(self, **kwargs):
        # Setup world engine
        self._physics_engine = PhysicsEngine(**kwargs)

        # Setup display engine
        if "scene" in kwargs:
            self._display_engine = DisplayEngine(scene=kwargs["scene"])
        else:
            self._display_engine = DisplayEngine()

        # Store update rates
        if "display_rate" in kwargs:
            self._display_rate = kwargs["display_rate"]
        else:
            self._display_rate = 60

        if "physics_scalar" in kwargs:
            self._physics_scalar = kwargs["physics_scalar"]
        else:
            self._physics_scalar = 2

        self._t = 0

        self._objects = []

    # Main function, blocks, runs canvas and display, syncs physics and display loops
    def run(self, n_sec=None, timescale=1.0):
        # flake8 really insists that these are None here, but they're not so adding this to show it that they aren't
        assert self._display_engine is not None
        assert self._physics_engine is not None

        # Counter to keep track of how many frames were skipped in the display loop
        frameskip = 1

        # Max number of display frames to skip before updating display again
        max_frameskip = self._physics_scalar

        # Run first iteration
        self._display_engine.iterate()

        physics_rate = self._display_rate * self._physics_scalar
        physics_dt = (1 / physics_rate) * timescale

        end_timestamp = self._t + n_sec

        print("physics_rate =", physics_rate, ", physics_dt =", physics_dt)

        infinite_run = n_sec is None

        while (infinite_run) or (self._t < end_timestamp):
            # print('loop')
            # Base loop rate == physics rate
            rate(physics_rate)

            # Physics update
            self._physics_engine.iterate(physics_dt)
            # print('physics done')

            self._t += physics_dt

            # Use frameskips to only update the display at the display rate
            # design inspired by video game emulators
            # Every (self._physics_scalar) physics iterations is also a display iteration
            if frameskip == max_frameskip:  # if display update due, update display
                self._display_engine.iterate()
                # print('display done')
                frameskip = 1
            else:  # else frameskip
                frameskip += 1

        # and one final iteration with that leftover time
        dt_left = end_timestamp - self._t
        self._physics_engine.iterate(dt_left)
        self._t += dt_left
        self._display_engine.iterate()

    # Add an object to the simulation
    def register_object(self, obj):
        # Make sure obj is an instance of PhysicalMixin
        if not isinstance(obj, PhysicalMixin):
            raise UserWarning(
                "Objects added to the simulation must subclass PhysicalMixin!"
            )

        if not isinstance(obj, standardAttributes):
            raise UserWarning(
                "Objects added to the simulation must be derived from the VPython object based class!"
            )

        if self._physics_engine is None:
            raise UserWarning(
                "SimulationEngine: Dev error, physics engine was not instantiated"
            )

        if self._display_engine is None:
            raise UserWarning(
                "SimulationEngine: Dev error, display engine was not instantiated"
            )

        # Add reference to object to the world engine and physics engine
        if not obj.static:  # but static objects shouldn't be added
            self._physics_engine.register_object(obj)

        self._display_engine.register_object(obj)

        # And store one final reference to the object
        self._objects.append(obj)

    def add_force_applicator(self, force_applicator):
        self._physics_engine.add_force_applicator(force_applicator)
        return self

    @property
    def scene(self):
        return self._display_engine.scene
