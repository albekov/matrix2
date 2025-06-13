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
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()"
    colors = {
        "WHITE": "\033[97m",
        "BRIGHT_GREEN": "\033[92m",
        "GREEN": "\033[32m",
        "RESET": "\033[0m",
    }
    columns = [0] * width
    return chars, colors, columns


def update_column_states(columns, width, height, density, trail_length):
    """Updates the state of each column for the next frame."""
    for i in range(width):
        if columns[i] == 0:
            if random.random() < density:
                columns[i] = 1
        else:
            columns[i] += 1
            if columns[i] - trail_length > height:
                columns[i] = 0
    return columns


def render_frame_buffer(columns, width, height, trail_length, chars, colors):
    """Renders the current frame into a buffer."""
    frame_buffer = []
    for y in range(1, height + 1):
        row_str = ""
        for x in range(width):
            trail_head_y = columns[x]
            if trail_head_y > 0 and trail_head_y - trail_length < y <= trail_head_y:
                distance_from_head = trail_head_y - y
                char = random.choice(chars)
                if distance_from_head == 0:
                    row_str += f"{colors['WHITE']}{char}"
                elif distance_from_head <= 2:
                    row_str += f"{colors['BRIGHT_GREEN']}{char}"
                else:
                    row_str += f"{colors['GREEN']}{char}"
            else:
                row_str += " "
        frame_buffer.append(row_str)
    return frame_buffer


def run_animation_loop(args, width, height, chars, colors, columns):
    """Runs the main animation loop."""
    while True:
        columns = update_column_states(
            columns, width, height, args.density, args.trail_length
        )
        frame_buffer = render_frame_buffer(
            columns, width, height, args.trail_length, chars, colors
        )
        sys.stdout.write("\033[H" + "\n".join(frame_buffer) + colors["RESET"])
        sys.stdout.flush()
        time.sleep(args.speed)


if __name__ == "__main__":
    args = parse_arguments()
    if args:
        width, height = get_terminal_dimensions(args)
        chars, colors, columns = initialize_animation_parameters(width, height, args)
        try:
            # Hide cursor
            sys.stdout.write("\033[?25l")
            run_animation_loop(args, width, height, chars, colors, columns)
        except KeyboardInterrupt:
            # Show cursor and reset color
            sys.stdout.write("\033[?25h" + colors["RESET"])
            print("\nAnimation stopped.")
