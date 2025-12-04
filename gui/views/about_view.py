import flet as ft
from icons import AppIcons
from theme import get_palette

RADIUS_CARD = 12
PADDING_PAGE = 20


class AboutView(ft.Container):
    def __init__(self, page: ft.Page, app_state):
        super().__init__()
        self.main_page = page
        self.app_state = app_state
        self.expand = True
        self.padding = PADDING_PAGE

        # Initialize with current palette
        self.palette = get_palette(page)
        self.bgcolor = self.palette.bg_page

        self.build_ui()

    def update_theme(self):
        self.palette = get_palette(self.main_page)
        self.bgcolor = self.palette.bg_page
        self.rebuild_ui()
        if self.page:
            self.update()

    def update_locale(self):
        self.rebuild_ui()
        if self.page:
            self.update()

    def build_ui(self):
        self.rebuild_ui()

    def rebuild_ui(self):
        self.content = ft.Column(
            [
                ft.Text(
                    self.app_state.get_text("about"),
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=self.palette.text_main,
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.INFO_OUTLINE,
                                        size=40,
                                        color=self.palette.primary,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                self.app_state.get_text("app_title"),
                                                size=20,
                                                weight=ft.FontWeight.BOLD,
                                                color=self.palette.text_main,
                                            ),
                                            ft.Text(
                                                "Version 1.0.0",
                                                size=14,
                                                color=self.palette.text_grey,
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                spacing=15,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Container(height=30),
                            # Info Rows
                            self._build_info_row("License", "MIT License"),
                            ft.Divider(color=self.palette.sidebar_border),
                            ft.Row(
                                [
                                    ft.Text(
                                        "Forked from",
                                        size=14,
                                        color=self.palette.text_grey,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.TextButton(
                                        "lbjlaq/Antigravity-Manager",
                                        url="https://github.com/lbjlaq/Antigravity-Manager",
                                        style=ft.ButtonStyle(
                                            color={"": self.palette.primary}, padding=0
                                        ),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Container(height=20),
                        ],
                        spacing=10,
                    ),
                    padding=30,
                    bgcolor=self.palette.bg_card,
                    border_radius=RADIUS_CARD,
                    width=600,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=10,
                        color=self.palette.shadow,
                        offset=ft.Offset(0, 4),
                    ),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
        )

    def _build_info_row(self, label, value):
        return ft.Row(
            [
                ft.Text(
                    label,
                    size=14,
                    color=self.palette.text_grey,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Text(
                    value,
                    size=14,
                    color=self.palette.text_main,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
