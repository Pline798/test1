import sys
import io

if sys.stdout is not None and sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from desktop.gui_app import DevGUI

if __name__ == "__main__":
    DevGUI().run()