"""Entity configuration constants.

This module centralizes hardcoded entity configurations to eliminate duplication
across platform files.
"""

from __future__ import annotations

from typing import Final

# ============================================================================
# Light Configuration
# ============================================================================

# Default color temperature range in Kelvin
# Used when device doesn't provide specific min/max values
# Note: Actual device ranges vary by product (e.g., 3000-4000K, 3000-5000K)
DEFAULT_MIN_KELVIN: Final = 2700
DEFAULT_MAX_KELVIN: Final = 6500

# ============================================================================
# Fan Configuration
# ============================================================================

# Default speed control range (1-100)
DEFAULT_SPEED_COUNT: Final = 100
DEFAULT_MIN_SPEED: Final = 1
DEFAULT_MAX_SPEED: Final = 100

# ============================================================================
# Cover Configuration
# ============================================================================

# Default position range (0-100)
DEFAULT_MIN_POSITION: Final = 0
DEFAULT_MAX_POSITION: Final = 100
