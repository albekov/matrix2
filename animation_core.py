import random
import sys
import time

import wcwidth

from config import DEFAULT_CHAR_SETS, AnsiColors


def initialize_animation_parameters(width, height, args):
    """Initializes characters, colors, and column states."""
    # Use DEFAULT_CHAR_SETS from config.py
    chars = DEFAULT_CHAR_SETS

    # Each column stores (y_position, char_set_index)
    # Initialize columns with a random character set index for each column
    columns = [(0, random.randrange(len(chars))) for _ in range(width)]

    final_theme_colors = {}

    if args.theme == "classic":
        final_theme_colors = {
            "WHITE": AnsiColors.WHITE.value,
            "BRIGHT_GREEN": AnsiColors.BRIGHT_GREEN.value,
            "GREEN": AnsiColors.GREEN.value,
            "RESET": AnsiColors.RESET.value,
        }
    elif args.theme == "colorful":
        # Start with RESET and WHITE, which are common
        final_theme_colors = {
            "RESET": AnsiColors.RESET.value,
            "WHITE": AnsiColors.WHITE.value,
        }

        # Create a lookup for all available AnsiColors by their names
        available_ansi_colors = {
            name: member.value for name, member in AnsiColors.__members__.items()
        }

        user_specified_color_names = []
        if args.base_colors:  # If user provided any string for --base-colors
            user_specified_color_names = [
                name.strip().upper()
                for name in args.base_colors.split(",")
                if name.strip()
            ]

        selected_user_colors_count = 0
        if user_specified_color_names:  # If there are actual names to process
            for name in user_specified_color_names:
                # Check if the name is a valid base color (not BRIGHT_*, not WHITE, not RESET)
                if (
                    name in available_ansi_colors
                    and "BRIGHT_" not in name
                    and name not in ["WHITE", "RESET"]
                ):
                    final_theme_colors[name] = available_ansi_colors[name]
                    bright_name = f"BRIGHT_{name}"
                    if bright_name in available_ansi_colors:
                        final_theme_colors[bright_name] = available_ansi_colors[
                            bright_name
                        ]
                    selected_user_colors_count += 1
                elif name:  # Non-empty but invalid/unsuitable name
                    print(
                        f"Warning: Invalid or unsuitable base color name '{name}' in --base-colors. Ignoring.",
                        file=sys.stderr,
                    )

            if (
                selected_user_colors_count == 0
            ):  # User specified names, but none were valid base colors
                print(
                    "Warning: No valid base colors from --base-colors were found. Using default full 'colorful' palette.",
                    file=sys.stderr,
                )
                # Populate with all available colors from AnsiColors, excluding RESET for general use
                for color_name, color_value in available_ansi_colors.items():
                    if color_name != "RESET":
                        final_theme_colors[color_name] = color_value
        else:  # No base colors specified by user (args.base_colors was empty)
            # Populate with all available colors from AnsiColors, excluding RESET for general use
            for color_name, color_value in available_ansi_colors.items():
                if color_name != "RESET":
                    final_theme_colors[color_name] = color_value

        # Fallback: Ensure at least GREEN and BRIGHT_GREEN are in the colorful palette if it's somehow empty of base colors
        # This check might be redundant if the above logic correctly populates from AnsiColors.
        current_base_colors_in_palette = [
            k
            for k in final_theme_colors
            if "BRIGHT_" not in k and k not in ["WHITE", "RESET"]
        ]
        if not current_base_colors_in_palette:
            print(
                "Warning: The 'colorful' palette ended up with no usable base colors. Adding GREEN as a fallback.",
                file=sys.stderr,
            )
            if "GREEN" in available_ansi_colors:
                final_theme_colors["GREEN"] = available_ansi_colors["GREEN"]
            if "BRIGHT_GREEN" in available_ansi_colors:
                final_theme_colors["BRIGHT_GREEN"] = available_ansi_colors[
                    "BRIGHT_GREEN"
                ]

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
                columns[i] = (0, char_set_index)  # Keep char_set_index until new drop
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
            # Ensure char_set_index is valid for char_sets
            if not (0 <= char_set_index < len(char_sets)):  # Defensive check
                # This case should ideally not happen if columns are initialized correctly
                # and num_char_sets in update_column_states is len(char_sets)
                char_list.append(" ")
                continue

            current_char_set = char_sets[char_set_index]
            if (
                trail_head_y > 0
                and trail_head_y - args.trail_length < y <= trail_head_y
            ):
                distance_from_head = trail_head_y - y

                original_char = random.choice(current_char_set)

                if wcwidth.wcwidth(original_char) != 1:
                    original_char = " "

                char_to_render = original_char

                if args.glitch_rate > 0 and random.random() < args.glitch_rate:
                    glitch_candidate = random.choice(current_char_set)
                    if wcwidth.wcwidth(glitch_candidate) == 1:
                        char_to_render = glitch_candidate

                base_color_name = "GREEN"  # Default for classic theme or fallback
                if args.theme == "colorful":
                    available_base_colors = [
                        name
                        for name in active_colors
                        if "BRIGHT_" not in name
                        and name not in ["WHITE", "RESET"]
                        and name in AnsiColors.__members__
                    ]
                    if not available_base_colors:
                        # Fallback if no suitable base colors are found in active_colors (e.g. if user specified only WHITE)
                        if "GREEN" in active_colors:
                            base_color_name = (
                                "GREEN"  # Explicitly check if GREEN is there
                            )
                        # else: it remains "GREEN", and we hope active_colors['GREEN'] exists or a key error occurs
                    else:
                        base_color_name = random.choice(available_base_colors)

                # Ensure selected base_color_name and its bright variant exist in active_colors
                # If not, default to WHITE or the base_color_name itself to avoid KeyError
                actual_base_color = active_colors.get(
                    base_color_name, AnsiColors.GREEN.value
                )  # Fallback to Green enum value
                bright_variant_key = f"BRIGHT_{base_color_name}"
                actual_bright_color = active_colors.get(
                    bright_variant_key, actual_base_color
                )

                color_white = active_colors.get(
                    "WHITE", AnsiColors.WHITE.value
                )  # Fallback to White enum value

                if args.color_intensity == "dim":
                    c_head = actual_bright_color
                    c_seg1 = actual_base_color
                    c_seg2 = actual_base_color
                elif args.color_intensity == "bright":
                    c_head = color_white
                    c_seg1 = color_white
                    c_seg2 = actual_bright_color
                else:  # normal (default)
                    c_head = color_white
                    c_seg1 = actual_bright_color
                    c_seg2 = actual_base_color

                if distance_from_head == 0:  # Head of the trail
                    char_list.append(f"{c_head}{char_to_render}")
                elif (
                    distance_from_head <= args.bright_length
                ):  # Bright part, uses c_seg1
                    char_list.append(f"{c_seg1}{char_to_render}")
                else:  # Dim part, uses c_seg2
                    char_list.append(f"{c_seg2}{char_to_render}")
            else:
                char_list.append(" ")
        frame_buffer.append("".join(char_list))
    return frame_buffer


def run_animation_loop(
    args, width, height, char_sets, columns_param, active_theme_colors_param
):
    """Runs the main animation loop."""
    active_colors_dict = (
        active_theme_colors_param  # This now contains enum values like "[97m"
    )

    MIN_EFFECTIVE_SLEEP = 0.005

    while True:
        current_columns = update_column_states(
            columns_param,
            width,
            height,
            args.density,
            args.trail_length,
            len(char_sets),
        )
        frame_buffer = render_frame_buffer(
            current_columns, width, height, char_sets, active_colors_dict, args
        )
        columns_param = current_columns

        # Ensure RESET code is correctly fetched. It should be directly in active_colors_dict.
        reset_code = active_colors_dict.get(
            "RESET", AnsiColors.RESET.value
        )  # Fallback to enum default
        sys.stdout.write("\033[H" + "\n".join(frame_buffer) + reset_code)
        sys.stdout.flush()

        actual_sleep_time = max(args.speed, MIN_EFFECTIVE_SLEEP)
        time.sleep(actual_sleep_time)
