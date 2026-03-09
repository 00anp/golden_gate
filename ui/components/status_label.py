import flet as ft


def build_status_label(initial_text: str = "") -> ft.Text:
    return ft.Text(
        value=initial_text, 
        size=13,
        color=ft.colors.SECONDARY,
        italic=True,
    )