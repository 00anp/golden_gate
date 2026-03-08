import flet as ft
from ui.views.process_view import build_process_view
from ui.views.passwords_view import build_passwords_view
from ui.views.rules_view import build_rules_view
from ui.views.history_view import build_history_view


async def build_app(page: ft.Page) -> None:

    page.title= "Golden Gate"
    page.window_width = 1100
    page.window_height = 700
    page.window_min_width = 800
    page.padding = 0

    file_picker = ft.FilePicker()
    folder_picker = ft.FilePicker()

    page.overlay.append(file_picker)
    page.overlay.append(file_picker)

    content_area = ft.Container(
        expand=True,
        padding=20,
        content=None
    )

    VIEWS = {
        0: lambda: build_process_view(page, file_picker, folder_picker),
        1: build_passwords_view,
        2: build_rules_view,
        3: build_history_view,
    }


    async def navigate(index: int) -> None:
        view_builder =  VIEWS.get(index)

        if view_builder:
            content_area.content = await view_builder()
            content_area.update()


    async def on_navigation_change(event) -> None:
        index =  event.control.selected_index
        await navigate(index)


    navigation_rail = ft.NavigationRail(
        selected_index=0,
        label_type= ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        on_change=on_navigation_change,

        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.UPLOAD_FILE_OUTLINED,
                selected_icon=ft.Icons.UPLOAD_FILE,
                label="Process"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LOCK_OUTLINE,
                selected_icon=ft.Icons.LOCK,
                label="Passwords"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.RULE_OUTLINED,
                selected_icon=ft.Icons.RULE,
                label="Business Rules"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.HISTORY_OUTLINED,
                selected_icon=ft.Icons.HISTORY,
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
        )
    )

    await navigate(0)
