import flet as ft
from ui.services.process_service import run_full_pipeline
from ui.components.progress_bar import build_progress_bar
from ui.components.status_label import build_status_label
from ui.services.password_service import load_passwords, get_passwords_dict
from core.models import ProcessResult

def build_process_view(
        page: ft.Page,
        file_picker: ft.FilePicker,
        folder_picker: ft.FilePicker) -> ft.Column:

    selected_file_path: list[str] = [""]
    selected_output_path: list[str] = [""]
    process_button_ref:   list[ft.ElevatedButton | None] = [None]

    file_display = ft.Text(
        value= "No file selected",
        italic= True, 
        color= ft.colors.SECONDARY,
    )

    folder_display = ft.Text(
        value="No folder selected",
        italic= True, 
        color= ft.colors.SECONDARY,
    )

    progress_section = build_progress_bar()
    status_label = build_status_label()


    def on_progress(value: float) -> None:
        progress_section.controls[0].value = value
        progress_section.controls[1].value = f"{int(value * 100)}%"
        progress_section.update()

    
    def on_status(message: str) -> None:
        status_label.value = message
        status_label.update()

    
    def on_complete(result: ProcessResult) -> None:
        if result.success:
            on_status(
                f"Process complete: {result.files_created} files "
                f"in {result.duration_seconds:0f} s."
            )

        else:
            on_status(
                f"Error: {result.errors[0]}"
            )
        
        if process_button_ref[0] is not None:
            process_button_ref[0].disabled = False
            process_button_ref[0].update()


    def on_file_picked(event: ft.ControlEvent) -> None:
        if event.files and len(event.files) > 0:
            selected_file_path[0] = event.files[0].path
            file_display.value    = event.files[0].path
        else:
            file_display.value = "No file selected."
        file_display.update()


    def on_folder_picked(event: ft.ControlEvent) -> None:
        if event.path:
            selected_output_path[0] = event.path
            folder_display.value    = event.path
        else:
            folder_display.value = "No folder selected."
        folder_display.update()


    file_picker.on_result   = on_file_picked
    folder_picker.on_result = on_folder_picked

    def on_pick_file_clicked(event: ft.ControlEvent) -> None:
        file_picker.pick_files(allowed_extensions=["xlsx"])


    def on_pick_folder_clicked(event: ft.ControlEvent) -> None:
        folder_picker.get_directory_path()


    def on_process_clicked(event: ft.ControlEvent) -> None:
        passwords = get_passwords_dict(load_passwords())
        
        if selected_file_path[0] == "":
            on_status("Please select an Excel file.")
            return

        if selected_output_path[0] == "":
            on_status("Please select an output folder.")
            return
        
        process_button_ref[0].disabled = True
        process_button_ref[0].update()
        progress_section.visible = True
        progress_section.update()
        on_status("Starting...")

        run_full_pipeline(
            input_path= selected_file_path[0],
            output_folder= selected_output_path[0],
            passwords= passwords,
            on_progress= on_progress,
            on_status= on_status,
            on_complete= on_complete,
        )

    process_button = ft.ElevatedButton(
        content = ft.Row(
            controls = [
                ft.Icon(ft.icons.PLAY_ARROW),
                ft.Text("Process file"),
            ],
            tight=True,
        ),
        on_click= on_process_clicked,
        style= ft.ButtonStyle(
            padding=ft.padding.symmetric(horizontal=30, vertical=15)
        ),
    )

    process_button_ref[0] = process_button   


    return ft.Column(
        controls= [
            ft.Text("Process File", size=22, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.Text("Input File", weight=ft.FontWeight.W_500),
            ft.Row(controls = [
                file_display, 
                ft.ElevatedButton(
                    content = ft.Row(
                        controls = [
                            ft.Icon(ft.icons.FOLDER_OPEN),
                            ft.Text("Browse"),
                        ],
                        tight = True,
                    ),
                    on_click= on_pick_file_clicked,
                ),
            ]),

            ft.Divider(height=10, color=ft.colors.TRANSPARENT),

            ft.Text("Output Folder", weight=ft.FontWeight.W_500),
            ft.Row(controls= [
                folder_display,
                ft.ElevatedButton(
                    content = ft.Row(
                        controls = [
                            ft.Icon(ft.icons.FOLDER),
                            ft.Text("Browse"),
                        ],
                        tight = True,
                    ),
                    on_click= on_pick_folder_clicked,
                ),
            ]),

            ft.Divider(height=20, color=ft.colors.TRANSPARENT),

            process_button,

            ft.Divider(height=10, color=ft.colors.TRANSPARENT),

            progress_section,
            status_label,   
        ],
        spacing=12,
        expand= True,
        )
