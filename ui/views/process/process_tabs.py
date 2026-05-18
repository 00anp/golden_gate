import flet as ft
import threading
import openpyxl
from ui.views.process.file_tab      import build_file_tab
from ui.views.process.prefilter_tab import build_prefilter_tab
from ui.views.process.analysis_tab  import build_analysis_tab
from ui.services.process_service    import run_full_pipeline
from ui.services.password_service   import load_passwords, get_passwords_dict
from ui.components.progress_bar     import build_progress_bar
from ui.components.status_label     import build_status_label
from core.models                    import ProcessResult


def build_process_tabs(
    page:          ft.Page,
    file_picker:   ft.FilePicker,
    folder_picker: ft.FilePicker,
) -> ft.Column:
    """Builds the 3-tab Process workflow: File → Review → Analysis."""

    # Shared state
    state = {
        "file_path":      "",
        "folder_path":    "",
        "ws":             None,   # loaded worksheet
        "wb":             None,   # loaded workbook
        "rows_to_remove": set(),
    }

    progress_section = build_progress_bar()
    status_label     = build_status_label()

    # Tab content placeholders
    tab_file     = ft.Tab(text="1. File",     content=ft.Container())
    tab_review   = ft.Tab(text="2. Review",   content=ft.Container(), disabled=True)
    tab_analysis = ft.Tab(text="3. Analysis", content=ft.Container(), disabled=True)

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[tab_file, tab_review, tab_analysis],
        expand=True,
    )

    def go_to_tab(index: int) -> None:
        tabs.selected_index = index
        tabs.update()

    def on_file_next(file_path: str, folder_path: str) -> None:
        state["file_path"]   = file_path
        state["folder_path"] = folder_path

        status_label.value = "Loading file..."
        status_label.update()

        def load_worker() -> None:
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            state["wb"] = wb
            state["ws"] = ws

            tab_review.content  = build_prefilter_tab(ws, on_review_next)
            tab_review.disabled = False
            status_label.value  = "File loaded. Review flagged rows."
            status_label.update()
            tabs.update()
            go_to_tab(1)

        threading.Thread(target=load_worker, daemon=True).start()

    def on_review_next(rows_to_remove: set[int]) -> None:
        state["rows_to_remove"] = rows_to_remove

        tab_analysis.content  = build_analysis_tab(
            page, state["ws"], rows_to_remove, on_process
        )
        tab_analysis.disabled = False
        tabs.update()
        go_to_tab(2)

    def on_process(final_rows_to_remove: set[int]) -> None:
        passwords = get_passwords_dict(load_passwords())
        progress_section.visible = True
        progress_section.update()
        status_label.value = "Starting pipeline..."
        status_label.update()

        run_full_pipeline(
            input_path=state["file_path"],
            output_folder=state["folder_path"],
            passwords=passwords,
            on_progress=on_progress,
            on_status=on_status,
            on_complete=on_complete,
        )

    def on_progress(value: float) -> None:
        progress_section.controls[0].value = value
        progress_section.controls[1].value = f"{int(value * 100)}%"
        progress_section.update()

    def on_status(message: str) -> None:
        status_label.value = message
        status_label.update()

    def on_complete(result: ProcessResult) -> None:
        if result.success:
            status_label.value = (
                f"Done: {result.files_created} files in {result.duration_seconds:.0f}s"
            )
        else:
            status_label.value = f"Error: {result.errors[0]}"
        status_label.update()

    # Build initial file tab
    tab_file.content = build_file_tab(file_picker, folder_picker, on_file_next)

    return ft.Column(
        controls=[
            ft.Text("Process File", size=22, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            tabs,
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            progress_section,
            status_label,
        ],
        spacing=12,
        expand=True,
    )