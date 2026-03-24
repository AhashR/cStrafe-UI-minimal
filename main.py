from input_events import InputListener
from overlay import Overlay
from settings_dialog import SettingsDialog
from PIL import Image
import threading
import pystray
import sys
import os

def create_tray_icon():
    # Find the correct path to tray_icon.ico whether running as script or exe
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    else:
        # Running as script
        base_path = os.path.abspath('.')
    icon_path = os.path.join(base_path, 'images', 'tray_icon.ico')
    image = Image.open(icon_path)

    def on_settings(icon, item):
        """Open the settings dialog for key bindings in a separate thread."""
        def open_settings_in_thread():
            try:
                settings = SettingsDialog()
                settings.run()
            except Exception as e:
                print(f"Error opening settings dialog: {e}")
        
        # Run the dialog in a daemon thread to avoid blocking the tray icon
        settings_thread = threading.Thread(target=open_settings_in_thread, daemon=True)
        settings_thread.start()

    def on_exit(icon, item):
        icon.stop()
        os._exit(0)

    menu = pystray.Menu(
        pystray.MenuItem('Configure movement keys', on_settings),
        pystray.MenuItem('Close application', on_exit)
    )
    icon = pystray.Icon('cStrafe', image, 'cStrafe', menu=menu)
    icon.run()

def run_overlay():
    overlay = Overlay()
    listener = InputListener(overlay)
    listener.start()
    overlay.run()

def main() -> None:
    overlay_thread = threading.Thread(target=run_overlay, daemon=True)
    overlay_thread.start()
    create_tray_icon()


if __name__ == "__main__":
    main()