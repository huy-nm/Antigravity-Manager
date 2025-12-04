import flet as ft
import threading
import time
from datetime import datetime
from process_manager import is_process_running, start_antigravity, close_antigravity
from account_manager import add_account_snapshot, list_accounts_data, switch_account, delete_account
from db_manager import get_current_account_info
from theme import get_palette
from icons import AppIcons

RADIUS_CARD = 12
PADDING_PAGE = 20

class HomeView(ft.Container):
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
        
        # Accounts list
        self.accounts_list = ft.Column(spacing=12, scroll=ft.ScrollMode.HIDDEN)
        self.current_email = None
        
        # Start status monitoring
        self.running = True

    def did_mount(self):
        self.running = True
        self.rebuild_content() # Initial build
        self.refresh_data()
        self.monitor_thread = threading.Thread(target=self.monitor_status, daemon=True)
        self.monitor_thread.start()
        
        # Automatically backup current account
        self.auto_backup()

    def auto_backup(self):
        def task():
            # Delay slightly to ensure UI is loaded
            time.sleep(1)
            if add_account_snapshot():
                self.refresh_data()
        threading.Thread(target=task, daemon=True).start()

    def will_unmount(self):
        self.running = False

    def update_theme(self):
        self.palette = get_palette(self.main_page)
        self.bgcolor = self.palette.bg_page
        self.rebuild_content()
        self.refresh_data()
        if self.page:
            self.update()

    def update_locale(self):
        self.rebuild_content()
        self.refresh_data()
        if self.page:
            self.update()

    def build_ui(self):
        # Just container init, actual content is built in rebuild_content to support dynamic updates
        pass

    def rebuild_content(self):
        # App Switching Tabs
        tabs = ft.Tabs(
            selected_index=["antigravity", "claude", "codex"].index(self.app_state.selected_app),
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text=self.app_state.get_text("antigravity"),
                    icon=AppIcons.app_antigravity,
                ),
                ft.Tab(
                    text=self.app_state.get_text("claude"),
                    icon=AppIcons.app_claude,
                ),
                ft.Tab(
                    text=self.app_state.get_text("codex"),
                    icon=AppIcons.app_codex,
                ),
            ],
            on_change=self.on_tab_change,
        )

        # Dashboard Content based on selected app
        if self.app_state.selected_app != "antigravity":
            dashboard_content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(AppIcons.info, size=64, color=self.palette.text_grey),
                        ft.Text("Coming Soon", size=20, weight=ft.FontWeight.BOLD, color=self.palette.text_main),
                        ft.Text(f"Support for {self.app_state.selected_app} is under development.", size=14, color=self.palette.text_grey),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                alignment=ft.alignment.center,
                expand=True,
                padding=40
            )
        else:
            # Status Bar Elements
            self.status_bar_text = ft.Text(self.app_state.get_text("status_checking"), size=13, weight=ft.FontWeight.W_500, color=self.palette.primary)
            self.status_bar_icon = ft.Icon(AppIcons.info, size=16, color=self.palette.primary)
            
            self.status_bar = ft.Container(
                content=ft.Row(
                    [
                        self.status_bar_icon,
                        self.status_bar_text
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                bgcolor=self.palette.bg_light_blue,
                padding=ft.padding.symmetric(vertical=8, horizontal=15),
                border_radius=8,
                animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
                on_click=self.toggle_app_status
            )
            
            # List Header Elements
            self.list_title = ft.Text(self.app_state.get_text("account_list"), size=18, weight=ft.FontWeight.BOLD, color=self.palette.text_main)
            self.stats_badge_text = ft.Text("0", size=12, color=self.palette.primary, weight=ft.FontWeight.BOLD)
            self.stats_badge = ft.Container(
                content=self.stats_badge_text,
                bgcolor=self.palette.bg_light_blue,
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                border_radius=10,
            )
            
            if not hasattr(self, 'accounts_list'):
                self.accounts_list = ft.Column(spacing=12, scroll=ft.ScrollMode.HIDDEN)

            dashboard_content = ft.Column(
                [
                    # 1. Status Notification Bar
                    self.status_bar,
                    
                    ft.Container(height=20),
                    
                    # 2. List Header with Integrated Stats
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    self.list_title,
                                    self.stats_badge
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8
                            ),
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(AppIcons.add, size=14, color="#FFFFFF"), # Always white on primary
                                        ft.Text(self.app_state.get_text("backup_current"), size=13, color="#FFFFFF", weight=ft.FontWeight.W_600)
                                    ],
                                    spacing=4,
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                bgcolor=self.palette.primary,
                                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                border_radius=8,
                                on_click=self.backup_current,
                                shadow=ft.BoxShadow(
                                    spread_radius=0,
                                    blur_radius=8,
                                    color=ft.Colors.with_opacity(0.4, self.palette.primary),
                                    offset=ft.Offset(0, 2),
                                )
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    
                    ft.Container(height=15),

                    # 3. Account List Container
                    ft.Container(
                        content=self.accounts_list,
                        expand=True, # Take up remaining space
                    )
                ],
                expand=True
            )

        self.content = ft.Column(
            [
                tabs,
                ft.Container(height=10),
                ft.Container(
                    content=dashboard_content,
                    expand=True
                )
            ],
            expand=True
        )

    def on_tab_change(self, e):
        index = e.control.selected_index
        apps = ["antigravity", "claude", "codex"]
        if 0 <= index < len(apps):
            new_app = apps[index]
            self.app_state.set_app(new_app)
            # Since set_app triggers refresh_app in main.py, and refresh_app calls rebuild_content,
            # we don't strictly need to do anything here, but main.py might only refresh if app CHANGED.
            # But set_app checks for change. So it should be fine.
            # However, calling set_app will trigger on_refresh which calls home_view.rebuild_content()
            pass

    def refresh_data(self):
        # Refresh current email
        info = get_current_account_info()
        if info and "email" in info:
            self.current_email = info["email"]
            
        # Refresh accounts list
        self.accounts_list.controls.clear()
        accounts = list_accounts_data()
        
        # Update stats badge
        # We need to handle pluralization if strict, but simple concatenation is fine here
        # Or just use the count
        self.stats_badge_text.value = f"{len(accounts)}"
        
        if not accounts:
            self.accounts_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(AppIcons.document, size=40, color=self.palette.text_grey),
                            ft.Container(height=10),
                            ft.Text(self.app_state.get_text("no_backups"), color=self.palette.text_grey, size=14),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    alignment=ft.alignment.center,
                    padding=40,
                    expand=True
                )
            )
        else:
            for idx, acc in enumerate(accounts):
                is_current = (acc.get('email') == self.current_email)
                self.accounts_list.controls.append(self.create_account_row(acc, is_current))
        
        if self.page:
            self.update()

    def format_last_used(self, iso_str):
        if not iso_str:
            return self.app_state.get_text("never")
        try:
            dt = datetime.fromisoformat(iso_str)
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return str(iso_str).split('T')[0]

    def create_account_row(self, acc, is_current):
        # Gradient effect for current account card
        # Use a subtle gradient if current, else solid color
        # Flet Container supports gradient
        
        bg_color = self.palette.bg_card
        border = None
        
        if is_current:
            # Highlight current account with a subtle border
            border = ft.border.all(1, self.palette.primary)
        
        return ft.Container(
            content=ft.Row(
                [
                    # Left: Avatar & Info
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(
                                    acc['name'][0].upper() if acc['name'] else "?", 
                                    color="#FFFFFF",
                                    weight=ft.FontWeight.BOLD,
                                    size=16
                                ),
                                width=40,
                                height=40,
                                border_radius=20,
                                bgcolor=self.palette.primary if is_current else self.palette.text_grey,
                                alignment=ft.alignment.center,
                                shadow=ft.BoxShadow(
                                    spread_radius=0,
                                    blur_radius=6,
                                    color=ft.Colors.with_opacity(0.3, self.palette.primary) if is_current else "#00000000",
                                    offset=ft.Offset(0, 2),
                                )
                            ),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(acc['name'], size=15, weight=ft.FontWeight.BOLD, color=self.palette.text_main),
                                            ft.Container(
                                                content=ft.Text(self.app_state.get_text("current"), size=10, color=self.palette.primary, weight=ft.FontWeight.BOLD),
                                                bgcolor=self.palette.bg_light_blue,
                                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                                border_radius=4,
                                                visible=is_current
                                            )
                                        ],
                                        spacing=6,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                                    ),
                                    ft.Text(acc['email'], size=12, color=self.palette.text_grey),
                                ],
                                spacing=2,
                                alignment=ft.MainAxisAlignment.CENTER
                            )
                        ],
                        spacing=12
                    ),
                    
                    # Right: Date & Menu
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        self.app_state.get_text("last_used"), 
                                        size=10, 
                                        color=self.palette.text_grey,
                                        text_align=ft.TextAlign.RIGHT
                                    ),
                                    ft.Text(
                                        self.format_last_used(acc.get('last_used')), 
                                        size=12, 
                                        color=self.palette.text_grey,
                                        weight=ft.FontWeight.W_500
                                    ),
                                ],
                                spacing=2,
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.END
                            ),
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.SWAP_HORIZ,
                                        icon_color=self.palette.primary,
                                        tooltip=self.app_state.get_text("switch_to"),
                                        on_click=lambda e: self.switch_to_account(acc['id'])
                                    ),
                                    ft.IconButton(
                                        icon=AppIcons.delete,
                                        icon_color="#FF3B30",
                                        tooltip=self.app_state.get_text("delete_backup"),
                                        on_click=lambda e: self.delete_acc(acc['id'])
                                    ),
                                ],
                                spacing=0
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor=bg_color,
            border=border,
            border_radius=RADIUS_CARD,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=self.palette.shadow,
                offset=ft.Offset(0, 2),
            ),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            on_hover=self.on_card_hover
        )

    def on_card_hover(self, e):
        # Only show shadow hover effect in light mode or if shadow is visible
        if self.palette.shadow != "#00000000":
            e.control.shadow.blur_radius = 15 if e.data == "true" else 10
            e.control.shadow.offset = ft.Offset(0, 6) if e.data == "true" else ft.Offset(0, 2)
            e.control.update()

    def monitor_status(self):
        while self.running:
            is_running = is_process_running()
            
            # Update Status Bar
            if hasattr(self, 'status_bar'):
                if is_running:
                    self.status_bar.bgcolor = self.palette.bg_light_green
                    self.status_bar_icon.name = AppIcons.check_circle
                    self.status_bar_icon.color = "#34C759"
                    self.status_bar_text.value = self.app_state.get_text("status_running")
                    self.status_bar_text.color = "#34C759"
                else:
                    self.status_bar.bgcolor = self.palette.bg_light_red
                    self.status_bar_icon.name = AppIcons.pause_circle
                    self.status_bar_icon.color = "#FF3B30"
                    self.status_bar_text.value = self.app_state.get_text("status_stopped")
                    self.status_bar_text.color = "#FF3B30"
                
                if self.page:
                    self.update()
            time.sleep(2)

    def toggle_app_status(self, e):
        if is_process_running():
            self.stop_app(e)
        else:
            self.start_app(e)

    def show_message(self, message, is_error=False):
        dlg = ft.CupertinoAlertDialog(
            title=ft.Text(self.app_state.get_text("notice")),
            content=ft.Text(message),
            actions=[
                ft.CupertinoDialogAction(
                    self.app_state.get_text("ok"), 
                    is_destructive_action=is_error,
                    on_click=lambda e: self.main_page.close(dlg)
                )
            ]
        )
        self.main_page.open(dlg)

    def start_app(self, e):
        if start_antigravity():
            pass
        else:
            self.show_message(self.app_state.get_text("start_failed"), True)

    def stop_app(self, e):
        def close_task():
            if close_antigravity():
                pass
            else:
                pass
        threading.Thread(target=close_task, daemon=True).start()

    def backup_current(self, e):
        def backup_task():
            try:
                if add_account_snapshot():
                    self.refresh_data()
                    # self.show_message(self.app_state.get_text("backup_success"))
                else:
                    pass
            except Exception as e:
                import traceback
                error_msg = f"Backup exception: {str(e)}\n{traceback.format_exc()}"
                from utils import error
                error(error_msg)
                self.show_message(f"{self.app_state.get_text('backup_error')}: {str(e)}", True)
        threading.Thread(target=backup_task, daemon=True).start()

    def show_confirm_dialog(self, title, content, on_confirm, confirm_text="OK", is_destructive=False):
        def handle_confirm(e):
            on_confirm()
            self.main_page.close(dlg)
            
        dlg = ft.CupertinoAlertDialog(
            title=ft.Text(title),
            content=ft.Text(content),
            actions=[
                ft.CupertinoDialogAction(
                    self.app_state.get_text("cancel"), 
                    on_click=lambda e: self.main_page.close(dlg)
                ),
                ft.CupertinoDialogAction(
                    confirm_text, 
                    is_destructive_action=is_destructive,
                    on_click=handle_confirm
                ),
            ]
        )
        self.main_page.open(dlg)

    def switch_to_account(self, account_id):
        def task():
            try:
                if switch_account(account_id):
                    self.refresh_data()
                    # self.show_message(self.app_state.get_text("switch_success"))
                else:
                    self.show_message(self.app_state.get_text("switch_fail"), True)
            except Exception as e:
                import traceback
                error_msg = f"Switch account exception: {str(e)}\n{traceback.format_exc()}"
                from utils import error
                error(error_msg)
                self.show_message(f"{self.app_state.get_text('switch_error')}: {str(e)}", True)
        threading.Thread(target=task, daemon=True).start()

    def delete_acc(self, account_id):
        def confirm_delete():
            try:
                if delete_account(account_id):
                    self.refresh_data()
                else:
                    self.show_message(self.app_state.get_text("delete_failed"), True)
            except Exception as e:
                import traceback
                error_msg = f"Delete exception: {str(e)}\n{traceback.format_exc()}"
                from utils import error
                error(error_msg)
                self.show_message(f"{self.app_state.get_text('delete_error')}: {str(e)}", True)
            self.page.update()

        self.show_confirm_dialog(
            title=self.app_state.get_text("confirm_delete"),
            content=self.app_state.get_text("delete_msg"),
            on_confirm=confirm_delete,
            confirm_text=self.app_state.get_text("delete"),
            is_destructive=True
        )
