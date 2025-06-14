import os


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
