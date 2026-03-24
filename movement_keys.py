"""
Directional movement key bindings - loaded from configuration.

Defaults:
    FORWARD  = 'W'
    BACKWARD = 'S'
    LEFT     = 'A'
    RIGHT    = 'D'

These defaults match the conventional WASD movement keys. You can change these
settings using the "Configure Keys" option in the application's tray menu.

Note:
    Only single‐character alphanumeric keys are supported. Special keys like
    arrow keys are not guaranteed to work because the underlying input
    library may not provide a `.char` attribute for non‐alphanumeric keys.
"""

from config import load_config

# Load key bindings from configuration file
_config = load_config()
FORWARD: str = _config['FORWARD']
BACKWARD: str = _config['BACKWARD']
LEFT: str = _config['LEFT']
RIGHT: str = _config['RIGHT']