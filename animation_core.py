import math
import random
import sys
import time
import wcwidth
from config import AnsiColors, DEFAULT_CHAR_SETS
from matrix_math import * # Import 3D math utilities

# Globals for view dimensions, to be set in initialize_animation_parameters
WORLD_WIDTH_VIEW = 0.0
WORLD_DEPTH_VIEW = 0.0

# CYLINDER_RADIUS global is removed.

def initialize_animation_parameters(width, height, args):
    """Initializes characters, colors, and the new 3D rain stream structures."""
    global WORLD_WIDTH_VIEW, WORLD_DEPTH_VIEW

    # final_theme_colors setup (existing logic, can be kept as is)
    final_theme_colors = {}
    if args.theme == "classic":
        final_theme_colors = {
            "WHITE": AnsiColors.WHITE.value,
            "BRIGHT_GREEN": AnsiColors.BRIGHT_GREEN.value,
            "GREEN": AnsiColors.GREEN.value,
            "RESET": AnsiColors.RESET.value,
        }
    elif args.theme == "colorful":
        final_theme_colors = {
            "RESET": AnsiColors.RESET.value,
            "WHITE": AnsiColors.WHITE.value,
        }
        available_ansi_colors = {name: member.value for name, member in AnsiColors.__members__.items()}
        user_specified_color_names = []
        if args.base_colors:
            user_specified_color_names = [name.strip().upper() for name in args.base_colors.split(',') if name.strip()]
        selected_user_colors_count = 0
        if user_specified_color_names:
            for name in user_specified_color_names:
                if name in available_ansi_colors and "BRIGHT_" not in name and name not in ["WHITE", "RESET"]:
                    final_theme_colors[name] = available_ansi_colors[name]
                    bright_name = f"BRIGHT_{name}"
                    if bright_name in available_ansi_colors:
                        final_theme_colors[bright_name] = available_ansi_colors[bright_name]
                    selected_user_colors_count += 1
                elif name:
                    print(f"Warning: Invalid or unsuitable base color name '{name}' in --base-colors. Ignoring.", file=sys.stderr)
            if selected_user_colors_count == 0:
                print("Warning: No valid base colors from --base-colors were found. Using default full 'colorful' palette.", file=sys.stderr)
                for color_name, color_value in available_ansi_colors.items():
                    if color_name != "RESET": final_theme_colors[color_name] = color_value
        else:
            for color_name, color_value in available_ansi_colors.items():
                if color_name != "RESET": final_theme_colors[color_name] = color_value
        current_base_colors_in_palette = [k for k in final_theme_colors if "BRIGHT_" not in k and k not in ["WHITE", "RESET"]]
        if not current_base_colors_in_palette:
            print("Warning: The 'colorful' palette ended up with no usable base colors. Adding GREEN as a fallback.", file=sys.stderr)
            if "GREEN" in available_ansi_colors: final_theme_colors["GREEN"] = available_ansi_colors["GREEN"]
            if "BRIGHT_GREEN" in available_ansi_colors: final_theme_colors["BRIGHT_GREEN"] = available_ansi_colors["BRIGHT_GREEN"]

    # Define World Parameters
    WORLD_WIDTH = float(width)
    WORLD_DEPTH = float(width)
    SPAWN_Y = float(height) / 2.0

    # Set globals for view dimensions
    WORLD_WIDTH_VIEW = WORLD_WIDTH
    WORLD_DEPTH_VIEW = WORLD_DEPTH

    # Determine number of streams
    # args.density could be used here if it's intended to mean overall "rain density"
    # For now, let's base it on width, ensuring it's an int.
    # The previous INITIAL_STREAM_COUNT = args.width * 2 might be too much if args.width is screen width.
    # Let's use width (passed in, actual terminal width)
    INITIAL_STREAM_COUNT = int(width * args.density * 5) # Adjust factor as needed, density is 0-1
    if INITIAL_STREAM_COUNT < 1: INITIAL_STREAM_COUNT = 1 # Ensure at least one stream

    active_rain_streams = []
    for _ in range(INITIAL_STREAM_COUNT):
        start_x = random.uniform(-WORLD_WIDTH / 2.0, WORLD_WIDTH / 2.0)
        start_z = random.uniform(-WORLD_DEPTH / 2.0, WORLD_DEPTH / 2.0)

        char_set_idx = random.randrange(len(DEFAULT_CHAR_SETS))
        current_char_set = DEFAULT_CHAR_SETS[char_set_idx]
        initial_char_code = random.choice(current_char_set)

        # Ensure single-width character for simplicity in rendering for now
        # Fallback character if a wide char is chosen.
        # This check might be better placed during actual character rendering/selection per point.
        if wcwidth.wcwidth(initial_char_code) != 1:
            initial_char_code = "X"
            # Find a suitable fallback from available sets if 'X' is not ideal
            for cs in DEFAULT_CHAR_SETS:
                if "X" in cs: break # Assuming 'X' is common enough
                elif len(cs) > 0 and wcwidth.wcwidth(cs[0]) == 1 : initial_char_code = cs[0]; break


        vertical_speed = -1.0 # Fixed vertical speed for now (moving towards negative Y)

        stream = {
            'id': random.randint(10000, 99999),
            'points': [{'pos': [start_x, SPAWN_Y, start_z, 1.0],
                        'char': initial_char_code,
                        'state': 'head'}],
            'velocity': [0, vertical_speed, 0],
            'char_set_index': char_set_idx,
            'trail_length': args.trail_length,
            'head_y': SPAWN_Y
        }
        active_rain_streams.append(stream)

    # Return the character sets, theme colors, and the newly initialized streams
    return DEFAULT_CHAR_SETS, final_theme_colors, active_rain_streams


def update_column_states(columns, width, height, density, trail_length, num_char_sets): # This function will be replaced/refactored
    """Placeholder for updating rain streams. Currently not compatible with new structure."""
    # This function needs a complete overhaul to work with 'active_rain_streams'
    # For now, it's bypassed in run_animation_loop.
    return columns # No-op for now, returning the old 'columns' structure if it were passed.


def render_frame_buffer(active_rain_streams, width, height, char_sets, active_colors, args,
                        current_x_rot, current_y_rot, current_z_rot):
    """Renders the current frame into a buffer using a 3D pipeline with multi-axis rotation."""

    final_frame_buffer_chars = [[" " for _ in range(width)] for _ in range(height)]
    # Depth buffer: store view_space_pos[2] (negative Z in front). Closer points are less negative.
    depth_buffer_frame = [[-float('inf') for _ in range(width)] for _ in range(height)]

    aspect_ratio = float(width) / float(height) if height > 0 else 1.0
    eye_z_distance = WORLD_WIDTH_VIEW # Base distance on world width
    eye = [0, WORLD_WIDTH_VIEW / 10.0, eye_z_distance]
    target = [0, 0, 0]
    up = [0, 1, 0]

    view_mat = look_at_matrix(eye, target, up)
    proj_mat = perspective_projection_matrix(fov_deg=75, aspect_ratio=aspect_ratio, near=0.1, far=WORLD_DEPTH_VIEW * 2 + eye_z_distance)

    # Create individual and combined rotation matrices
    rot_mat_x = rotation_matrix_x(current_x_rot)
    rot_mat_y = rotation_matrix_y(current_y_rot)
    rot_mat_z = rotation_matrix_z(current_z_rot)

    # Combine rotation matrices (ZYX order: Rx, then Ry, then Rz)
    temp_rot_matrix = multiply_matrices(rot_mat_y, rot_mat_x)
    world_rotation_matrix = multiply_matrices(rot_mat_z, temp_rot_matrix)

    for stream in active_rain_streams:
        for point_data in stream['points']:
            world_pos_vec = point_data['pos'] # [x,y,z,w]

            # Apply combined rotation matrix
            rotated_pos = multiply_matrix_vector(world_rotation_matrix, world_pos_vec)
            view_space_pos = multiply_matrix_vector(view_mat, rotated_pos)

            # Basic near plane clipping (view_space_pos[2] is negative Z in front of camera)
            if view_space_pos[2] > -0.1: # If Z is not negative enough (too close to or behind camera)
                continue
            # Add far plane clipping if needed: if view_space_pos[2] < -(WORLD_DEPTH_VIEW * 2 + eye_z_distance): continue


            projected_pos_h = multiply_matrix_vector(proj_mat, view_space_pos)

            w_h = projected_pos_h[3]
            if abs(w_h) < 1e-6: continue

            ndc_x = projected_pos_h[0] / w_h
            ndc_y = projected_pos_h[1] / w_h
            # ndc_z = projected_pos_h[2] / w_h # Not strictly needed for 2D char placement if depth is from view_space

            screen_x = int((ndc_x + 1.0) * 0.5 * width)
            screen_y = int((1.0 - (ndc_y + 1.0) * 0.5) * height) # Y is inverted

            current_depth = view_space_pos[2] # View space Z (negative in front)

            if 0 <= screen_x < width and 0 <= screen_y < height:
                if current_depth > depth_buffer_frame[screen_y][screen_x]:
                    depth_buffer_frame[screen_y][screen_x] = current_depth
                    # TODO: Color and character determination will be more complex later
                    # For now, just use the character from point_data, no color.
                    final_frame_buffer_chars[screen_y][screen_x] = point_data['char']

    output_frame_buffer = []
    for r in range(height):
        output_frame_buffer.append("".join(final_frame_buffer_chars[r]))
    return output_frame_buffer


def run_animation_loop(args, width, height, char_sets, streams_param, active_theme_colors_param): # Renamed columns_param
    """Runs the main animation loop."""
    active_colors_dict = active_theme_colors_param
    MIN_EFFECTIVE_SLEEP = 0.005
    current_y_rotation_angle = 0.0
    current_x_rotation_angle = 0.0
    current_z_rotation_angle = 0.0

    while True:
        actual_sleep_time = max(args.speed, MIN_EFFECTIVE_SLEEP)

        # Update rotation angles
        # Using args.y_rotation_speed as the base for now, will be replaced by specific args later
        placeholder_x_rotation_speed = args.y_rotation_speed * 0.5
        placeholder_z_rotation_speed = args.y_rotation_speed * 0.3

        current_x_rotation_angle += placeholder_x_rotation_speed
        current_y_rotation_angle += args.y_rotation_speed
        current_z_rotation_angle += placeholder_z_rotation_speed

        # Optional: normalize angles (e.g., to keep them within 0-2PI or -PI to PI)
        # current_x_rotation_angle %= (2 * math.pi)
        # current_y_rotation_angle %= (2 * math.pi)
        # current_z_rotation_angle %= (2 * math.pi)

        # Temporarily bypass stream state updates
        current_streams = streams_param # No state update for now

        frame_buffer = render_frame_buffer(
            current_streams, width, height, char_sets, active_colors_dict, args,
            current_x_rotation_angle, current_y_rotation_angle, current_z_rotation_angle
        )
        # streams_param = current_streams

        # Ensure RESET code is correctly fetched. It should be directly in active_colors_dict.
        reset_code = active_colors_dict.get("RESET", AnsiColors.RESET.value) # Fallback to enum default
        sys.stdout.write("\033[H" + "\n".join(frame_buffer) + reset_code)
        sys.stdout.flush()

        actual_sleep_time = max(args.speed, MIN_EFFECTIVE_SLEEP)
        time.sleep(actual_sleep_time)
