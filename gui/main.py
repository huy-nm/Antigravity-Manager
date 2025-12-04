import flet as ft
import sys
from pathlib import Path

# Import from local modules
from views.home_view import HomeView
from views.settings_view import SettingsView
from views.logs_view import LogsView
from views.about_view import AboutView
from theme import get_palette
from icons import AppIcons
from locales import Locales
from utils import load_settings, save_settings

class AppState:
    def __init__(self, page: ft.Page, on_refresh=None):
        self.page = page
        self.on_refresh = on_refresh
        self.settings = load_settings()
        self.lang = self.settings.get("language", "en")
        self.selected_app = "antigravity"
        
    def get_text(self, key):
        return Locales.get_text(self.lang, key)
        
    def set_language(self, lang_code):
        if self.lang != lang_code:
            self.lang = lang_code
            self.settings["language"] = lang_code
            save_settings(self.settings)
            if self.on_refresh:
                self.on_refresh()

    def set_app(self, app_id):
        if self.selected_app != app_id:
            self.selected_app = app_id
            if self.on_refresh:
                self.on_refresh()

class SidebarItem(ft.Container):
    def __init__(self, icon, label, selected, on_click, palette):
        super().__init__()
        self.on_click = on_click
        self.border_radius = 6
        self.padding = ft.padding.symmetric(horizontal=10, vertical=8)
        self.bgcolor = ft.Colors.with_opacity(0.1, palette.text_main) if selected else ft.Colors.TRANSPARENT
        self.animate = ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        
        self.content = ft.Row(
            [
                ft.Icon(
                    icon, 
                    size=18, 
                    color=palette.primary if selected else palette.text_main
                ),
                ft.Text(
                    label, 
                    size=13, 
                    weight=ft.FontWeight.W_500 if selected else ft.FontWeight.NORMAL,
                    color=palette.text_main if selected else palette.text_grey
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

class Sidebar(ft.Container):
    def __init__(self, page, app_state, on_nav_change):
        super().__init__()
        self.page = page
        self.app_state = app_state
        self.on_nav_change = on_nav_change
        self.selected_index = 0
        self.width = 200
        self.padding = ft.padding.only(top=20, left=10, right=10)
        
        # Initialize theme without calling update()
        self.palette = get_palette(self.page)
        self.bgcolor = self.palette.sidebar_bg
        self.border = ft.border.only(right=ft.BorderSide(1, self.palette.sidebar_border))
        self.build_menu()

    def update_theme(self):
        self.palette = get_palette(self.page)
        self.bgcolor = self.palette.sidebar_bg
        self.border = ft.border.only(right=ft.BorderSide(1, self.palette.sidebar_border))
        self.build_menu()
        self.update()
        
    def refresh_locale(self):
        self.build_menu()
        self.update()

    def build_menu(self):
        # Language Selector - Segmented Toggle Style
        def lang_btn(text, lang_code):
            is_selected = self.app_state.lang == lang_code
            return ft.Container(
                content=ft.Text(
                    text, 
                    size=11, 
                    weight=ft.FontWeight.BOLD, 
                    color="#FFFFFF" if is_selected else self.palette.text_grey
                ),
                bgcolor=self.palette.primary if is_selected else ft.Colors.TRANSPARENT,
                border_radius=6,
                padding=ft.padding.symmetric(vertical=6),
                alignment=ft.alignment.center,
                expand=True,
                on_click=lambda _: self.app_state.set_language(lang_code),
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
            )

        lang_selector = ft.Container(
            content=ft.Row(
                [
                    lang_btn("EN", "en"),
                    lang_btn("VI", "vi"),
                    lang_btn("JA", "ja"),
                ],
                spacing=2,
            ),
            bgcolor=self.palette.bg_light_blue,
            border_radius=8,
            padding=4,
            margin=ft.padding.only(left=10, right=10, bottom=15)
        )

        # Define items here to capture current locale
        items_data = [
            {"icon": AppIcons.dashboard, "label": self.app_state.get_text("dashboard")},
            {"icon": AppIcons.settings, "label": self.app_state.get_text("settings")},
            {"icon": AppIcons.logs, "label": self.app_state.get_text("logs")},
            {"icon": ft.Icons.INFO_OUTLINE, "label": self.app_state.get_text("about")},
        ]
        
        menu_items = []
        for idx, item in enumerate(items_data):
            menu_items.append(
                SidebarItem(
                    icon=item["icon"],
                    label=item["label"],
                    selected=(idx == self.selected_index),
                    on_click=lambda e, i=idx: self.handle_nav(i),
                    palette=self.palette
                )
            )
        
        # Update title based on selected app
        app_names = {
            "antigravity": "Antigravity",
            "claude": "Claude Code",
            "codex": "Codex"
        }
        app_title = app_names.get(self.app_state.selected_app, "Manager")
        
        self.content = ft.Column(
            [
                ft.Container(
                    content=ft.Text(app_title, size=12, weight=ft.FontWeight.BOLD, color=self.palette.text_grey),
                    padding=ft.padding.only(left=10, bottom=10)
                ),
                lang_selector,
                ft.Column(menu_items, spacing=2)
            ]
        )

    def on_language_change(self, e):
        # Deprecated, logic moved to button click
        pass

    def handle_nav(self, index):
        self.selected_index = index
        self.build_menu()
        self.update()
        self.on_nav_change(index)

def main(page: ft.Page):
    # Try to write log on startup to verify path and permissions
    try:
        from utils import info, get_app_data_dir
        app_dir = get_app_data_dir()
        info(f"App started, data directory: {app_dir}")
        info(f"Python version: {sys.version}")
        info(f"Platform: {sys.platform}")
    except Exception as e:
        print(f"Failed to write startup log: {e}")
        
    # Initial palette
    palette = get_palette(page)
    page.bgcolor = palette.bg_page

    # Define references to views and sidebar
    home_view = None
    settings_view = None
    logs_view = None
    about_view = None
    sidebar = None
    
    def refresh_app():
        """Callback to refresh all components when language changes"""
        nonlocal home_view, settings_view, logs_view, about_view, sidebar
        if home_view: 
            home_view.update_locale()
            # Force rebuild content if app changed
            home_view.rebuild_content()
        if settings_view: settings_view.update_locale()
        if logs_view: logs_view.update_locale()
        if about_view: about_view.update_locale()
        if sidebar: sidebar.refresh_locale()
        
        # Update page title if needed
        page.title = app_state.get_text("app_title")
        page.update()

    # Initialize AppState
    app_state = AppState(page, on_refresh=refresh_app)

    page.title = app_state.get_text("app_title")
    page.theme_mode = ft.ThemeMode.SYSTEM
    
    # Window settings optimization
    page.window_width = 1000
    page.window_height = 700
    page.window_min_width = 800
    page.window_min_height = 600
    page.window_resizable = True
    page.padding = 0
    
    # Set window icon (must use .ico format on Windows and page.window.icon property)
    page.window.icon = "icon.ico"
    
    # Define views
    home_view = HomeView(page, app_state)
    settings_view = SettingsView(page, app_state)
    logs_view = LogsView(page, app_state)
    about_view = AboutView(page, app_state)
    
    views = {
        0: home_view,
        1: settings_view,
        2: logs_view,
        3: about_view
    }

    content_area = ft.Container(
        content=home_view,
        expand=True,
        padding=0,
        bgcolor=palette.bg_page
    )

    def change_route(index):
        content_area.content = views[index]
        content_area.update()

    sidebar = Sidebar(page, app_state, change_route)

    page.add(
        ft.Row(
            [
                sidebar,
                content_area,
            ],
            expand=True,
            spacing=0,
        )
    )
    
    def theme_changed(e):
        palette = get_palette(page)
        page.bgcolor = palette.bg_page
        content_area.bgcolor = palette.bg_page
        
        sidebar.update_theme()
        home_view.update_theme()
        settings_view.update_theme()
        logs_view.update_theme()
        about_view.update_theme()
        
        page.update()

    page.on_platform_brightness_change = theme_changed

if __name__ == "__main__":
    # Handle assets path for both development and PyInstaller frozen state
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        if hasattr(sys, '_MEIPASS'):
            # --onefile mode: assets are extracted to temp dir
            assets_path = str(Path(sys._MEIPASS) / "assets")
        else:
            # --onedir mode: assets are next to the executable
            assets_path = str(Path(sys.executable).parent / "assets")
    else:
        # Running as script
        # gui/main.py -> parent is gui -> parent is root -> assets
        assets_path = str(Path(__file__).parent.parent / "assets")
        
    try:
        ft.app(target=main, assets_dir=assets_path)
    except Exception as e:
        import traceback
        print("CRITICAL ERROR: Application crashed!")
        print(traceback.format_exc())
        input("Press Enter to exit...")
    except KeyboardInterrupt:
        pass
    finally:
        # If the app exits normally, we might still want to pause if debugging
        # input("App exited. Press Enter to close...")
        pass
