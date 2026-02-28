from input_events import InputListener
from overlay import Overlay

import threading
import pystray
from PIL import Image
import sys
import os

def create_tray_icon():
    # Use tray_icon.png for the tray icon
    # Find the correct path to tray_icon.png whether running as script or exe
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.abspath('.')
    icon_path = os.path.join(base_path, 'images', 'tray_icon.png')
    image = Image.open(icon_path)

    def on_exit(icon, item):
        icon.stop()
        import os
        os._exit(0)

    menu = pystray.Menu(
        pystray.MenuItem('Close application', on_exit)
    )
    icon = pystray.Icon('cStrafe', image, 'cStrafe UI', menu=menu)
    icon.run()



def run_overlay():
    overlay = Overlay()
    listener = InputListener(overlay)
    listener.start()
    overlay.run()

def main() -> None:
    # Start overlay and input listener in a background thread
    overlay_thread = threading.Thread(target=run_overlay, daemon=True)
    overlay_thread.start()
    # Run tray icon in the main thread
    create_tray_icon()


if __name__ == "__main__":
    main()