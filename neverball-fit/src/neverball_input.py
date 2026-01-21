from evdev import UInput, ecodes

class NeverballController:
    def __init__(self):
        self.ui = UInput({
            ecodes.EV_KEY: [
                ecodes.KEY_LEFT,
                ecodes.KEY_RIGHT,
                ecodes.KEY_UP,
                ecodes.KEY_DOWN,
            ]
        })
        print("[uinput] virtual keyboard created")

    def update(self, x, y):
        self._set(ecodes.KEY_LEFT,  x < -0.15)
        self._set(ecodes.KEY_RIGHT, x >  0.15)
        self._set(ecodes.KEY_UP,    y >  0.15)
        self._set(ecodes.KEY_DOWN,  y < -0.15)

    def _set(self, key, pressed):
        self.ui.write(ecodes.EV_KEY, key, int(pressed))
        self.ui.syn()