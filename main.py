import argparse
import os
import random
import sys
import time


def main():
    """
    Sets up the console and runs the Matrix digital rain animation with a fade effect.
    """
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

    # Validate command-line arguments.
    if not (0 < args.speed):
        print("Error: Animation speed must be a positive number.")
        return
    if not (0 < args.density <= 1):
        print("Error: Column density must be between 0 and 1.")
        return
    if not (2 < args.trail_length):
        print("Error: Trail length must be greater than 2.")
        return

    # A string containing a variety of characters for the digital rain.
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()"

    # Get terminal dimensions.
    try:
        width, height = os.get_terminal_size()
    except OSError:
        # Fallback to default dimensions if unable to get terminal size.
        width, height = 80, 24
        print("Warning: Unable to get terminal size. Using default 80x24.")

    # ANSI escape codes for colors.
    # The fade effect is achieved by stepping from white to bright green to normal green.
    WHITE = "\033[97m"
    BRIGHT_GREEN = "\033[92m"
    GREEN = "\033[32m"
    RESET = "\033[0m"

    # `columns` stores the y-coordinate for the head of the trail in each column.
    # A value of 0 means the column is inactive.
    columns = [0] * width

    try:
        while True:
            # First, update the state of all columns for the next frame.
            for i in range(width):
                # If a column is inactive (0), randomly decide to activate it.
                if columns[i] == 0:
                    if random.random() < args.density:
                        columns[i] = 1  # Activate it; trail head starts at row 1.
                # If active, move the trail head down.
                else:
                    columns[i] += 1
                    # Deactivate if the trail is fully off-screen.
                    if columns[i] - args.trail_length > height:
                        columns[i] = 0

            # Build the frame buffer as a list of strings (rows).
            frame_buffer = []
            for y in range(1, height + 1):
                row_str = ""
                for x in range(width):
                    trail_head_y = columns[x]
                    trail_len = args.trail_length

                    # Check if the current coordinate (x, y) should have a character.
                    if (
                        trail_head_y > 0
                        and trail_head_y - trail_len < y <= trail_head_y
                    ):
                        distance_from_head = trail_head_y - y
                        char = random.choice(chars)

                        # Determine color based on distance from the trail head.
                        if distance_from_head == 0:
                            # Head of the trail is the brightest.
                            row_str += f"{WHITE}{char}"
                        elif distance_from_head <= 2:
                            # The next 2 characters are bright green.
                            row_str += f"{BRIGHT_GREEN}{char}"
                        else:
                            # The rest of the trail is normal green.
                            row_str += f"{GREEN}{char}"
                    else:
                        # This is an empty space.
                        row_str += " "
                frame_buffer.append(row_str)

            # Print the entire frame at once to reduce flicker.
            # "\033[H" moves the cursor to the home position (top-left).
            sys.stdout.write("\033[H" + "\n".join(frame_buffer) + RESET)
            sys.stdout.flush()

            # Control the animation speed.
            time.sleep(args.speed)

    except KeyboardInterrupt:
        # Gracefully exit on user interruption (Ctrl+C).
        # Ensure the cursor is visible and color is reset.
        sys.stdout.write("\033[?25h" + RESET)  # Show cursor
        print("\nAnimation stopped.")


if __name__ == "__main__":
    main()
