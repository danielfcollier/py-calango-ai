import os
import sys

import streamlit.web.cli as stcli


def resolve_path(path):
    """
    Finds the absolute path to resources.
    PyInstaller unpacks files to a temp folder named _MEIPASS.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath("."), path)


if __name__ == "__main__":
    # 1. Locate the actual Streamlit app file inside the bundle
    app_path = resolve_path(os.path.join("src", "app.py"))

    # 2. Trick Streamlit into thinking it was run via CLI
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]

    # 3. Launch
    sys.exit(stcli.main())
