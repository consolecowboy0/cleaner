"""Entry point script for PyInstaller that doesn't use relative imports."""

import sys
from pathlib import Path

# Add the parent directory to the path so cleaner package can be imported
if __name__ == "__main__":
    import cleaner.__main__
    cleaner.__main__.main()
