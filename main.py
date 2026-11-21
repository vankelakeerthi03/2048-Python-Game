
import random

from kivy.app import App
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


SIZE = 4

COLORS = {
    0: "#cdc1b4",
    2: "#eee4da",
    4: "#ede0c8",
    8: "#f2b179",
    16: "#f59563",
    32: "#f67c5f",
    64: "#f65e3b",
    128: "#edcf72",
    256: "#edcc61",
    512: "#edc850",
    1024: "#edc53f",
    2048: "#edc22e",
}


class Tile(Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.border = (0, 0, 0, 0)
        self.bold = True
        self.size_hint = (1, 1)

        self.update_tile(0)

    def update_tile(self, value, merged=False):

        Animation.cancel_all(self)

        self.text = str(value) if value else ""

        color = COLORS.get(value, "#3c3a32")
        self.background_color = get_color_from_hex(color)

        self.color = get_color_from_hex(
            "#776e65" if value in [0, 2, 4] else "#ffffff"
        )

        if value <= 64:
            self.font_size = dp(34)
        elif value <= 512:
            self.font_size = dp(29)
        elif value <= 2048:
            self.font_size = dp(24)
        else:
            self.font_size = dp(20)

        if merged and value:
            original_size = self.font_size
            self.font_size = original_size * 0.75

            Animation(
                font_size=original_size,
                duration=0.18,
                transition="out_back"
            ).start(self)


class Game2048App(App):

    def build(self):

        self.board = [[0] * SIZE for _ in range(SIZE)]
        self.score = 0
        self.best_score = 0
        self.game_over = False
        self.touch_start = None

        Window.clearcolor = get_color_from_hex("#faf8ef")

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(15), dp(18), dp(12)],
            spacing=dp(10)
        )

        # HEADER

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(85),
            spacing=dp(8)
        )

        self.title_label = Label(
            text="2048",
            font_size=dp(62),
            bold=True,
            color=get_color_from_hex("#776e65"),
            halign="left",
            valign="middle"
        )

        header.add_widget(self.title_label)

        self.score_label = self.create_score_card("SCORE", "0")
        self.best_label = self.create_score_card("BEST", "0")

        header.add_widget(self.score_label)
        header.add_widget(self.best_label)

        self.root_layout.add_widget(header)

        # DESCRIPTION

        description = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            spacing=dp(5)
        )

        self.description_label = Label(
            text="Join the numbers and reach 2048!",
            font_size=dp(14),
            color=get_color_from_hex("#776e65"),
            halign="left",
            valign="middle"
        )

        description.add_widget(self.description_label)

        self.root_layout.add_widget(description)

        # NEW GAME BUTTON

        self.restart_button = Button(
            text="NEW GAME",
            size_hint=(None, None),
            size=(dp(115), dp(42)),
            font_size=dp(14),
            bold=True,
            color=get_color_from_hex("#ffffff"),
            background_normal="",
            background_down="",
            background_color=get_color_from_hex("#8f7a66")
        )

        self.restart_button.bind(
            on_release=lambda instance: self.restart()
        )

        self.root_layout.add_widget(self.restart_button)

        # GAME BOARD

        self.board_container = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint=(1, 1)
        )

        self.grid = GridLayout(
            cols=SIZE,
            rows=SIZE,
            spacing=dp(10),
            padding=dp(10),
            size_hint=(None, None)
        )

        self.cells = []

        for r in range(SIZE):

            row = []

            for c in range(SIZE):

                cell = Tile()
                self.grid.add_widget(cell)
                row.append(cell)

            self.cells.append(row)

        self.board_container.add_widget(self.grid)
        self.root_layout.add_widget(self.board_container)

        # INSTRUCTIONS

        self.message = Label(
            text="Use arrow keys or swipe to play",
            font_size=dp(14),
            color=get_color_from_hex("#776e65"),
            size_hint_y=None,
            height=dp(35)
        )

        self.root_layout.add_widget(self.message)

        self.how_to_play = Label(
            text="HOW TO PLAY: Join matching numbers to make bigger tiles.",
            font_size=dp(11),
            color=get_color_from_hex("#776e65"),
            size_hint_y=None,
            height=dp(28)
        )

        self.root_layout.add_widget(self.how_to_play)

        self.root_layout.bind(size=self.resize_board)
        Window.bind(size=self.resize_board)
        Window.bind(on_key_down=self.on_key_down)

        self.grid.bind(
            on_touch_down=self.on_touch_down,
            on_touch_up=self.on_touch_up
        )

        self.resize_board()

        self.add_tile()
        self.add_tile()
        self.update_display()

        return self.root_layout

    # SCORE CARD

    def create_score_card(self, heading, value):

        card = BoxLayout(
            orientation="vertical",
            size_hint=(None, 1),
            width=dp(75),
            padding=dp(5),
            spacing=dp(2)
        )

        card.background_color = get_color_from_hex("#bbada0")

        label = Label(
            text=heading,
            font_size=dp(11),
            bold=True,
            color=get_color_from_hex("#eee4da")
        )

        number = Label(
            text=value,
            font_size=dp(19),
            bold=True,
            color=get_color_from_hex("#ffffff")
        )

        card.add_widget(label)
        card.add_widget(number)

        card.number_label = number

        return card

    # RESPONSIVE BOARD WIDTH

    def resize_board(self, *args):

        if not hasattr(self, "grid"):
            return

        available_width = Window.width - dp(45)
        available_height = Window.height - dp(300)

        board_size = min(
            available_width,
            available_height,
            dp(430)
        )

        board_size = max(dp(220), board_size)

        self.grid.size = (board_size, board_size)

    # ADD RANDOM TILE

    def add_tile(self):

        empty = [
            (r, c)
            for r in range(SIZE)
            for c in range(SIZE)
            if self.board[r][c] == 0
        ]

        if empty:

            r, c = random.choice(empty)

            self.board[r][c] = random.choices(
                [2, 4],
                weights=[90, 10]
            )[0]

    # SLIDE AND MERGE

    def slide(self, row):

        numbers = [n for n in row if n != 0]

        result = []
        merged_indices = []

        i = 0

        while i < len(numbers):

            if (
                i + 1 < len(numbers)
                and numbers[i] == numbers[i + 1]
            ):

                value = numbers[i] * 2

                result.append(value)
                merged_indices.append(len(result) - 1)

                self.score += value

                i += 2

            else:

                result.append(numbers[i])
                i += 1

        return (
            result + [0] * (SIZE - len(result)),
            merged_indices
        )

    # MOVE TILES

    def move(self, direction):

        if self.game_over:
            return

        old_board = [row[:] for row in self.board]

        merged_positions = []

        if direction in ("left", "right"):

            new_board = []

            for r, row in enumerate(self.board):

                if direction == "right":

                    processed, merged = self.slide(row[::-1])
                    processed.reverse()

                    merged = [
                        SIZE - 1 - index
                        for index in merged
                    ]

                else:

                    processed, merged = self.slide(row)

                new_board.append(processed)

                for c in merged:
                    merged_positions.append((r, c))

            self.board = new_board

        elif direction in ("up", "down"):

            transposed = [
                list(row)
                for row in zip(*self.board)
            ]

            new_transposed = []

            for c, row in enumerate(transposed):

                if direction == "down":

                    processed, merged = self.slide(row[::-1])
                    processed.reverse()

                    merged = [
                        SIZE - 1 - index
                        for index in merged
                    ]

                else:

                    processed, merged = self.slide(row)

                new_transposed.append(processed)

                for r in merged:
                    merged_positions.append((r, c))

            self.board = [
                list(row)
                for row in zip(*new_transposed)
            ]

        if self.board != old_board:

            self.add_tile()
            self.update_display(merged_positions)

        self.check_game_status()

    # UPDATE DISPLAY

    def update_display(self, merged_positions=None):

        merged_positions = merged_positions or []

        for r in range(SIZE):

            for c in range(SIZE):

                value = self.board[r][c]

                self.cells[r][c].update_tile(
                    value,
                    merged=(r, c) in merged_positions
                )

        self.score_label.number_label.text = str(self.score)

        if self.score > self.best_score:
            self.best_score = self.score

        self.best_label.number_label.text = str(self.best_score)

    # CHECK GAME OVER

    def check_game_status(self):

        for r in range(SIZE):

            for c in range(SIZE):

                value = self.board[r][c]

                if value == 0:
                    return

                if (
                    c + 1 < SIZE
                    and value == self.board[r][c + 1]
                ):
                    return

                if (
                    r + 1 < SIZE
                    and value == self.board[r + 1][c]
                ):
                    return

        self.game_over = True
        self.message.text = "GAME OVER! Click NEW GAME"

    # RESTART

    def restart(self):

        self.board = [[0] * SIZE for _ in range(SIZE)]

        self.score = 0
        self.game_over = False

        self.message.text = "Use arrow keys or swipe to play"

        self.add_tile()
        self.add_tile()

        self.update_display()

    # KEYBOARD CONTROLS

    def on_key_down(
        self,
        window,
        key,
        scancode,
        codepoint,
        modifiers
    ):

        keys = {
            276: "left",
            275: "right",
            273: "up",
            274: "down"
        }

        if key in keys:
            self.move(keys[key])
            return True

        return False

    # TOUCH START

    def on_touch_down(self, widget, touch):

        if not self.grid.collide_point(*touch.pos):
            return False

        self.touch_start = touch.pos

        return True

    # MOBILE SWIPE

    def on_touch_up(self, widget, touch):

        if self.touch_start is None:
            return False

        start_x, start_y = self.touch_start

        diff_x = touch.x - start_x
        diff_y = touch.y - start_y

        self.touch_start = None

        if max(abs(diff_x), abs(diff_y)) < dp(25):
            return True

        if abs(diff_x) > abs(diff_y):

            direction = "right" if diff_x > 0 else "left"

        else:

            direction = "up" if diff_y > 0 else "down"

        self.move(direction)

        return True


if __name__ == "__main__":

    Game2048App().run()
