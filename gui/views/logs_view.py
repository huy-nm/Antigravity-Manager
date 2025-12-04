import flet as ft
import sys
from theme import get_palette

RADIUS_CARD = 12
PADDING_PAGE = 20

class LogsView(ft.Container):
    def __init__(self, page: ft.Page, app_state):
        super().__init__()
        self.main_page = page
        self.app_state = app_state
        self.expand = True
        self.padding = PADDING_PAGE
        
        # Initialize with current palette
        self.palette = get_palette(page)
        self.bgcolor = self.palette.bg_page
        
        self.log_view = ft.ListView(
            expand=True,
            spacing=5,
            padding=10,
            auto_scroll=True,
        )
        
        # Redirect stdout to capture logs
        self.original_stdout = sys.stdout
        sys.stdout = self.LogRedirector(self.log_view)
        
        self.build_ui()

    def did_mount(self):
        pass

    def will_unmount(self):
        # Keep stdout redirected so we capture logs even when not on this view
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
                ft.Row(
                    [
                        ft.Text(self.app_state.get_text("logs"), size=28, weight=ft.FontWeight.BOLD, color=self.palette.text_main),
                        ft.Dropdown(
                            width=200,
                            options=[
                                ft.dropdown.Option("all", self.app_state.get_text("all_apps")),
                                ft.dropdown.Option("antigravity", self.app_state.get_text("antigravity")),
                                ft.dropdown.Option("claude", self.app_state.get_text("claude")),
                                ft.dropdown.Option("codex", self.app_state.get_text("codex")),
                            ],
                            value="all",
                            text_size=13,
                            border_color=self.palette.sidebar_border,
                            focused_border_color=self.palette.primary,
                            content_padding=ft.padding.symmetric(horizontal=10, vertical=0),
                            filled=True,
                            bgcolor=self.palette.bg_card,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Container(height=20),
                
                # Logs Section
                ft.Container(
                    content=self.log_view,
                    bgcolor="#1E1E1E", # Console always dark
                    border_radius=RADIUS_CARD,
                    expand=True,  # This will take up all remaining vertical space
                    padding=15,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=10,
                        color=self.palette.shadow,
                        offset=ft.Offset(0, 4),
                    )
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START
        )

    class LogRedirector:
        def __init__(self, log_view):
            self.log_view = log_view
            self.terminal = sys.stdout

        def write(self, message):
            if self.terminal:
                try:
                    self.terminal.write(message)
                except:
                    pass
            if not message.strip():
                return
                
            # Simple ANSI color parsing
            text_color = "#FFFFFF" # Default log color
            clean_message = message.strip()
            
            if "\033[32m" in message: # Green (INFO)
                text_color = "#34C759"
                clean_message = clean_message.replace("\033[32m", "").replace("\033[0m", "")
            elif "\033[33m" in message: # Yellow (WARN)
                text_color = "#FFCC00"
                clean_message = clean_message.replace("\033[33m", "").replace("\033[0m", "")
            elif "\033[31m" in message: # Red (ERR)
                text_color = "#FF3B30"
                clean_message = clean_message.replace("\033[31m", "").replace("\033[0m", "")
            elif "\033[90m" in message: # Grey (DEBUG)
                text_color = "#8E8E93"
                clean_message = clean_message.replace("\033[90m", "").replace("\033[0m", "")
            
            # Remove any remaining ANSI codes if simple parsing missed them
            if "\033[" in clean_message:
                import re
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                clean_message = ansi_escape.sub('', clean_message)

            self.log_view.controls.append(
                ft.Text(
                    clean_message, 
                    font_family="Monaco, Menlo, Courier New, monospace", 
                    size=12,
                    color=text_color,
                    selectable=True
                )
            )
            
            # Only try to update if the control is attached to a page
            if self.log_view.page:
                try:
                    self.log_view.update()
                except:
                    pass

        def flush(self):
            self.terminal.flush()
