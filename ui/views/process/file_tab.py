import flet as ft


def build_file_tab(
    file_picker:   ft.FilePicker,
    folder_picker: ft.FilePicker,
    on_next:       callable,   # on_next(file_path: str, folder_path: str)
) -> ft.Container:
    """Builds the File Selection tab with file/folder pickers and a Next button."""

    # Mutable state via single-element lists (Flet 0.24.1 pattern)
    selected_file   = [""]
    selected_folder = [""]

    file_display   = ft.Text(value="No file selected",   italic=True, color=ft.colors.SECONDARY)
    folder_display = ft.Text(value="No folder selected", italic=True, color=ft.colors.SECONDARY)
    error_label    = ft.Text(value="", color=ft.colors.ERROR)

    def on_file_result(event: ft.ControlEvent) -> None:
        if event.files and len(event.files) > 0:
            selected_file[0]   = event.files[0].path
            file_display.value = event.files[0].path
        file_display.update()

    def on_folder_result(event: ft.ControlEvent) -> None:
        if event.path:
            selected_folder[0]   = event.path
            folder_display.value = event.path
        folder_display.update()

    file_picker.on_result   = on_file_result
    folder_picker.on_result = on_folder_result

    def on_browse_file_clicked(event: ft.ControlEvent) -> None:
        file_picker.pick_files(allowed_extensions=["xlsx"])

    def on_browse_folder_clicked(event: ft.ControlEvent) -> None:
        folder_picker.get_directory_path()

    def on_next_clicked(event: ft.ControlEvent) -> None:
        if not selected_file[0]:
            error_label.value = "Please select an input file."
            error_label.update()
            return
        if not selected_folder[0]:
            error_label.value = "Please select an output folder."
            error_label.update()
            return
        error_label.value = ""
        error_label.update()
        on_next(selected_file[0], selected_folder[0])

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("File Selection", size=22, weight=ft.FontWeight.BOLD),
                ft.Divider(),

                ft.Text("Input File", weight=ft.FontWeight.W_500),
                ft.Row(controls=[
                    file_display,
                    ft.ElevatedButton(
                        content=ft.Row(
                            controls=[ft.Icon(ft.icons.FOLDER_OPEN), ft.Text("Browse")],
                            tight=True,
                        ),
                        on_click=on_browse_file_clicked,
                    ),
                ]),

                ft.Divider(height=10, color=ft.colors.TRANSPARENT),

                ft.Text("Output Folder", weight=ft.FontWeight.W_500),
                ft.Row(controls=[
                    folder_display,
                    ft.ElevatedButton(
                        content=ft.Row(
                            controls=[ft.Icon(ft.icons.FOLDER), ft.Text("Browse")],
                            tight=True,
                        ),
                        on_click=on_browse_folder_clicked,
                    ),
                ]),

                ft.Divider(height=10, color=ft.colors.TRANSPARENT),

                error_label,

                ft.ElevatedButton(
                    content=ft.Row(
                        controls=[ft.Icon(ft.icons.ARROW_FORWARD), ft.Text("Next →")],
                        tight=True,
                    ),
                    on_click=on_next_clicked,
                ),
            ],
            spacing=12,
        ),
        padding=20,
        expand=True,
    )