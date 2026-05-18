import flet as ft
from ui.views.process.process_tabs import build_process_tabs
from ui.views.passwords_view import build_passwords_view
from ui.views.rules.rules_view import build_rules_view
from ui.views.history_view import build_history_view


def build_app(page: ft.Page) -> None:

    page.title= "Golden Gate"
    page.window_width = 1700
    page.window_height = 1100
    page.window_min_width = 1200
    page.padding = 0

    file_picker = ft.FilePicker()
    folder_picker = ft.FilePicker()

    content_area = ft.Container(expand=True, padding=20)

    VIEWS = {
        0: lambda: build_process_tabs(page, file_picker, folder_picker),
        1: build_passwords_view,
        2: lambda: build_rules_view(page),
        3: build_history_view,
    }


    def navigate(index: int) -> None:
        view_builder =  VIEWS.get(index)

        if view_builder:
            content_area.content = view_builder()
            content_area.update()


    def on_navigation_change(event) -> None:
        index =  event.control.selected_index
        navigate(index)


    navigation_rail = ft.NavigationRail(
        selected_index=0,
        label_type= ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        on_change=on_navigation_change,

        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.UPLOAD_FILE_OUTLINED,
                selected_icon=ft.icons.UPLOAD_FILE,
                label="Process"
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.LOCK_OUTLINE,
                selected_icon=ft.icons.LOCK,
                label="Passwords"
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.RULE_OUTLINED,
                selected_icon=ft.icons.RULE,
                label="Business Rules"
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.HISTORY_OUTLINED,
                selected_icon=ft.icons.HISTORY,
                label="Records"
            ),
        ]
    )

    page.add(
        ft.Row(
            controls=[
                navigation_rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
        ),
    )
    
    page.overlay.append(file_picker)
    page.overlay.append(folder_picker)
    page.update()

    navigate(0)
