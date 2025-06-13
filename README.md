# Matrix Digital Rain Animation

This Python script creates a Matrix-like digital rain animation in your console. It's highly customizable, allowing you to tweak various aspects of the animation for a personalized visual experience.

## Features

*   **Customizable Animation Speed**: Control how fast the digital rain falls using the `--speed` argument.
*   **Customizable Column Density**: Adjust the probability of new rain drops appearing in columns with the `--density` argument.
*   **Customizable Trail Length**: Define the length of the fading trails for each drop using the `--trail-length` argument.
*   **Theming**: Choose between a `classic` green-on-black Matrix theme or a `colorful` theme that uses a wider palette.
*   **Color Intensity Control**: Fine-tune the brightness of the trails. Options include `dim`, `normal` (default), and `bright`. This interacts with the chosen theme.
*   **Character Set Cycling**: Each rain drop can use a different set of characters, randomly chosen from Latin characters (letters, numbers, common symbols), Japanese Katakana, or miscellaneous symbols/arrows, adding visual diversity.
*   **Robust Character Rendering**: Utilizes the `wcwidth` library to correctly handle characters of varying display widths (e.g., East Asian characters, symbols). This prevents visual misalignments and artifacts (like the 'wave' effect) ensuring smoother animation across diverse character sets and terminals.
*   **Expanded Color Palette (for 'colorful' theme)**: The `colorful` theme utilizes a variety of colors like blues, cyans, magentas, and yellows, in addition to greens.
*   **Dynamic Terminal Resizing**: The animation attempts to adapt to your terminal's dimensions.
*   **Cursor Hiding**: The terminal cursor is hidden during animation for a cleaner look and restored on exit.
*   **Improved Animation Consistency**: More consistent animation pacing, especially at very high speed settings.

## Requirements

*   Python 3.x
*   The `wcwidth` library. You can install it using `uv` (or `pip`):
    ```bash
    uv add wcwidth
    ```
    (If you don't have `uv`, you can use: `pip install wcwidth`)

## Usage

To run the script, navigate to its directory and execute:

```bash
python main.py [OPTIONS]
```

### Options

*   `--speed FLOAT`: Animation speed (delay between frames in seconds).
    *   Default: `0.1`
    *   Must be a positive number. A minimum effective sleep time is enforced for stability at very high rates.
*   `--density FLOAT`: Column density (probability of a column starting a new drop).
    *   Default: `0.075`
    *   Must be between 0 (exclusive) and 1 (inclusive).
*   `--trail-length INT`: The length of the fading trail.
    *   Default: `10`
    *   Must be greater than 2.
*   `--theme {classic,colorful}`: Color theme for the animation.
    *   Default: `classic`
    *   `classic`: Uses the traditional green and white Matrix color scheme.
    *   `colorful`: Uses an expanded palette with various colors (greens, blues, cyans, etc.) randomly chosen for different trails.
*   `--color-intensity {dim,normal,bright}`: Adjusts the brightness levels of the trail segments.
    *   Default: `normal`
    *   When `theme` is `classic`:
        *   `dim`: Trail head is bright green, subsequent segments are green.
        *   `normal`: Trail head is white, first segment bright green, rest green.
        *   `bright`: Trail head is white, first segment white, rest bright green.
    *   When `theme` is `colorful`:
        *   `dim`: Trail head is a bright version of a random base color, subsequent segments are the base color.
        *   `normal`: Trail head is white, first segment is a bright version of a random base color, rest is the base color.
        *   `bright`: Trail head is white, first segment is white, rest is a bright version of a random base color.

## Examples

1.  Run with default settings (classic Matrix look):
    ```bash
    python main.py
    ```

2.  Run with a faster speed, higher density, longer trails, and bright intensity using the classic theme:
    ```bash
    python main.py --speed 0.08 --density 0.1 --trail-length 15 --color-intensity bright --theme classic
    ```

3.  Run with the colorful theme and normal intensity:
    ```bash
    python main.py --theme colorful --color-intensity normal
    ```

4.  Run the colorful theme with high density and dim intensity:
    ```bash
    python main.py --density 0.15 --theme colorful --color-intensity dim
    ```

Press `Ctrl+C` to stop the animation.
