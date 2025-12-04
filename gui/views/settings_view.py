import flet as ft
import sys
import os
import platform
import subprocess
from pathlib import Path
from theme import get_palette
from icons import AppIcons

RADIUS_CARD = 12
PADDING_PAGE = 20

class SettingsView(ft.Container):
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

    def did_mount(self):
        pass

    def will_unmount(self):
        pass

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
        # Just wrapper
        self.rebuild_ui()

    def rebuild_ui(self):
        self.content = ft.Column(
            [
                ft.Text(self.app_state.get_text("settings"), size=28, weight=ft.FontWeight.BOLD, color=self.palette.text_main),
                ft.Container(height=20),
                
                # App Specific Settings Sections
                self._build_app_settings(self.app_state.get_text("antigravity"), "antigravity"),
                ft.Container(height=20),
                self._build_app_settings(self.app_state.get_text("claude"), "claude"),
                ft.Container(height=20),
                self._build_app_settings(self.app_state.get_text("codex"), "codex"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO
        )

    def _build_app_settings(self, title, app_id):
        # Only show specific settings for Antigravity for now
        if app_id == "antigravity":
            content = ft.Column(
                [
                    ft.Text(self.app_state.get_text("data_management"), size=13, weight=ft.FontWeight.BOLD, color=self.palette.text_grey),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Row(
                                            [
                                                ft.Container(
                                                    content=ft.Icon(AppIcons.folder, size=24, color=self.palette.primary),
                                                    bgcolor=self.palette.bg_light_blue,
                                                    padding=8,
                                                    border_radius=8
                                                ),
                                                ft.Column(
                                                    [
                                                        ft.Text(self.app_state.get_text("local_data_dir"), size=15, weight=ft.FontWeight.W_600, color=self.palette.text_main),
                                                        ft.Text(self.app_state.get_text("view_files"), size=12, color=self.palette.text_grey),
                                                    ],
                                                    spacing=2,
                                                    alignment=ft.MainAxisAlignment.CENTER
                                                )
                                            ],
                                            spacing=15
                                        ),
                                        ft.Container(
                                            content=ft.Text(self.app_state.get_text("open_folder"), size=13, color=self.palette.primary, weight=ft.FontWeight.BOLD),
                                            padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                            border_radius=8,
                                            bgcolor=self.palette.bg_light_blue,
                                            on_click=self.open_data_folder,
                                            alignment=ft.alignment.center
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                            ],
                            spacing=0,
                        ),
                        padding=20,
                        bgcolor=self.palette.bg_card,
                        border_radius=RADIUS_CARD,
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=10,
                            color=self.palette.shadow,
                            offset=ft.Offset(0, 4),
                        ),
                    ),
                ],
                spacing=0
            )
        else:
            content = ft.Container(
                content=ft.Text(f"{title} settings coming soon", color=self.palette.text_grey),
                padding=20,
                bgcolor=self.palette.bg_card,
                border_radius=RADIUS_CARD,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=10,
                    color=self.palette.shadow,
                    offset=ft.Offset(0, 4),
                ),
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row([
                        ft.Icon(
                            AppIcons.app_antigravity if app_id == "antigravity" else (AppIcons.app_claude if app_id == "claude" else AppIcons.app_codex),
                            size=24, 
                            color=self.palette.text_main
                        ),
                        ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=self.palette.text_main)
                    ], spacing=10),
                    ft.Container(height=10),
                    content
                ],
                spacing=0
            ),
            width=600
        )

    def on_language_change(self, e):
        # Moved to Sidebar
        pass

    def open_data_folder(self, e):
        path_to_open = os.path.expanduser("~/.antigravity-agent")
        if not os.path.exists(path_to_open):
             path_to_open = os.getcwd()
        
        path_to_open = os.path.normpath(path_to_open)
             
        if platform.system() == "Darwin":
            subprocess.run(["open", path_to_open])
        elif platform.system() == "Windows":
            try:
                os.startfile(path_to_open)
            except Exception as e:
                print(f"Failed to open folder: {e}")
        else:
            subprocess.run(["xdg-open", path_to_open])
