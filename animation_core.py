import random
import sys
import time

import wcwidth

from config import (
    CHARS_KATAKANA,
    CHARS_LATIN,
    CHARS_SYMBOLS,
    DEFAULT_CHAR_SETS,
    AnsiColors,
)


def initialize_animation_parameters(args, width, height):
    """Initializes characters, colors, and column states."""

    available_char_sets = []
    # Check if args.char_set was provided by the user
    if (
        args.char_set
    ):  # Not None and not empty string (already validated in parse_arguments)
        chars = list(args.char_set)
        available_char_sets = [chars]
    else:
        # Keep the existing logic for DEFAULT_CHAR_SETS
        # Ensure DEFAULT_CHAR_SETS are lists of characters if they aren't already
        available_char_sets = [list(cs) for cs in DEFAULT_CHAR_SETS if cs]

    # Initialize columns
    # Each column will be a dictionary to store its state, including its current character set
    columns = []
    for _ in range(width):
        columns.append(
            {
                "head_y": 0,  # Current y position of the head of the drop
                "current_char_set": random.choice(available_char_sets)
                if available_char_sets
                else list(CHARS_LATIN),  # Fallback if empty
                "trail": [],  # Stores characters and their specific attributes for the trail
            }
        )

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

    # The function should return columns, available_char_sets, and final_theme_colors
    return columns, available_char_sets, final_theme_colors


def update_column_states(
    columns, width, height, density, trail_length, available_char_sets
):
    """Updates the state of each column for the next frame."""
    for i in range(width):
        col_state = columns[i]
        if col_state["head_y"] == 0:  # No active drop in this column
            if random.random() < density:  # Chance to start a new drop
                col_state["head_y"] = 1
                col_state["current_char_set"] = (
                    random.choice(available_char_sets) if available_char_sets else [" "]
                )
                # Trail initialization could be done here or in render
        else:
            col_state["head_y"] += 1
            # Reset column if trail is off screen
            # The trail length is visual, head_y is the leading char's position
            if col_state["head_y"] - trail_length > height:
                col_state["head_y"] = 0  # Reset the drop
                # No need to change current_char_set, it will be picked when new drop starts
    # columns list is modified in place, but returning it is fine.
    return columns


def render_frame_buffer(
    columns, width, height, active_colors, args, available_char_sets, glitch_rate
):  # Added available_char_sets and glitch_rate
    """Renders the current frame into a buffer."""
    frame_buffer = []
    for y in range(1, height + 1):  # Iterate through each row of the terminal
        char_list = []
        for x in range(width):  # Iterate through each column
            col_state = columns[x]
            trail_head_y = col_state["head_y"]
            char_set_for_column = col_state["current_char_set"]

            # Determine if a character should be rendered at this (x,y)
            # A character is rendered if it's part of an active trail
            if (
                trail_head_y > 0  # Is there an active drop?
                and trail_head_y - args.trail_length
                < y
                <= trail_head_y  # Is current y within the trail?
            ):
                distance_from_head = trail_head_y - y

                # Choose a character from the column's specific character set
                original_char = random.choice(char_set_for_column)
                if not original_char:  # handle empty char set
                    original_char = " "

                if wcwidth.wcwidth(original_char) != 1:
                    original_char = " "  # Ensure single width

                char_to_render = original_char

                # Apply glitch effect if applicable
                if glitch_rate > 0 and random.random() < glitch_rate:
                    glitched_char = random.choice(char_set_for_column)
                    if not glitched_char:
                        glitched_char = " "
                    if wcwidth.wcwidth(glitched_char) == 1:
                        char_to_render = glitched_char

                base_color_name = "GREEN"  # Default for classic theme or fallback
                if args.theme == "colorful":
                    # Filter for base colors (not BRIGHT, not WHITE, not RESET)
                    # that are actually defined in AnsiColors enum and present in active_colors
                    available_base_colors_in_palette = [
                        name
                        for name, color_val in active_colors.items()
                        if "BRIGHT_" not in name
                        and name not in ["WHITE", "RESET"]
                        and name
                        in AnsiColors.__members__  # Ensure it's a valid AnsiColor name
                    ]
                    if not available_base_colors_in_palette:
                        # Fallback if no suitable base colors are found
                        # (e.g., user specified only WHITE, or theme has no base colors)
                        # Default to GREEN if it's in active_colors, otherwise keep "GREEN" and hope for the best
                        if "GREEN" in active_colors:
                            base_color_name = "GREEN"
                        # else: base_color_name remains "GREEN", implies classic-like behavior or error if GREEN not in active_colors
                    else:
                        base_color_name = random.choice(
                            available_base_colors_in_palette
                        )

                # Fetch colors from active_colors, with fallbacks to direct AnsiColor enum values
                # This ensures that even if a color is missing from active_colors (e.g. due to user filtering),
                # we try to get a sensible default.
                actual_base_color = active_colors.get(
                    base_color_name, AnsiColors.GREEN.value
                )
                bright_variant_key = f"BRIGHT_{base_color_name}"
                actual_bright_color = active_colors.get(
                    bright_variant_key, actual_base_color
                )
                color_white = active_colors.get("WHITE", AnsiColors.WHITE.value)

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

                # Apply color based on distance from head
                if distance_from_head == 0:  # Head of the trail
                    char_list.append(f"{c_head}{char_to_render}")
                elif distance_from_head <= args.bright_length:  # Bright segment
                    char_list.append(f"{c_seg1}{char_to_render}")
                else:  # Dim part of the trail
                    char_list.append(f"{c_seg2}{char_to_render}")
            else:
                char_list.append(" ")  # Empty space if no character here
        frame_buffer.append("".join(char_list))
    return frame_buffer


def run_animation_loop(
    args,
    width,
    height,
    colors,
    columns,
    available_char_sets,  # Added available_char_sets
):
    """Runs the main animation loop."""
    # colors is active_theme_colors_param
    # columns is columns_param

    MIN_EFFECTIVE_SLEEP = 0.005

    while True:
        columns = update_column_states(  # columns is updated in place and also returned
            columns,
            width,
            height,
            args.density,
            args.trail_length,
            available_char_sets,  # Pass available_char_sets
        )
        frame_buffer = render_frame_buffer(
            columns,
            width,
            height,
            colors,  # This is active_theme_colors
            args,
            available_char_sets,  # Pass available_char_sets
            args.glitch_rate,  # Pass glitch_rate
        )
        # columns_param = current_columns # columns is already updated

        reset_code = colors.get("RESET", AnsiColors.RESET.value)
        sys.stdout.write("\033[H" + "\n".join(frame_buffer) + reset_code)
        sys.stdout.flush()

        actual_sleep_time = max(args.speed, MIN_EFFECTIVE_SLEEP)
        time.sleep(actual_sleep_time)
