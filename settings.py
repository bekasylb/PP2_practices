# settings.py — Load and save user preferences via settings.json

import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULT_SETTINGS = {
    "snake_color": [0, 220, 120],   # RGB list
    "grid_overlay": True,
    "sound": True,
}


def load_settings() -> dict:
    """Load settings from disk; fall back to defaults on error."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            # Fill missing keys with defaults
            for k, v in DEFAULT_SETTINGS.items():
                data.setdefault(k, v)
            return data
        except Exception as e:
            print(f"[settings] Failed to load settings.json: {e}")
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict) -> bool:
    """Persist settings dict to settings.json."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"[settings] Failed to save settings.json: {e}")
        return False
