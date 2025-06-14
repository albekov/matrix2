import math
import random
import sys
import time
import wcwidth
from config import AnsiColors, DEFAULT_CHAR_SETS

# Global variable for cylinder radius, will be set in initialize_animation_parameters
CYLINDER_RADIUS = 0.0

def initialize_animation_parameters(width, height, args):
    """Initializes characters, colors, and column states for cylindrical display."""
    global CYLINDER_RADIUS
    # Update CYLINDER_RADIUS calculation to use the new factor from args
    CYLINDER_RADIUS = (width / 3.0) * args.cylindrical_radius_factor

    # Use DEFAULT_CHAR_SETS from config.py
    chars = DEFAULT_CHAR_SETS

    # Each column stores (y_position, char_set_index, z_position, base_angle_on_cylinder)
    columns = []
    for i in range(width):
        y_pos = 0  # Initial y_position, all drops start off-screen or at the top
        char_set_idx = random.randrange(len(chars))
        z_pos = random.randint(0, 10)  # Existing random z_position for per-drop effects

        # Calculate the base angle for this column on the cylinder surface
        # This distributes columns around the full circumference (0 to 2*PI)
        base_angle_on_cylinder = (i / float(width)) * 2.0 * math.pi

        columns.append((y_pos, char_set_idx, z_pos, base_angle_on_cylinder))

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
    """Updates the state of each column for the next frame, preserving base_angle."""
    for i in range(width):
        # Unpack all four elements, including the base_angle_on_cylinder
        y_position, char_set_index, z_position, base_angle = columns[i]

        if y_position == 0: # Column is ready for a new drop
            if random.random() < density:
                # Start a new drop: reset y_pos, new char_set, new z_pos, keep existing base_angle
                columns[i] = (1, random.randrange(num_char_sets), random.randint(0, 10), base_angle)
            # If no new drop starts, the column state (including base_angle) remains unchanged (y_position is still 0)
        else: # Column is currently active (trail is falling)
            y_position += 1
            # Reset column if trail is off screen
            if y_position - trail_length > height:
                # Reset y_pos, keep char_set_index, z_pos, and base_angle for the next potential drop
                columns[i] = (0, char_set_index, z_position, base_angle)
            else:
                # Continue drop: update y_pos, keep char_set_index, z_pos, and base_angle
                columns[i] = (y_position, char_set_index, z_position, base_angle)
    return columns


def render_frame_buffer(columns, width, height, char_sets, active_colors, args, current_rotation_angle):
    """Renders the current frame into a buffer using cylindrical projection."""
    frame_buffer = []
    for y_coord in range(1, height + 1):
        char_list = [" "] * width  # Initialize row with spaces
        depth_buffer_row = [-float('inf')] * width # Initialize depth buffer for this row

        for x_orig_idx in range(len(columns)):
            # Unpack Column Data
            trail_head_y, char_set_index, z_prop_individual_drop, base_angle = columns[x_orig_idx]

            # Calculate World Position & Cylindrical Depth
            effective_angle = base_angle + current_rotation_angle
            # Ensure CYLINDER_RADIUS is accessed (it's a global in this module)
            x_world = CYLINDER_RADIUS * math.cos(effective_angle)
            z_world = CYLINDER_RADIUS * math.sin(effective_angle) # Positive z_world is towards viewer

            # Backface Culling
            if z_world < 0.0:
                continue  # Skip this column for this row if it's on the back of the cylinder

            # Character Visibility in Current Row (Existing Logic)
            is_char_visible_in_row = (trail_head_y > 0 and
                                      trail_head_y - args.trail_length < y_coord <= trail_head_y)
            if not is_char_visible_in_row:
                continue

            # Projection to Screen X
            screen_x = int(round(x_world + width / 2.0))

            # Screen Bounds Check
            if not (0 <= screen_x < width):
                continue

            # Z-BUFFER CHECK STARTS HERE
            if z_world > depth_buffer_row[screen_x]:
                # This character is closer than what's already at this screen_x for this row.
                depth_buffer_row[screen_x] = z_world

                # Proceed with existing character and color determination logic
                distance_from_head = trail_head_y - y_coord
                if not (0 <= char_set_index < len(char_sets)): # Should be caught by earlier check too
                    continue

                current_char_set = char_sets[char_set_index]
                original_char = random.choice(current_char_set)
                if wcwidth.wcwidth(original_char) != 1:
                    original_char = " "
                char_to_render = original_char
                if args.glitch_rate > 0 and random.random() < args.glitch_rate:
                    glitch_candidate = random.choice(current_char_set)
                    if wcwidth.wcwidth(glitch_candidate) == 1:
                        char_to_render = glitch_candidate

                base_color_name = "GREEN"
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

                c_head_orig, c_seg1_orig, c_seg2_orig = color_white, actual_bright_color, actual_base_color
                if args.color_intensity == "dim":
                    c_head_orig, c_seg1_orig, c_seg2_orig = actual_bright_color, actual_base_color, actual_base_color
                elif args.color_intensity == "bright":
                    c_head_orig, c_seg1_orig, c_seg2_orig = color_white, color_white, actual_bright_color

                depth_influence_drop = (z_prop_individual_drop / 10.0) * args.depth_effect_strength

                # Stage 1 Dimming: Based on individual drop's z_prop and trail position
                color_selected_by_drop_depth = c_seg2_orig # Default to dimmest
                if distance_from_head == 0: # Head
                    if depth_influence_drop > 0.7: color_selected_by_drop_depth = c_seg2_orig
                    elif depth_influence_drop > 0.4: color_selected_by_drop_depth = c_seg1_orig
                    else: color_selected_by_drop_depth = c_head_orig
                elif distance_from_head <= args.bright_length: # Bright segment
                    if depth_influence_drop > 0.6: color_selected_by_drop_depth = c_seg2_orig
                    else: color_selected_by_drop_depth = c_seg1_orig
                # Else: Dim segment, color_selected_by_drop_depth is already c_seg2_orig

                # Stage 2 Dimming: Based on cylindrical depth (z_world)
                final_char_color_for_render = color_selected_by_drop_depth

                if CYLINDER_RADIUS > 0.001: # Avoid division by zero or near-zero radius issues
                    cylinder_depth_factor = z_world / CYLINDER_RADIUS  # Normalized: 0 (edge) to 1 (front)

                    # (1.0 - cylinder_depth_factor) is 0 for front, 1 for edge.
                    cylinder_side_dim_amount = (1.0 - cylinder_depth_factor) * args.depth_effect_strength

                    if cylinder_side_dim_amount > 0.65: # Significantly on the side
                        if color_selected_by_drop_depth == c_head_orig:
                            final_char_color_for_render = c_seg1_orig
                        elif color_selected_by_drop_depth == c_seg1_orig:
                            final_char_color_for_render = c_seg2_orig
                    elif cylinder_side_dim_amount > 0.35: # Somewhat on the side
                        if color_selected_by_drop_depth == c_head_orig:
                            final_char_color_for_render = c_seg1_orig

                # Render Character
                char_list[screen_x] = f"{final_char_color_for_render}{char_to_render}"
            # ELSE: (z_world <= depth_buffer_row[screen_x])
                # Another character is already rendered at this screen_x and is closer or at the same depth.
                # Do nothing, effectively letting the previous character remain.

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
