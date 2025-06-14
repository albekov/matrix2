import unittest
import random # Added for random.choice mocking
from unittest.mock import MagicMock, patch # Added patch

from animation_core import (
    ColumnState,
    initialize_animation_parameters,
    update_column_states, # Added update_column_states
    render_frame_buffer,  # Added render_frame_buffer
)
from config import CHARS_LATIN, DEFAULT_CHAR_SETS, AnsiColors # Added AnsiColors


class TestAnimationCore(unittest.TestCase):
    def test_column_state_initialization(self):
        """Test that ColumnState dataclass is initialized correctly."""
        cs = ColumnState(head_y=0, current_char_set=list(CHARS_LATIN), trail=[])
        self.assertEqual(cs.head_y, 0)
        self.assertEqual(cs.current_char_set, list(CHARS_LATIN))
        self.assertEqual(cs.trail, [])

    def test_initialize_animation_parameters_creates_column_states(self):
        """Test that initialize_animation_parameters creates ColumnState objects."""
        args = MagicMock()
        args.char_set = None  # Use default character sets
        args.theme = "classic"
        args.base_colors = None

        width = 10
        height = 5

        columns, _, _ = initialize_animation_parameters(args, width, height)

        self.assertEqual(len(columns), width)
        for col in columns:
            self.assertIsInstance(col, ColumnState)
            self.assertEqual(col.head_y, 0)
            self.assertIn(col.current_char_set, [list(cs) for cs in DEFAULT_CHAR_SETS if cs] or [list(CHARS_LATIN)])
            self.assertEqual(col.trail, [])

    def test_update_column_states_updates_head_y(self):
        """Test that update_column_states correctly updates head_y."""
        cols = [
            ColumnState(0, ["a"], []),
            ColumnState(1, ["b"], []),
            ColumnState(5, ["c"], []),
        ]
        width = len(cols)
        height = 10
        density = 0.0  # No new drops for simplicity
        trail_length = 3
        available_char_sets = [["a"], ["b"], ["c"]]

        updated_cols = update_column_states(
            cols, width, height, density, trail_length, available_char_sets
        )

        self.assertEqual(updated_cols[0].head_y, 0)  # Remains 0 due to density
        self.assertEqual(updated_cols[1].head_y, 2)  # Incremented
        self.assertEqual(updated_cols[2].head_y, 6)  # Incremented

    def test_update_column_states_resets_head_y_past_height(self):
        """Test that update_column_states resets head_y when trail is past height."""
        cols = [ColumnState(15, ["a"], [])]  # head_y is far down
        width = len(cols)
        height = 10
        density = 0.0
        trail_length = 3  # head_y - trail_length = 12, which is > height (10)
        available_char_sets = [["a"]]

        updated_cols = update_column_states(
            cols, width, height, density, trail_length, available_char_sets
        )
        self.assertEqual(updated_cols[0].head_y, 0) # Should reset

    def test_update_column_states_starts_new_drop(self):
        """Test that update_column_states can start a new drop."""
        cols = [ColumnState(0, ["a"], [])]
        width = len(cols)
        height = 10
        density = 1.0  # Always start a new drop
        trail_length = 3
        available_char_sets = [["x"]]

        # Mock random.random() to control new drop generation if necessary,
        # but density=1.0 should guarantee it.
        updated_cols = update_column_states(
            cols, width, height, density, trail_length, available_char_sets
        )
        self.assertEqual(updated_cols[0].head_y, 1)
        self.assertEqual(updated_cols[0].current_char_set, ["x"])

    def test_render_frame_buffer_accesses_column_state_attributes(self):
        """Test that render_frame_buffer correctly accesses ColumnState attributes."""
        args = MagicMock()
        args.trail_length = 3
        args.glitch_rate = 0.0
        args.theme = "classic"  # For predictable color choices
        args.color_intensity = "normal"
        args.bright_length = 1


        # active_colors for classic theme
        active_colors = {
            "WHITE": AnsiColors.WHITE.value,
            "BRIGHT_GREEN": AnsiColors.BRIGHT_GREEN.value,
            "GREEN": AnsiColors.GREEN.value,
            "RESET": AnsiColors.RESET.value,
        }

        # Setup a single column with a known state
        char_set = ["T"]
        # Column where the head is at y=1, so 'T' should be rendered.
        cols = [ColumnState(head_y=1, current_char_set=char_set, trail=[])]
        width = 1
        height = 1
        available_char_sets = [char_set]

        # Mock random.choice to return a predictable character
        with patch("random.choice", return_value="T") as mock_random_choice:
            frame_buffer = render_frame_buffer(
                cols, width, height, active_colors, args, available_char_sets, args.glitch_rate
            )
            # Expected: White 'T' because it's the head of the trail (distance_from_head == 0)
            # and color_intensity 'normal' uses WHITE for the head.
            expected_char_output = f"{AnsiColors.WHITE.value}T"
            self.assertEqual(frame_buffer[0], expected_char_output)
            # Verify random.choice was called (it's used to pick a char from current_char_set)
            mock_random_choice.assert_called_with(char_set)

        # Test a column where the trail should be rendered
        # Head at y=2, trail_length=3. Character at y=1 is part of bright segment.
        cols_trail = [ColumnState(head_y=2, current_char_set=char_set, trail=[])]
        with patch("random.choice", return_value="T") as mock_random_choice:
            frame_buffer_trail = render_frame_buffer(
                cols_trail, width, height, active_colors, args, available_char_sets, args.glitch_rate
            )
            # Expected: Bright Green 'T' (normal intensity, bright segment)
            expected_char_output_trail = f"{AnsiColors.BRIGHT_GREEN.value}T"
            self.assertEqual(frame_buffer_trail[0], expected_char_output_trail)


if __name__ == "__main__":
    unittest.main()
