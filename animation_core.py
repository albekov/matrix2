import math
import random
import sys
import time
import wcwidth
from config import AnsiColors, DEFAULT_CHAR_SETS

def initialize_animation_parameters(width, height, args):
    """Initializes characters, colors, and column states."""
    # Use DEFAULT_CHAR_SETS from config.py
    chars = DEFAULT_CHAR_SETS

    # Each column stores (y_position, char_set_index, z_position)
    # Initialize columns with a random character set index and z_position for each column
    columns = [(0, random.randrange(len(chars)), random.randint(0, 10)) for _ in range(width)]

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
        available_ansi_colors = {name: member.value for name, member in AnsiColors.__members__.items()}

        user_specified_color_names = []
        if args.base_colors:  # If user provided any string for --base-colors
            user_specified_color_names = [name.strip().upper() for name in args.base_colors.split(',') if name.strip()]

        selected_user_colors_count = 0
        if user_specified_color_names:  # If there are actual names to process
            for name in user_specified_color_names:
                # Check if the name is a valid base color (not BRIGHT_*, not WHITE, not RESET)
                if name in available_ansi_colors and "BRIGHT_" not in name and name not in ["WHITE", "RESET"]:
                    final_theme_colors[name] = available_ansi_colors[name]
                    bright_name = f"BRIGHT_{name}"
                    if bright_name in available_ansi_colors:
                        final_theme_colors[bright_name] = available_ansi_colors[bright_name]
                    selected_user_colors_count += 1
                elif name:  # Non-empty but invalid/unsuitable name
                    print(f"Warning: Invalid or unsuitable base color name '{name}' in --base-colors. Ignoring.", file=sys.stderr)

            if selected_user_colors_count == 0: # User specified names, but none were valid base colors
                print("Warning: No valid base colors from --base-colors were found. Using default full 'colorful' palette.", file=sys.stderr)
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
        current_base_colors_in_palette = [k for k in final_theme_colors if "BRIGHT_" not in k and k not in ["WHITE", "RESET"]]
        if not current_base_colors_in_palette:
            print("Warning: The 'colorful' palette ended up with no usable base colors. Adding GREEN as a fallback.", file=sys.stderr)
            if "GREEN" in available_ansi_colors: final_theme_colors["GREEN"] = available_ansi_colors["GREEN"]
            if "BRIGHT_GREEN" in available_ansi_colors: final_theme_colors["BRIGHT_GREEN"] = available_ansi_colors["BRIGHT_GREEN"]

    return chars, final_theme_colors, columns


def update_column_states(columns, width, height, density, trail_length, num_char_sets):
    """Updates the state of each column for the next frame."""
    for i in range(width):
        y_position, char_set_index, z_position = columns[i]  # Unpack z_position
        if y_position == 0:
            if random.random() < density:
                # Start a new drop with a randomly selected char set and z_position for this column
                columns[i] = (1, random.randrange(num_char_sets), random.randint(0, 10))
            # If no new drop, z_position remains unchanged (implicitly, as columns[i] isn't updated here)
        else:
            y_position += 1
            # Reset column if trail is off screen
            if y_position - trail_length > height:
                columns[i] = (0, char_set_index, z_position) # Keep char_set_index and z_position until new drop
            else:
                columns[i] = (y_position, char_set_index, z_position) # Preserve z_position
    return columns


def render_frame_buffer(columns, width, height, char_sets, active_colors, args, current_rotation_angle):
    """Renders the current frame into a buffer."""
    frame_buffer = []
    for y_coord in range(1, height + 1): # Renamed y to y_coord to avoid conflict with column's y_position
        char_list = [" "] * width  # Initialize row with spaces for horizontal shift
        for x in range(width):
            trail_head_y, char_set_index, z_position = columns[x] # Unpack z_position
            # Ensure char_set_index is valid for char_sets
            if not (0 <= char_set_index < len(char_sets)): # Defensive check
                continue # Skip if invalid, char_list[x] remains " "

            current_char_set = char_sets[char_set_index]
            # Check if the current y_coord is part of this column's trail
            if trail_head_y > 0 and trail_head_y - args.trail_length < y_coord <= trail_head_y:
                distance_from_head = trail_head_y - y_coord

                original_char = random.choice(current_char_set)

                if wcwidth.wcwidth(original_char) != 1:
                    original_char = " "

                char_to_render = original_char

                if args.glitch_rate > 0 and random.random() < args.glitch_rate:
                    glitch_candidate = random.choice(current_char_set)
                    if wcwidth.wcwidth(glitch_candidate) == 1:
                        char_to_render = glitch_candidate

                base_color_name = "GREEN" # Default for classic theme or fallback
                if args.theme == "colorful":
                    available_base_colors = [
                        name for name in active_colors
                        if "BRIGHT_" not in name and name not in ["WHITE", "RESET"] and name in AnsiColors.__members__
                    ]
                    if not available_base_colors:
                         if "GREEN" in active_colors : base_color_name = "GREEN"
                    else:
                        base_color_name = random.choice(available_base_colors)

                actual_base_color = active_colors.get(base_color_name, AnsiColors.GREEN.value)
                bright_variant_key = f"BRIGHT_{base_color_name}"
                actual_bright_color = active_colors.get(bright_variant_key, actual_base_color)
                color_white = active_colors.get("WHITE", AnsiColors.WHITE.value)

                c_head_orig, c_seg1_orig, c_seg2_orig = color_white, actual_bright_color, actual_base_color # Default (normal)
                if args.color_intensity == "dim":
                    c_head_orig, c_seg1_orig, c_seg2_orig = actual_bright_color, actual_base_color, actual_base_color
                elif args.color_intensity == "bright":
                    c_head_orig, c_seg1_orig, c_seg2_orig = color_white, color_white, actual_bright_color

                # Refined Perspective (Dimming) using depth_effect_strength
                depth_influence = (z_position / 10.0) * args.depth_effect_strength

                # Rotation (Horizontal Shift) - z_factor calculation is fine
                # Using trail_head_y for a more cohesive shift of the entire column drop.
                # z_position incorporated: further away (larger z) shifts less.
                # (11 - z_position) / 10.0 makes z=10 shift by 0.1x, z=0 shift by 1.1x (approx)
                # (height / 2.0 - y_coord) for y-dependent shift (center rows shift less)
                # Scaled by 0.3 as an arbitrary factor
                # Shift direction depends on y_coord relative to height/2 and rotation angle
                y_factor = (height / 2.0 - y_coord) / (height / 2.0) if height > 1 else 0 # Normalized y distance from center
                z_factor = (11.0 - z_position) / 10.0 # Closer items (smaller z) shift more

                # Simplified horizontal_shift for now, focusing on y and angle.
                # The subtask asks for: int( (y - height/2) * math.sin(current_rotation_angle) * 0.1 )
                # Let's use y_coord here for the current character's row.
                horizontal_shift = int( (y_coord - height/2.0) * math.sin(current_rotation_angle) * 0.2 * z_factor )

                final_x = x + horizontal_shift

                applied_color = c_seg2_orig # Default to the dimmest color

                if distance_from_head == 0: # Head of the trail
                    if depth_influence > 0.7: # Adjusted threshold
                        applied_color = c_seg2_orig
                    elif depth_influence > 0.4: # Adjusted threshold
                        applied_color = c_seg1_orig
                    else:
                        applied_color = c_head_orig
                elif distance_from_head <= args.bright_length: # Bright part
                    if depth_influence > 0.6: # Adjusted threshold
                        applied_color = c_seg2_orig
                    else:
                        applied_color = c_seg1_orig
                # else: Dim part, applied_color is already c_seg2_orig

                if 0 <= final_x < width:
                    char_list[final_x] = f"{applied_color}{char_to_render}"
            # If not in trail, char_list[x] remains " " due to prefill
        frame_buffer.append("".join(char_list))
    return frame_buffer


def run_animation_loop(args, width, height, char_sets, columns_param, active_theme_colors_param):
    """Runs the main animation loop."""
    active_colors_dict = active_theme_colors_param
    MIN_EFFECTIVE_SLEEP = 0.005
    current_rotation_angle = 0.0

    while True:
        actual_sleep_time = max(args.speed, MIN_EFFECTIVE_SLEEP)

        # Update rotation angle using args.rotation_speed
        current_rotation_angle += args.rotation_speed * actual_sleep_time
        # Optional: normalize angle if it grows too large, though math.sin handles large angles.
        # if abs(current_rotation_angle) > 2 * math.pi:
        #     current_rotation_angle %= (2 * math.pi)

        current_columns = update_column_states(
            columns_param, width, height, args.density, args.trail_length, len(char_sets)
        )
        frame_buffer = render_frame_buffer(
            current_columns, width, height, char_sets, active_colors_dict, args, current_rotation_angle
        )
        columns_param = current_columns

        # Ensure RESET code is correctly fetched. It should be directly in active_colors_dict.
        reset_code = active_colors_dict.get("RESET", AnsiColors.RESET.value) # Fallback to enum default
        sys.stdout.write("\033[H" + "\n".join(frame_buffer) + reset_code)
        sys.stdout.flush()

        actual_sleep_time = max(args.speed, MIN_EFFECTIVE_SLEEP)
        time.sleep(actual_sleep_time)
