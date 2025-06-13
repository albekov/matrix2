import argparse
import os
import random
import sys
import time


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
    return args


def get_terminal_dimensions(args):
    """Gets terminal dimensions or returns fallback values."""
    try:
        width, height = os.get_terminal_size()
    except OSError:
        width, height = 80, 24
        print("Warning: Unable to get terminal size. Using default 80x24.")
    return width, height


def initialize_animation_parameters(width, height, args):
    """Initializes characters, colors, and column states."""
    chars_latin = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()"
    # Temporarily commenting out other char sets for debugging
    # chars_katakana = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶ"
    # chars_symbols = "←↑→↓↔↕↖↗↘↙↚↛↜↝↞↟↠↡↢↣↤↥↦↧↨↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇂⇃⇄⇅⇆⇇⇈⇉⇊⇋⇌⇍⇎⇏⇐⇑⇒⇓⇔⇕⇖⇗⇘⇙⇚⇛⇜⇝⇞⇟⇠⇡⇢⇣⇤⇥⇦⇧⇨⇩⇪"
    chars = [chars_latin] # Using only latin characters for debugging

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
    return chars, classic_colors, extended_colors, columns


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


def render_frame_buffer(columns, width, height, trail_length, char_sets, active_colors, color_intensity="normal", theme="classic"):
    """Renders the current frame into a buffer."""
    frame_buffer = []
    for y in range(1, height + 1):
        char_list = []
        for x in range(width):
            trail_head_y, char_set_index = columns[x]
            current_char_set = char_sets[char_set_index]
            if trail_head_y > 0 and trail_head_y - trail_length < y <= trail_head_y:
                distance_from_head = trail_head_y - y
                char = random.choice(current_char_set)

                base_color_name = "GREEN" # Default for classic theme
                if theme == "colorful":
                    color_names = list(active_colors.keys())
                    available_base_colors = [name for name in color_names if "BRIGHT_" not in name and name not in ["WHITE", "RESET"]]
                    if not available_base_colors:
                        available_base_colors = ["GREEN"] # Fallback
                    base_color_name = random.choice(available_base_colors)

                bright_variant_key = f"BRIGHT_{base_color_name}"
                bright_variant_exists = bright_variant_key in active_colors

                # Define colors based on intensity and theme
                if color_intensity == "dim":
                    c_head = active_colors[bright_variant_key] if bright_variant_exists else active_colors[base_color_name]
                    c_seg1 = active_colors[base_color_name]
                    c_seg2 = active_colors[base_color_name]
                elif color_intensity == "bright":
                    c_head = active_colors["WHITE"]
                    c_seg1 = active_colors["WHITE"]
                    c_seg2 = active_colors[bright_variant_key] if bright_variant_exists else active_colors["WHITE"]
                else: # normal (default)
                    c_head = active_colors["WHITE"]
                    c_seg1 = active_colors[bright_variant_key] if bright_variant_exists else active_colors["WHITE"]
                    c_seg2 = active_colors[base_color_name]

                if distance_from_head == 0: # Head of the trail
                    char_list.append(f"{c_head}{char}")
                elif distance_from_head <= 2: # Segment immediately following the head
                    char_list.append(f"{c_seg1}{char}")
                else: # Rest of the trail
                    char_list.append(f"{c_seg2}{char}")
            else:
                char_list.append(" ")
        frame_buffer.append("".join(char_list))
    return frame_buffer


def run_animation_loop(args, width, height, char_sets, classic_colors_param, extended_colors_param, columns_param):
    """Runs the main animation loop."""
    # Determine which color set to use based on the theme
    active_colors_dict = extended_colors_param if args.theme == "colorful" else classic_colors_param

    MIN_EFFECTIVE_SLEEP = 0.005 # Minimum sleep time for potentially better consistency

    while True:
        current_columns = update_column_states(
            columns_param, width, height, args.density, args.trail_length, len(char_sets)
        )
        frame_buffer = render_frame_buffer(
            current_columns, width, height, args.trail_length, char_sets, active_colors_dict, args.color_intensity, args.theme
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
        chars, classic_colors, extended_colors, columns = initialize_animation_parameters(width, height, args)
        try:
            # Hide cursor
            sys.stdout.write("\033[?25l")
            # Pass all color sets to the loop, it will select based on theme
            run_animation_loop(args, width, height, chars, classic_colors, extended_colors, columns)
        except KeyboardInterrupt:
            # Show cursor and reset color (use classic_colors for reset as it's simpler)
            sys.stdout.write("\033[?25h" + classic_colors["RESET"])
            print("\nAnimation stopped.")