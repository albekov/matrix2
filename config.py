import argparse
import sys
from enum import Enum

class AnsiColors(Enum):
    WHITE = "[97m"
    BRIGHT_GREEN = "[92m"
    GREEN = "[32m"
    BLUE = "[34m"
    BRIGHT_BLUE = "[94m"
    CYAN = "[36m"
    BRIGHT_CYAN = "[96m"
    MAGENTA = "[35m"
    BRIGHT_MAGENTA = "[95m"
    YELLOW = "[33m"
    BRIGHT_YELLOW = "[93m"
    RESET = "[0m"

    @classmethod
    def get_color(cls, color_name_or_code: str):
        # Helper to get color by name or direct code, useful for user-defined themes later
        upper_color_name = color_name_or_code.upper()
        if hasattr(cls, upper_color_name):
            return getattr(cls, upper_color_name).value
        # Basic validation for direct ANSI codes if needed, e.g. "97" or "38;2;r;g;b"
        # For now, this is simple. Task 4.1 might expand this.
        return f"[{color_name_or_code}m"

CHARS_LATIN = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()"
CHARS_KATAKANA = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶ"
CHARS_SYMBOLS = "←↑→↓↔↕↖↗↘↙↚↛↜↝↞↟↠↡↢↣↤↥↦↧↨↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇂⇃⇄⇅⇆⇇⇈⇉⇊⇋⇌⇍⇎⇏⇐⇑⇒⇓⇔⇕⇖⇗⇘⇙⇚⇛⇜⇝⇞⇟⇠⇡⇢⇣⇤⇥⇦⇧⇨⇩⇪"
DEFAULT_CHAR_SETS = [CHARS_LATIN, CHARS_KATAKANA, CHARS_SYMBOLS]

def parse_arguments():
    """Parses command-line arguments and validates them."""
    parser = argparse.ArgumentParser(
        description="Creates a Matrix-like digital rain animation in the console."
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=0.1,
        help="Animation speed (delay between frames in seconds). Default: 0.1",
    )
    parser.add_argument(
        "--density",
        type=float,
        default=0.075,
        help="Column density (probability of a column starting a new drop). Default: 0.075",
    )
    parser.add_argument(
        "--trail-length",
        type=int,
        default=10,
        help="The length of the fading trail. Default: 10",
    )
    parser.add_argument(
        "--color-intensity",
        type=str,
        default="normal",
        choices=["dim", "normal", "bright"],
        help="Color intensity for the trail. Choices: dim, normal, bright. Default: normal",
    )
    parser.add_argument(
        "--theme",
        type=str,
        default="classic",
        choices=["classic", "colorful"],
        help="Color theme for the animation. Choices: classic, colorful. Default: classic",
    )
    parser.add_argument(
        "--bright-length",
        type=int,
        default=2,
        help="Length of the 'bright' segment of the trail, following the head (not including the head). Default: 2"
    )
    parser.add_argument(
        "--glitch-rate",
        type=float,
        default=0.0,
        help="Probability (0.0 to 1.0) of a character glitching per frame. Default: 0.0 (no glitches)"
    )
    parser.add_argument(
        "--base-colors",
        type=str,
        default="",
        help="Comma-separated list of base color names (e.g., 'BLUE,GREEN,CYAN') to use ONLY for the 'colorful' theme. If empty, all available colors will be used. Invalid names are ignored."
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Manually set terminal width. Overrides automatic detection. Requires --height to be set as well."
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Manually set terminal height. Overrides automatic detection. Requires --width to be set as well."
    )
    parser.add_argument(
        "--depth_effect_strength",
        type=float,
        default=0.5,
        help="Controls the intensity of the depth effect (e.g., dimming) based on z_position (0.0 to 1.0). Default: 0.5"
    )
    parser.add_argument(
        "--rotation_speed",
        type=float,
        default=0.1,
        help="Controls the speed of the rotation effect. Positive for clockwise, negative for counter-clockwise, 0 for no rotation. Default: 0.1"
    )
    parser.add_argument(
        "--cylindrical_radius_factor",
        type=float,
        default=1.0,
        help="Factor to adjust the radius of the animation cylinder (e.g., 0.5 for tighter, 1.5 for wider). Default: 1.0"
    )
    parser.add_argument(
        "--y_rotation_speed",
        type=float,
        default=0.01,
        help="Controls the speed of rotation around the Y-axis for the 3D rain effect. Default: 0.01"
    )
    args = parser.parse_args()

    if not (0 < args.speed):
        print("Error: Animation speed must be a positive number.")
        return None
    if not (0 < args.density <= 1):
        print("Error: Column density must be between 0 and 1.")
        return None
    if not (2 < args.trail_length):
        print("Error: Trail length must be greater than 2.")
        return None

    if args.bright_length < 0:
        print("Error: Bright length cannot be negative.")
        return None # Indicates validation failure

    # Trail length must be able to accommodate the head (1 char), the bright segment,
    # and at least one dim character.
    # So, trail_length >= bright_length (segment after head) + 1 (head) + 1 (minimum dim character)
    # Which means trail_length >= bright_length + 2
    if args.trail_length < args.bright_length + 2:
        print(f"Error: Trail length ({args.trail_length}) must be at least bright length ({args.bright_length}) + 2 to accommodate head, bright segment, and at least one dim character.")
        return None # Indicates validation failure

    if not (0.0 <= args.glitch_rate <= 1.0):
        print("Error: Glitch rate must be between 0.0 and 1.0 inclusive.")
        return None # Indicates validation failure

    if args.width is not None and args.width <= 0:
        print("Error: --width must be a positive integer.")
        sys.exit(1)
    if args.height is not None and args.height <= 0:
        print("Error: --height must be a positive integer.")
        sys.exit(1)

    if (args.width is not None and args.height is None) or \
       (args.height is not None and args.width is None):
        print("Error: Both --width and --height must be provided if one is specified.")
        sys.exit(1)

    if not (0.0 <= args.depth_effect_strength <= 1.0):
        print("Error: Depth effect strength must be between 0.0 and 1.0 inclusive.")
        return None

    # No specific validation for rotation_speed beyond type checking by argparse

    if args.cylindrical_radius_factor <= 0.0:
        print("Error: Cylindrical radius factor must be positive.")
        return None

    # No specific validation for y_rotation_speed for now
    return args
