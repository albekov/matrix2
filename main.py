import argparse
import os
import random
import sys
import time
import wcwidth


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

    return args


def get_terminal_dimensions(args):
    """Gets terminal dimensions or returns fallback values."""
    if args.width is not None and args.height is not None:
        # Validation for positive values should have been done in parse_arguments
        print(f"Using manually specified dimensions: {args.width}x{args.height}")
        return args.width, args.height
    # If one is specified but not the other, parse_arguments should have exited.
    # So, if we reach here, either both are None, or something went wrong with arg parsing logic.

    try:
        width, height = os.get_terminal_size()
        # print(f"Detected terminal dimensions: {width}x{height}") # Optional: for debugging
        return width, height
    except OSError:
        print("Warning: Could not detect terminal size. Falling back to default 80x24.")
        return 80, 24


def initialize_animation_parameters(width, height, args):
    """Initializes characters, colors, and column states."""
    chars_latin = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()"
    chars_katakana = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶ"
    chars_symbols = "←↑→↓↔↕↖↗↘↙↚↛↜↝↞↟↠↡↢↣↤↥↦↧↨↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇂⇃⇄⇅⇆⇇⇈⇉⇊⇋⇌⇍⇎⇏⇐⇑⇒⇓⇔⇕⇖⇗⇘⇙⇚⇛⇜⇝⇞⇟⇠⇡⇢⇣⇤⇥⇦⇧⇨⇩⇪"
    chars = [chars_latin, chars_katakana, chars_symbols]

    classic_colors = {
        "WHITE": "\033[97m",
        "BRIGHT_GREEN": "\033[92m",
        "GREEN": "\033[32m",
        "RESET": "\033[0m",
    }
    extended_colors = {
        **classic_colors, # Includes WHITE, BRIGHT_GREEN, GREEN, RESET
        "BLUE": "\033[34m",
        "BRIGHT_BLUE": "\033[94m",
        "CYAN": "\033[36m",
        "BRIGHT_CYAN": "\033[96m",
        "MAGENTA": "\033[35m",
        "BRIGHT_MAGENTA": "\033[95m",
        "YELLOW": "\033[33m",
        "BRIGHT_YELLOW": "\033[93m",
    }
    # Each column stores (y_position, char_set_index)
    columns = [(0, random.randrange(len(chars))) for _ in range(width)]

    final_theme_colors = {}
    if args.theme == "classic":
        final_theme_colors = classic_colors.copy() # Use a copy
    elif args.theme == "colorful":
        final_theme_colors = {"RESET": extended_colors.get("RESET", "\033[0m")}
        if "WHITE" in extended_colors:
             final_theme_colors["WHITE"] = extended_colors["WHITE"]

        user_specified_color_names = []
        if args.base_colors: # If user provided any string for --base-colors
            user_specified_color_names = [name.strip().upper() for name in args.base_colors.split(',') if name.strip()]

        selected_user_colors_count = 0
        if user_specified_color_names: # If there are actual names to process
            for name in user_specified_color_names:
                if name in extended_colors and "BRIGHT_" not in name and name not in ["WHITE", "RESET"]:
                    final_theme_colors[name] = extended_colors[name]
                    bright_name = f"BRIGHT_{name}"
                    if bright_name in extended_colors:
                        final_theme_colors[bright_name] = extended_colors[bright_name]
                    selected_user_colors_count += 1
                elif name: # Non-empty but invalid/unsuitable name
                    print(f"Warning: Invalid base color name '{name}' in --base-colors, or it's not a suitable base color type. Ignoring.")

            if selected_user_colors_count == 0: # User specified names, but none were valid base colors
                print("Warning: No valid base colors from --base-colors were found. Using default full 'colorful' palette.")
                final_theme_colors = extended_colors.copy()
        else: # No base colors specified by user (args.base_colors was empty)
            final_theme_colors = extended_colors.copy()

        # Fallback: Ensure at least one usable base color is in the colorful palette
        current_base_colors_in_palette = [k for k in final_theme_colors if "BRIGHT_" not in k and k not in ["WHITE", "RESET"]]
        if not current_base_colors_in_palette:
            print("Warning: The 'colorful' palette ended up with no usable base colors for trails. Adding GREEN as a fallback.")
            if "GREEN" in extended_colors: final_theme_colors["GREEN"] = extended_colors["GREEN"]
            if "BRIGHT_GREEN" in extended_colors: final_theme_colors["BRIGHT_GREEN"] = extended_colors["BRIGHT_GREEN"]
            # If GREEN itself isn't in extended_colors, this is a deeper setup issue.

    return chars, final_theme_colors, columns


def update_column_states(columns, width, height, density, trail_length, num_char_sets):
    """Updates the state of each column for the next frame."""
    for i in range(width):
        y_position, char_set_index = columns[i]
        if y_position == 0:
            if random.random() < density:
                # Start a new drop with a randomly selected char set for this column
                columns[i] = (1, random.randrange(num_char_sets))
        else:
            y_position += 1
            # Reset column if trail is off screen
            if y_position - trail_length > height:
                columns[i] = (0, char_set_index) # Keep char_set_index until new drop
            else:
                columns[i] = (y_position, char_set_index)
    return columns


def render_frame_buffer(columns, width, height, char_sets, active_colors, args):
    """Renders the current frame into a buffer."""
    frame_buffer = []
    for y in range(1, height + 1):
        char_list = []
        for x in range(width):
            trail_head_y, char_set_index = columns[x]
            current_char_set = char_sets[char_set_index]
            if trail_head_y > 0 and trail_head_y - args.trail_length < y <= trail_head_y:
                distance_from_head = trail_head_y - y

                original_char = random.choice(current_char_set)

                # Ensure character has a display width of 1, otherwise replace with space
                if wcwidth.wcwidth(original_char) != 1:
                    original_char = " " # Use space if original char is not single-width

                char_to_render = original_char # Default to original

                if args.glitch_rate > 0 and random.random() < args.glitch_rate:
                    # Attempt to pick a new glitched character from the same character set
                    glitch_candidate = random.choice(current_char_set)
                    if wcwidth.wcwidth(glitch_candidate) == 1:
                        char_to_render = glitch_candidate
                    # If the glitch_candidate is not single-width, char_to_render remains original_char

                base_color_name = "GREEN" # Default for classic theme
                if args.theme == "colorful":
                    available_base_colors = [
                        name for name in active_colors
                        if "BRIGHT_" not in name and name not in ["WHITE", "RESET"]
                    ]
                    # This check should ideally not be needed if initialize_animation_parameters guarantees a valid palette
                    if not available_base_colors:
                        # This is a safety net.
                        # print("Critical Warning: No base colors in active_colors for render_frame_buffer. Defaulting to GREEN.")
                        base_color_name = "GREEN" # Fallback name
                        # To make this truly safe, we'd need to ensure active_colors[base_color_name] is valid.
                        # However, initialize_animation_parameters is supposed to ensure 'GREEN' is added if this list would be empty.
                    else:
                        base_color_name = random.choice(available_base_colors)

                bright_variant_key = f"BRIGHT_{base_color_name}"
                bright_variant_exists = bright_variant_key in active_colors

                # Define colors based on intensity and theme
                if args.color_intensity == "dim":
                    c_head = active_colors[bright_variant_key] if bright_variant_exists else active_colors[base_color_name]
                    c_seg1 = active_colors[base_color_name]
                    c_seg2 = active_colors[base_color_name]
                elif args.color_intensity == "bright":
                    c_head = active_colors["WHITE"]
                    c_seg1 = active_colors["WHITE"]
                    c_seg2 = active_colors[bright_variant_key] if bright_variant_exists else active_colors["WHITE"]
                else: # normal (default)
                    c_head = active_colors["WHITE"]
                    c_seg1 = active_colors[bright_variant_key] if bright_variant_exists else active_colors["WHITE"]
                    c_seg2 = active_colors[base_color_name]

                if distance_from_head == 0: # Head of the trail
                    char_list.append(f"{c_head}{char_to_render}")
                elif distance_from_head <= args.bright_length: # Bright part, uses c_seg1
                    char_list.append(f"{c_seg1}{char_to_render}")
                else: # Dim part, uses c_seg2
                    char_list.append(f"{c_seg2}{char_to_render}")
            else:
                char_list.append(" ")
        frame_buffer.append("".join(char_list))
    return frame_buffer


def run_animation_loop(args, width, height, char_sets, columns_param, active_theme_colors_param):
    """Runs the main animation loop."""
    active_colors_dict = active_theme_colors_param

    MIN_EFFECTIVE_SLEEP = 0.005 # Minimum sleep time for potentially better consistency

    while True:
        current_columns = update_column_states(
            columns_param, width, height, args.density, args.trail_length, len(char_sets)
        )
        frame_buffer = render_frame_buffer(
            current_columns, width, height, char_sets, active_colors_dict, args
        )
        # Update columns_param for the next iteration if update_column_states returns a new list/object
        columns_param = current_columns
        sys.stdout.write("\033[H" + "\n".join(frame_buffer) + active_colors_dict["RESET"])
        sys.stdout.flush()

        actual_sleep_time = max(args.speed, MIN_EFFECTIVE_SLEEP)
        time.sleep(actual_sleep_time)


if __name__ == "__main__":
    args = parse_arguments()
    if args:
        width, height = get_terminal_dimensions(args)
        chars, active_theme_colors, columns = initialize_animation_parameters(width, height, args)
        try:
            # Hide cursor
            sys.stdout.write("\033[?25l")
            # Pass all color sets to the loop, it will select based on theme
            run_animation_loop(args, width, height, chars, columns, active_theme_colors)
        except KeyboardInterrupt:
            # Show cursor and reset color
            reset_color = active_theme_colors.get("RESET", "\033[0m")
            sys.stdout.write("\033[?25h" + reset_color)
            print("\nAnimation stopped.")