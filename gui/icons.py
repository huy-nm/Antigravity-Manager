"""
Platform-adaptive icon system for AI Tools Manager.
Automatically selects appropriate icon set based on the operating system.
"""

import platform

import flet as ft


class AppIcons:
    """
    Unified icon interface that adapts to the platform.
    - macOS: Uses CupertinoIcons (native look)
    - Windows/Linux: Uses Material Icons
    """

    _is_macos = platform.system() == "Darwin"

    # App Icons
    app_antigravity = (
        ft.CupertinoIcons.ROCKET_FILL if _is_macos else ft.Icons.ROCKET_LAUNCH
    )
    app_claude = ft.CupertinoIcons.CHAT_BUBBLE_2_FILL if _is_macos else ft.Icons.CHAT
    app_codex = (
        ft.CupertinoIcons.CHEVRON_LEFT_SLASH_CHEVRON_RIGHT
        if _is_macos
        else ft.Icons.CODE
    )

    # Navigation Icons
    dashboard = ft.CupertinoIcons.SQUARE_GRID_2X2 if _is_macos else ft.Icons.DASHBOARD
    settings = ft.CupertinoIcons.GEAR if _is_macos else ft.Icons.SETTINGS
    logs = ft.CupertinoIcons.DOC_TEXT if _is_macos else ft.Icons.TEXT_SNIPPET

    # Action Icons
    add = ft.CupertinoIcons.ADD if _is_macos else ft.Icons.ADD
    delete = ft.CupertinoIcons.DELETE if _is_macos else ft.Icons.DELETE_OUTLINE
    refresh = ft.CupertinoIcons.REFRESH if _is_macos else ft.Icons.REFRESH

    # Status Icons
    check_circle = (
        ft.CupertinoIcons.CHECK_MARK_CIRCLED_SOLID
        if _is_macos
        else ft.Icons.CHECK_CIRCLE
    )
    pause_circle = (
        ft.CupertinoIcons.PAUSE_CIRCLE if _is_macos else ft.Icons.PAUSE_CIRCLE_FILLED
    )
    info = ft.CupertinoIcons.INFO if _is_macos else ft.Icons.INFO

    # File & Folder Icons
    folder = ft.CupertinoIcons.FOLDER_SOLID if _is_macos else ft.Icons.FOLDER
    document = ft.CupertinoIcons.DOC_TEXT_SEARCH if _is_macos else ft.Icons.SEARCH

    # Menu & More Icons
    ellipsis = ft.CupertinoIcons.ELLIPSIS if _is_macos else ft.Icons.MORE_VERT
    swap = ft.Icons.SWAP_HORIZ  # Same on all platforms

    @classmethod
    def is_macos(cls):
        """Returns True if running on macOS"""
        return cls._is_macos
