import flet as ft
from ui.services.process_service import run_full_pipeline
from ui.components.progress_bar import build_progress_bar
from ui.components.status_label import build_status_label
from core.models import ProcessResult

async def build_process_view(
        page: ft.Page,
        file_picker: ft.FilePicker,
        folder_picker: ft.FilePicker) -> ft.Column:

    selected_file_path: list[str] = [""]
    selected_output_path: list[str] = [""]

    file_display = ft.Text(
        value= "No file selected",
        italic= True, 
        color= ft.Colors.SECONDARY,
    )

    folder_display = ft.Text(
        value="No folder selected",
        italic= True, 
        color= ft.Colors.SECONDARY,
    )

    progress_section = build_progress_bar()
    status_label = build_status_label()
    process_button_ref: list[ft.ElevatedButton | None] = [None]

    async def on_progress(value: float) -> None:
        progress_section.controls[0].value = value
        progress_section.controls[1].value = f"{int(value * 100)}%"
        progress_section.update()

    
    async def on_status(message: str) -> None:
        status_label.value = message
        status_label.update()

    
    async def on_complete(result: ProcessResult) -> None:
        if result.success:
            await on_status(
                f"Process complete: {result.files_created} files"
                f"in {result.duration_seconds:1f}s."
            )

        else:
            await on_status(
                f"Error: {result.errors[0]}"
            )
        
        if process_button_ref[0] is not None:
            process_button_ref[0].disabled = False
            process_button_ref[0].update()


    async def on_file_picked(event: ft.ControlEvent) -> None:
        if event.files and len(event.files) > 0:
            file: ft.FilePickerFile = event.files[0]
            selected_file_path[0] = file.path
            file_display.value = file.path
        else:
            file_display.value = "No file selected."

        file_display.update()
    

    async def on_folder_picked(event: ft.ControlEvent) -> None:
        if event.path:
            selected_output_path[0] = event.path
            folder_display.value = event.path
        else:
            folder_display.value = "No folder selected."
        
        folder_display.update()

    
    file_picker.on_result = on_file_picked
    folder_picker.on_result = on_folder_picked


    async def on_pick_file_clicked(event: ft.ControlEvent) -> None:
        await file_picker.pick_files(allowed_extensions=["xlsx"])

    
    async def on_pick_folder_clicked(event: ft.ControlEvent) -> None:
        await folder_picker.get_directory_path()


    async def on_process_clicked(event: ft.ControlEvent) -> None:
        if selected_file_path[0] == "":
            await on_status("Please select an Excel file.")
            return

        if selected_output_path[0] == "":
            await on_status("Please select an output folder.")
            return
        
        process_button_ref[0].disabled = True
        process_button_ref[0].update()
        progress_section.visible = True
        progress_section.update()
        await on_status("Starting...")

        run_full_pipeline(
            input_path= selected_file_path[0],
            output_folder= selected_output_path[0],
            passwords= {},
            on_progress= on_progress,
            on_status= on_status,
            on_complete= on_complete,
        )

    process_button = ft.ElevatedButton(
        content = ft.Row(
            controls = [
                ft.Icon(ft.Icons.PLAY_ARROW),
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
                            ft.Icon(ft.Icons.FOLDER_OPEN),
                            ft.Text("Browse"),
                        ],
                        tight = True,
                    ),
                    on_click= on_pick_file_clicked,
                ),
            ]),

            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

            ft.Text("Output Folder", weight=ft.FontWeight.W_500),
            ft.Row(controls= [
                folder_display,
                ft.ElevatedButton(
                    content = ft.Row(
                        controls = [
                            ft.Icon(ft.Icons.FOLDER),
                            ft.Text("Browse"),
                        ],
                        tight = True,
                    ),
                    on_click= on_pick_folder_clicked,
                ),
            ]),

            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

            process_button,

            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

            progress_section,
            status_label,   
        ],
        spacing=12,
        expand= True,
        )
