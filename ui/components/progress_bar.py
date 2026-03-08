import flet as ft


def build_progress_bar() -> ft.Column:

    percent_text = ft.Text(
        value= "0%",
        size= 12,
        color= ft.Colors.SECONDARY,
    )

    bar = ft.ProgressBar(
        value= 0, 
        width= 400,
        bgcolor= ft.Colors.ON_SURFACE_VARIANT,
        color = ft.Colors.PRIMARY,
    )

    return ft.Column(
        controls= [bar, percent_text],
        spacing= 4,
        visible= False
    )
