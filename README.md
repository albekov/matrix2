# Matrix Digital Rain Animation

This Python script creates a Matrix-like digital rain animation in your console. It's highly customizable, allowing you to tweak various aspects of the animation for a personalized visual experience.

## Features

*   **Customizable Animation Speed**: Control how fast the digital rain falls using the `--speed` argument.
*   **Customizable Column Density**: Adjust the probability of new rain drops appearing in columns with the `--density` argument.
*   **Customizable Trail Length**: Define the length of the fading trails for each drop using the `--trail-length` argument.
*   **Color Intensity Control**: Choose the brightness of the rain with the `--color-intensity` argument. Options include `dim`, `normal` (default), and `bright` profiles.
*   **Expanded Color Palette**: The animation now cycles through a wider variety of colors beyond the classic green, including blues, cyans, magentas, and yellows, in both normal and bright versions for each trail. The head of the trail remains the brightest, creating a dynamic effect.
*   **Character Set Cycling**: Each rain drop can now use a different set of characters, randomly chosen from Latin characters (letters, numbers, common symbols), Japanese Katakana, or a collection of miscellaneous symbols and arrows. This adds more visual diversity to the animation.
*   **Dynamic Terminal Resizing**: The animation attempts to adapt to your terminal's dimensions.
*   **Cursor Hiding**: The terminal cursor is hidden during the animation for a cleaner look and restored on exit.

## Usage

To run the script, navigate to its directory and execute:

```bash
python main.py [OPTIONS]
```

### Options

*   `--speed FLOAT`: Animation speed (delay between frames in seconds).
    *   Default: `0.1`
    *   Must be a positive number.
*   `--density FLOAT`: Column density (probability of a column starting a new drop).
    *   Default: `0.075`
    *   Must be between 0 (exclusive) and 1 (inclusive).
*   `--trail-length INT`: The length of the fading trail.
    *   Default: `10`
    *   Must be greater than 2.
*   `--color-intensity {dim,normal,bright}`: Color intensity for the trail.
    *   Default: `normal`
    *   `dim`: Uses dimmer colors for the trail (e.g., bright base color for head, base color for trail).
    *   `normal`: Standard intensity (e.g., white head, bright base color segment, base color trail).
    *   `bright`: Uses brighter colors for the trail (e.g., white head, white segment, bright base color trail).

## Example

To run the animation with a slightly faster speed, higher density, longer trails, and bright intensity:

```bash
python main.py --speed 0.08 --density 0.1 --trail-length 15 --color-intensity bright
```

Press `Ctrl+C` to stop the animation.
