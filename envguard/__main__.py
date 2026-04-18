"""Allow running envguard as a module: python -m envguard."""
import sys
from envguard.cli import main

sys.exit(main())
