import sys

from animation_core import (  # update_column_states and render_frame_buffer are used by run_animation_loop,; and initialize_animation_parameters, not directly by main
    initialize_animation_parameters,
    run_animation_loop,
)
from config import AnsiColors, parse_arguments
from terminal_utils import get_terminal_dimensions

# import os # os is not directly used in main.py after refactoring get_terminal_dimensions
# No need for random, time, wcwidth, argparse if no longer directly used in main.py


if __name__ == "__main__":
    args = parse_arguments()
    if (
        args
    ):  # parse_arguments returns None on validation failure for some existing checks
        width, height = get_terminal_dimensions(args)

        # initialize_animation_parameters now uses DEFAULT_CHAR_SETS from config
        # and AnsiColors for theme definitions.
        # It returns:
        # 1. chars (which will be DEFAULT_CHAR_SETS)
        # 2. available_char_sets (list of lists of characters, e.g., [['a','b'], ['0','1']])
        # 3. final_theme_colors (a dictionary of color strings like {"WHITE": "[97m", ...})
        columns_state, available_char_sets, active_theme_colors = (
            initialize_animation_parameters(args, width, height) # Corrected order and return values
        )

        try:
            # Hide cursor
            sys.stdout.write("[?25l")

            run_animation_loop(
                args,
                width,
                height,
                active_theme_colors, # This maps to 'colors' in run_animation_loop
                columns_state,       # This maps to 'columns'
                available_char_sets  # This maps to 'available_char_sets'
            )

        except KeyboardInterrupt:
            # Show cursor and reset color
            # Use AnsiColors.RESET.value directly
            sys.stdout.write(f"[?25h{AnsiColors.RESET.value}")
            print("\nAnimation stopped.")
        except Exception as e:
            # Show cursor and reset color in case of other errors
            sys.stdout.write(f"[?25h{AnsiColors.RESET.value}")
            print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
            sys.exit(1)  # Exit with error status
    else:
        # args is None, meaning parse_arguments detected an issue and printed a message.
        # sys.exit(1) might have already been called in parse_arguments for some error types.
        # If not, we ensure an error exit status here.
        sys.exit(1)
