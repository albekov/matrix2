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
        help="Length of the 'bright' segment of the trail, following the head (not including the head). Default: 2",
    )
    parser.add_argument(
        "--glitch-rate",
        type=float,
        default=0.0,
        help="Probability (0.0 to 1.0) of a character glitching per frame. Default: 0.0 (no glitches)",
    )
    parser.add_argument(
        "--base-colors",
        type=str,
        default="",
        help="Comma-separated list of base color names (e.g., 'BLUE,GREEN,CYAN') to use ONLY for the 'colorful' theme. If empty, all available colors will be used. Invalid names are ignored.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Manually set terminal width. Overrides automatic detection. Requires --height to be set as well.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Manually set terminal height. Overrides automatic detection. Requires --width to be set as well.",
    )
    parser.add_argument(
        "--char-set",
        type=str,
        default="",  # Empty string by default, to distinguish from no input vs. explicit empty string
        help="String of characters to use for the rain. Overrides default character cycling. Example: --char-set '01'",
    )
    args = parser.parse_args()

    if args.char_set == "":  # Check if it's an explicitly provided empty string
        # This check is a bit tricky because default="" means we need to rely on how parse_args behaves.
        # If --char-set is NOT provided, args.char_set will be default "".
        # If --char-set IS provided as --char-set "" or --char-set="", args.char_set will be "".
        # To distinguish, we check if "--char-set" was in sys.argv and if the value associated was empty.
        # A simpler way is to change default to None and check if args.char_set == ""
        # For now, let's assume if args.char_set is "", it was explicitly set to empty by user.
        # This will be refined if it causes issues.
        # A common way to check if an arg was supplied is to use a unique default value not normally expected.
        # Let's refine the default and check:
        # Change default to a unique marker like a special string or None.
        # For this implementation, the requirements state: default=""
        # "If args.char_set is explicitly provided and is an empty string by the user (e.g. --char-set ""), print an error message"
        # This means we need to check sys.argv directly, as args.char_set will be "" for both default and explicit empty.
        # This is a common issue with argparse. A better default would be None.
        # Let's re-evaluate the requirement: "default="" (empty string to distinguish from no input vs. explicit empty string, will handle fallback logic in initialize_animation_parameters)"
        # This implies that if args.char_set is "", it could be EITHER the default OR explicitly set.
        # The error should only trigger if EXPLICITLY set to empty.
        # The prompt for config.py: "If args.char_set is explicitly provided and is an empty string by the user (e.g. --char-set ""), print an error message"
        # This is best handled by checking if "--char-set" is in sys.argv and its value is empty.
        # Let's find "--char-set" in sys.argv. If it's there, and the *next* arg (if it exists) is not another option (doesn't start with "-"), then that's its value.
        # Or, if it's like "--char-set=", then it's empty.

        is_explicitly_empty = False
        try:
            idx = sys.argv.index("--char-set")
            if idx + 1 < len(sys.argv):
                # Check if it's "--char-set """ or "--char-set=''"
                if (
                    sys.argv[idx + 1] == ""
                    or sys.argv[idx + 1] == "''"
                    or sys.argv[idx + 1] == '""'
                ):
                    is_explicitly_empty = True
                # Check if it's "--char-set=" (value is part of the same argument)
                elif sys.argv[idx].endswith("="):  # Handles --char-set=
                    # if sys.argv[idx] == "--char-set=" (no value after =) then it's empty
                    if sys.argv[idx] == "--char-set=":
                        is_explicitly_empty = True

            # If "--char-set" is the last argument, it implies no value was given,
            # which argparse might treat as needing a value or using default.
            # If default is "", and it's provided as last arg, args.char_set will be "".
            # This specific check is for *explicitly providing an empty string*.
            # e.g. script.py --char-set ""

        except ValueError:
            # --char-set was not in sys.argv, so it's using the default.
            pass

        # A more robust check for explicit empty string with argparse:
        # Change default to a sentinel value (e.g., object()) and then check if
        # args.char_set is ""
        # However, sticking to the requirement "default=''"
        # The problem is `parser.add_argument(..., default="", ...)` means `args.char_set` will be `""`
        # if the arg is not provided OR if it's provided as `--char-set ""`.
        # The requirement: "If args.char_set is explicitly provided and is an empty string by the user"
        # This means we must differentiate.
        # The easiest way is to set a different default in add_argument, and then if it's "", it was explicit.
        # Let's adjust the default for parsing and then handle the "not set" logic in animation_core.
        # Let's change the default here to a unique sentinel to detect if it was provided.
        # NO, the requirement is "default=''" for add_argument.
        # "default="" (empty string to distinguish from no input vs. explicit empty string, will handle fallback logic in initialize_animation_parameters)"
        # This means the distinction happens in initialize_animation_parameters.
        # So, the error check in parse_arguments should be: if args.char_set is "" AND "--char-set" was actually in sys.argv.

        # Simplest way to check if an option was provided and set to empty:
        # Check if '--char-set' is in sys.argv. If it is, find its value.
        # This is getting complicated due to argparse's behavior with default="".
        # Let's assume for now that if args.char_set is "", it *could* be an explicit empty string.
        # The prompt: "If args.char_set is explicitly provided and is an empty string by the user (e.g. --char-set ""), print an error message"
        # This implies we must detect *explicit provision*.
        # A common pattern is to have `nargs='?'` and `const=""` if `default` is something else,
        # or to check `sys.argv`.

        # Let's check `sys.argv` for the presence of `--char-set` followed by an empty string.
        found_char_set_arg = False
        explicitly_empty = False
        for i, arg_val in enumerate(sys.argv):
            if arg_val == "--char-set":
                found_char_set_arg = True
                if i + 1 < len(sys.argv) and (
                    sys.argv[i + 1] == ""
                    or sys.argv[i + 1] == "''"
                    or sys.argv[i + 1] == '""'
                ):
                    explicitly_empty = True
                elif arg_val.endswith("="):  # Handles --char-set=
                    explicitly_empty = True
                break  # Found the arg
            elif arg_val.startswith("--char-set="):
                found_char_set_arg = True
                if arg_val == "--char-set=":  # --char-set=""
                    explicitly_empty = True
                break

        if found_char_set_arg and explicitly_empty and args.char_set == "":
            # This condition means --char-set was used and an empty string was supplied.
            print(
                "Error: Character set cannot be an empty string if explicitly provided."
            )
            parser.exit(1)
        # The default="" will be handled in initialize_animation_parameters to mean "use default sets"

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
        return None  # Indicates validation failure

    # Trail length must be able to accommodate the head (1 char), the bright segment,
    # and at least one dim character.
    # So, trail_length >= bright_length (segment after head) + 1 (head) + 1 (minimum dim character)
    # Which means trail_length >= bright_length + 2
    if args.trail_length < args.bright_length + 2:
        print(
            f"Error: Trail length ({args.trail_length}) must be at least bright length ({args.bright_length}) + 2 to accommodate head, bright segment, and at least one dim character."
        )
        return None  # Indicates validation failure

    if not (0.0 <= args.glitch_rate <= 1.0):
        print("Error: Glitch rate must be between 0.0 and 1.0 inclusive.")
        return None  # Indicates validation failure

    if args.width is not None and args.width <= 0:
        print("Error: --width must be a positive integer.")
        sys.exit(1)
    if args.height is not None and args.height <= 0:
        print("Error: --height must be a positive integer.")
        sys.exit(1)

    if (args.width is not None and args.height is None) or (
        args.height is not None and args.width is None
    ):
        print("Error: Both --width and --height must be provided if one is specified.")
        sys.exit(1)

    return args
