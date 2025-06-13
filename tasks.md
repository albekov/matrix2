# Detailed Task List for Console Matrix Animation

This document outlines specific tasks to improve and enhance the Python-based console Matrix animation script (`main.py`). Each task includes detailed instructions, context, and expected outcomes.

## 1. Code Structure and Readability

### 1.1. Refactor `main()` Function
*   **Objective:** Improve modularity and readability by breaking down the `main()` function in `main.py` into smaller, focused functions.
*   **Current State:** The `main.py` script has most of its logic within a single `main()` function.
*   **Instructions:**
    1.  **Identify Logical Blocks:** Review the existing `main()` function and identify distinct sections of code:
        *   Argument parsing and validation.
        *   Initialization of animation parameters (terminal size, character sets, colors, column states).
        *   The main animation loop.
        *   Within the loop: updating column states and rendering the frame.
    2.  **Create `parse_arguments()` function:**
        *   Move all `argparse` setup, argument parsing (`parser.parse_args()`), and argument validation logic into this function.
        *   This function should return the `args` object.
    3.  **Create `initialize_animation_parameters()` function:**
        *   This function will take `args` (and potentially `width`, `height` if terminal size detection is also moved here or passed in).
        *   Move the setup for `chars`, ANSI color constants (until they are refactored into an Enum), initial `columns` state array.
        *   Return these initialized parameters (e.g., `chars`, `colors_enum_or_dict`, `columns_array`).
        *   Alternatively, terminal size detection can be its own function `get_terminal_dimensions(args)` which is called before this.
    4.  **Create `update_column_states()` function:**
        *   This function will take `columns`, `width`, `height`, `args.density`, and `args.trail_length` as input.
        *   It should contain the logic for iterating `i in range(width)` to update each column's head position or activate new drops.
        *   It should return the updated `columns` list.
    5.  **Create `render_frame_buffer()` function:**
        *   This function will take `columns`, `width`, `height`, `args.trail_length`, `chars`, and color definitions (e.g., `WHITE`, `BRIGHT_GREEN`, `GREEN`) as input.
        *   It should contain the nested loops (`for y`, `for x`) to build the `frame_buffer` list of strings.
        *   It should return the `frame_buffer`.
    6.  **Create `run_animation_loop()` function:**
        *   This function will take all necessary parameters (e.g., `args`, `width`, `height`, `chars`, `colors`, `columns`).
        *   It will contain the main `while True` loop.
        *   Inside the loop, it will call `update_column_states()` and `render_frame_buffer()`.
        *   It will handle printing the frame (`sys.stdout.write`, `sys.stdout.flush`) and `time.sleep(args.speed)`.
        *   The `KeyboardInterrupt` try-except block should wrap the call to this function in the main execution block.
    7.  **Modify Main Execution Block:** The `if __name__ == "__main__":` block should now primarily:
        *   Call `parse_arguments()`.
        *   Call a function to get terminal dimensions (e.g., `get_terminal_dimensions(args)`).
        *   Call `initialize_animation_parameters()`.
        *   Call `run_animation_loop()` with the prepared data.
        *   Handle `KeyboardInterrupt` around `run_animation_loop()`.
*   **Expected Outcome:** `main.py` will be more organized, with distinct functions for different responsibilities, making it easier to read, debug, and extend.
*   **Status: COMPLETED**

### 1.2. Organize ANSI Color Constants
*   **Objective:** Make ANSI escape code constants more manageable and descriptive using an `Enum`.
*   **Current State:** Colors (`WHITE`, `BRIGHT_GREEN`, `GREEN`, `RESET`) are global string constants in `main.py`.
*   **Instructions:**
    1.  **Define an Enum:** Create an enumeration (e.g., `AnsiColors`) for the ANSI color codes:
        ```python
        from enum import Enum

        class AnsiColors(Enum):
            WHITE = "[97m"
            BRIGHT_GREEN = "[92m"
            GREEN = "[32m"
            # Add other colors if customizable themes are implemented
            # e.g., BLUE = "[34m"
            RESET = "[0m"
        ```
    2.  **Replace Direct Usage:** In the code (primarily in `render_frame_buffer()` and `KeyboardInterrupt` handler), replace hardcoded strings or old global variables with enum members:
        *   Example: `f"{WHITE}{char}"` becomes `f"{AnsiColors.WHITE.value}{char}"`.
        *   `RESET` becomes `AnsiColors.RESET.value`.
    3.  **Pass or Access Enum:** Ensure the enum is accessible where needed, likely by passing `AnsiColors` or specific members to functions like `render_frame_buffer()`. If color themes are added, an instance of this Enum or a dictionary derived from it might be passed.
*   **Expected Outcome:** Color definitions are centralized, more descriptive, and easier to manage or expand for themes.

### 1.3. Configurable Character Set (via CLI)
*   **Objective:** Allow users to specify the characters used in the animation via a command-line argument.
*   **Current State:** The `chars` variable in `main.py` is a hardcoded string.
*   **Instructions:**
    1.  **Add `argparse` Argument:** In the `parse_arguments()` function (or equivalent part of `main()` before refactoring):
        *   Add a new argument:
            ```python
            parser.add_argument(
                "--char-set",
                type=str,
                default="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()",
                help="String of characters to use for the rain. Default: Alphanumeric and symbols."
            )
            ```
    2.  **Input Validation:** Add validation for `args.char_set`:
        *   Ensure it's not empty.
            ```python
            if not args.char_set:
                print("Error: Character set cannot be empty.")
                # Consider exiting or falling back to default
                return None # Or raise an error
            ```
    3.  **Use the Argument:** In `initialize_animation_parameters()` (or equivalent), set the main `chars` variable from `args.char_set` instead of the hardcoded string.
    4.  **Ensure Usage:** Confirm that `random.choice(chars)` in `render_frame_buffer()` (or equivalent) uses this new configurable `chars` variable.
*   **Expected Outcome:** Users can customize the animation's appearance by providing their own character sets (e.g., binary "01", Katakana, etc.) via the command line.

## 2. Performance Enhancements

### 2.1. Optimize String Concatenation
*   **Objective:** Improve performance of frame rendering by using `"".join()` instead of repeated string concatenation for rows.
*   **Current State:** In `main.py` (within the frame rendering loop), `row_str += ...` is used to build each row.
*   **Instructions:**
    1.  **Locate Loop:** Identify the inner loop in `render_frame_buffer()` (or equivalent part of `main()`) where `row_str` is constructed:
        ```python
        # for y in range(1, height + 1):
        #     row_str = "" # Original
        #     for x in range(width):
        #         # ... logic ...
        #         row_str += f"{color}{char}" # Original
        #     frame_buffer.append(row_str)
        ```
    2.  **Modify Loop:** Change the logic to append characters (or character segments with color codes) to a list, and then `"".join()` the list at the end of the inner loop:
        ```python
        # for y in range(1, height + 1):
        #     char_list = [] # New
        #     for x in range(width):
        #         # ... logic ...
        #         if (condition_for_char):
        #             char_list.append(f"{color}{char_to_add}") # New
        #         else:
        #             char_list.append(" ") # New
        #     frame_buffer.append("".join(char_list)) # New
        ```
*   **Expected Outcome:** Reduced CPU usage and potentially smoother animation, especially on systems where string concatenation is slow or for larger terminal sizes.
*   **Status: COMPLETED**

## 3. Error Handling and Robustness

### 3.1. Enhanced Terminal Size Detection (with CLI Override)
*   **Objective:** Provide a more robust way to handle terminal size, allowing users to override detected dimensions if necessary.
*   **Current State:** `main.py` uses `os.get_terminal_size()` with a fallback to 80x24 and a warning.
*   **Instructions:**
    1.  **Add `argparse` Arguments:** In `parse_arguments()` (or equivalent):
        ```python
        parser.add_argument(
            "--width",
            type=int,
            default=None, # Important: default to None
            help="Manually set terminal width. Overrides automatic detection."
        )
        parser.add_argument(
            "--height",
            type=int,
            default=None, # Important: default to None
            help="Manually set terminal height. Overrides automatic detection."
        )
        ```
    2.  **Input Validation:** Add validation for `args.width` and `args.height` in `parse_arguments()`:
        *   If provided, ensure they are positive integers.
        *   Example: `if args.width is not None and args.width <= 0: print("Error: Width must be positive.")`
    3.  **Modify Dimension Acquisition Logic:** In the section where `width` and `height` are determined (e.g., a new `get_terminal_dimensions(args)` function):
        *   First, check if `args.width` and `args.height` are provided. If both are valid numbers, use them.
        *   If only one is provided, you might choose to use it and try to detect the other, or inform the user they must provide both or neither for override. For simplicity, requiring both if one is set is easier.
        *   If neither `args.width` nor `args.height` is set, then attempt `os.get_terminal_size()`.
        *   If `os.get_terminal_size()` fails and no CLI override is given, then fall back to defaults (e.g., 80x24) and print a warning.
*   **Expected Outcome:** Users whose systems have trouble with `os.get_terminal_size()` can manually specify dimensions, making the script more usable in varied environments.

### 3.2. Input Validation (General Principle)
*   **Objective:** Ensure all new user-configurable parameters have robust validation.
*   **Current State:** Existing parameters (`speed`, `density`, `trail-length`) have validation.
*   **Instructions:**
    1.  **Apply to New Arguments:** For every new command-line argument added (e.g., `char-set`, `width`, `height`, color arguments, `bright-length`, `glitch-rate`):
        *   Determine valid ranges or conditions (e.g., positive numbers, non-empty strings, specific formats).
        *   Add validation logic within the `parse_arguments()` function (or wherever args are processed).
        *   Print a clear error message and exit gracefully (or return an error indicator) if validation fails.
    *   **Example (for a hypothetical color code format):**
        ```python
        # if args.color_head and not is_valid_color_code(args.color_head):
        #     print(f"Error: Invalid format for --color-head: {args.color_head}")
        #     # exit or return error
        ```
*   **Expected Outcome:** The application is more robust against invalid user inputs, providing clear feedback.

## 4. Feature Enhancements

### 4.1. Customizable Color Themes (via CLI)
*   **Objective:** Allow users to define custom colors for the trail's head, bright part, and main part via CLI arguments.
*   **Current State:** Colors are hardcoded (WHITE, BRIGHT_GREEN, GREEN).
*   **Instructions:**
    1.  **Add `argparse` Arguments:** In `parse_arguments()`:
        ```python
        parser.add_argument("--color-head", type=str, default="97", help="ANSI code for the trail head (e.g., '97' for white).")
        parser.add_argument("--color-bright", type=str, default="92", help="ANSI code for the bright part of the trail (e.g., '92' for bright green).")
        parser.add_argument("--color-dim", type=str, default="32", help="ANSI code for the dim part of the trail (e.g., '32' for green).")
        # Consider adding --color-reset if needed, though standard reset is usually fine.
        ```
    2.  **Input Validation:** Validate these arguments. They should likely be string representations of numbers (ANSI codes). You might check if they are within a typical range or a predefined list of supported codes if you want to be restrictive. For flexibility, allowing any string and letting the terminal interpret it is also an option, but basic validation (e.g., not empty, looks like a number or a sequence like "38;2;r;g;b") is good.
    3.  **Construct ANSI Sequences:** In `initialize_animation_parameters()` or where colors are set up:
        *   Dynamically create the full ANSI escape sequences using the provided codes.
            Example: `HEAD_COLOR = f"[{args.color_head}m"`
            `BRIGHT_COLOR = f"[{args.color_bright}m"`
            `DIM_COLOR = f"[{args.color_dim}m"`
        *   Store these in variables or a dictionary.
    4.  **Use in Rendering:** In `render_frame_buffer()`, use these dynamically generated color variables instead of the hardcoded `WHITE`, `BRIGHT_GREEN`, `GREEN`.
    5.  **Update `AnsiColors` Enum (Optional):** If using the Enum from task 1.2, you might not store these dynamic user colors directly in the Enum (as Enums are typically static). Instead, the Enum could hold default/fallback values, and the actual colors used for rendering would be chosen based on CLI args, potentially overriding Enum defaults. Or, the Enum is simply used for `RESET`. A dictionary mapping e.g. `'head': HEAD_COLOR` might be more practical for user-defined themes.
*   **Expected Outcome:** Users can customize the rain's color scheme, for example, to create blue rain or red rain.

### 4.2. Adjustable Trail/Fade Dynamics (Bright Part Length)
*   **Objective:** Allow users to configure the length of the "bright" segment of the fading trail.
*   **Current State:** The bright part is fixed at 2 characters after the head.
*   **Instructions:**
    1.  **Add `argparse` Argument:** In `parse_arguments()`:
        ```python
        parser.add_argument(
            "--bright-length",
            type=int,
            default=2,
            help="Length of the 'bright' segment of the trail, following the head. Default: 2"
        )
        ```
    2.  **Input Validation:** In `parse_arguments()`:
        *   Ensure `args.bright_length` is a non-negative integer.
        *   It should also be less than `args.trail_length - 1` (since head is 1 char, dim part needs at least 1 char).
            ```python
            if args.bright_length < 0:
                print("Error: Bright length cannot be negative.")
                # Handle error
            if args.trail_length <= args.bright_length + 1: # +1 for the head
                print("Error: Trail length must be greater than bright length + 1.")
                # Handle error
            ```
    3.  **Use in Rendering Logic:** In `render_frame_buffer()` (or equivalent), modify the condition that determines the color:
        *   The current logic is:
            ```python
            # if distance_from_head == 0: # Head
            # elif distance_from_head <= 2: # Bright
            # else: # Dim
            ```
        *   Change to:
            ```python
            if distance_from_head == 0: # Head
                row_str += f"{HEAD_COLOR}{char}" # Or AnsiColors.WHITE.value etc.
            elif distance_from_head <= args.bright_length: # Bright part
                row_str += f"{BRIGHT_COLOR}{char}"
            else: # Dim part
                row_str += f"{DIM_COLOR}{char}"
            ```
*   **Expected Outcome:** Users can control the visual dynamics of the trail, making the bright segment shorter or longer.

### 4.3. "Glitch" Effects (via CLI)
*   **Objective:** Introduce an optional feature where characters in a trail might randomly change for a single frame.
*   **Current State:** No glitch effect.
*   **Instructions:**
    1.  **Add `argparse` Argument:** In `parse_arguments()`:
        ```python
        parser.add_argument(
            "--glitch-rate",
            type=float,
            default=0.0, # Default to 0 (no glitches)
            help="Probability (0.0 to 1.0) of a character glitching per frame. Default: 0.0"
        )
        ```
    2.  **Input Validation:** In `parse_arguments()`:
        *   Ensure `0.0 <= args.glitch_rate <= 1.0`.
    3.  **Implement Glitch Logic:** In `render_frame_buffer()`, within the loop where characters are chosen and colored:
        *   After a character `char = random.choice(chars)` is selected:
            ```python
            if random.random() < args.glitch_rate:
                # Glitch: pick another random character for this frame only
                glitched_char = random.choice(chars)
                # Proceed to color and append glitched_char instead of char
            # else:
                # Proceed to color and append original char
            ```
        *   Ensure the glitch only changes the character, not its color or position within the trail logic.
*   **Expected Outcome:** A subtle (or pronounced, depending on rate) visual effect where characters in the rain flicker or change randomly.

### 4.4. Pause and Resume Functionality
*   **Objective:** Allow users to pause and resume the animation.
*   **Current State:** Animation runs continuously until Ctrl+C.
*   **Instructions (Conceptual - requires platform-specific non-blocking input):**
    *   **Challenge:** Standard `input()` is blocking. Non-blocking keyboard input is platform-dependent (`msvcrt` on Windows, `select` with `sys.stdin` on Unix). A simpler, cross-platform approach might involve a slightly longer delay and quick check, or a dedicated thread for input, but this can add complexity.
    *   **Simplified Approach (Illustrative - may have slight input lag):**
        1.  **State Variable:** Introduce a global boolean variable, e.g., `is_paused = False`.
        2.  **Modify Main Loop (`run_animation_loop()`):**
            *   Before `time.sleep(args.speed)`, check for input. This is the tricky part.
            *   **For a very basic attempt (not truly non-blocking, more like "check between frames"):** This would not be very responsive.
            *   **Using a Thread (More Robust):**
                *   Start a separate thread that listens for a specific key (e.g., 'p').
                *   When the key is pressed, this thread toggles the `is_paused` variable.
                *   The main animation loop checks `is_paused`:
                    ```python
                    # In run_animation_loop()
                    while True:
                        if is_paused:
                            time.sleep(0.1) # Sleep a bit while paused to prevent busy-waiting
                            continue # Skip update and render

                        # ... (existing logic for updating column states) ...
                        # ... (existing logic for rendering frame buffer) ...
                        # ... (existing logic for printing frame) ...
                        # ... time.sleep(args.speed) ...
                    ```
        3.  **Input Handling (Conceptual for threaded approach):**
            ```python
            # import threading
            # is_paused = False
            #
            # def input_thread_func():
            #     global is_paused
            #     while True:
            #         # This is still blocking for the thread, but not the main animation
            #         key = input() # Or a more sophisticated single key reader
            #         if key.lower() == 'p':
            #             is_paused = not is_paused
            #
            # # In main execution, before starting run_animation_loop:
            # input_listener = threading.Thread(target=input_thread_func, daemon=True)
            # input_listener.start()
            ```
        4.  **Consider `curses` (More Complex but Capable):** For true non-blocking input and better screen control, the `curses` library is the standard Python solution, but it's a larger refactor of the rendering logic.
*   **Instructions (If `curses` or similar is too complex, recommend a simpler placeholder or note the challenge):**
    *   Acknowledge that true non-blocking input without `curses` is tricky.
    *   Suggest that if a simple threaded approach is too much, this feature might be deferred or require a more significant library change (like adopting `curses`).
    *   For this document, detail the threaded approach as a viable option, noting its daemon thread nature for clean exit.
*   **Expected Outcome:** User can press a key (e.g., 'p') to toggle pausing and resuming the animation, allowing them to inspect a frame or temporarily stop the visual output.

## 5. Future Considerations for Configuration

### 5.1. Configuration File Support
*   **Objective:** Plan for supporting a configuration file (e.g., JSON, YAML, INI) for managing numerous settings.
*   **Current State:** Configuration is solely via CLI arguments.
*   **Context & Benefits:**
    *   As features like detailed color schemes, complex character sets, and multiple effect parameters are added, the CLI argument list can become very long and unwieldy.
    *   Configuration files allow users to save, share, and manage multiple complex settings profiles easily.
    *   Keeps the command line cleaner for simple invocations.
*   **Implementation Ideas (Not for immediate implementation, but for future planning):**
    1.  **Choose Format:** Decide on a format (JSON, YAML, or INI are common).
    2.  **Loading Logic:**
        *   Application could look for a default config file (e.g., `~/.matrix_config.json` or `matrix_config.json` in the script's directory).
        *   Allow specifying a config file path via a CLI argument (e.g., `python main.py --config my_settings.json`).
    3.  **Priority:**
        *   Establish a clear order of precedence: e.g., CLI arguments override config file settings, which override hardcoded defaults.
    4.  **Parsing:** Use appropriate Python libraries to parse the chosen format (e.g., `json` module for JSON, `PyYAML` for YAML, `configparser` for INI).
    5.  **Structure:** Design a clear structure for the config file. Example (JSON):
        ```json
        {
          "animation": {
            "speed": 0.08,
            "density": 0.1,
            "trail_length": 12,
            "bright_length": 3
          },
          "display": {
            "character_set": "01",
            "colors": {
              "head": "96", // Bright Cyan
              "bright": "36", // Cyan
              "dim": "34"     // Blue
            }
          },
          "effects": {
            "glitch_rate": 0.001
          }
        }
        ```
*   **Expected Outcome (for this task):** A section in `detailed_tasks.md` that explains why config files are a good future step and outlines how they might be implemented, guiding future development if the script becomes significantly more complex.
