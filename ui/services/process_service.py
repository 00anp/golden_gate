import asyncio
import threading
import time
import os
from core.processor import process_file
from core.splitter import split_and_protect
from core.models import ProcessResult


def run_full_pipeline(
        input_path: str,
        output_folder: str,
        passwords: dict, 
        on_progress: callable,
        on_status: callable, 
        on_complete: callable
) -> None:
    
    def _worker() -> None:
        def call(coro):
            asyncio.run_coroutine_threadsafe(
                coro,
                loop=asyncio.get_event_loop()
            )
        start = time.time()

        try:
            call(on_status("Starting process..."))
            call(on_progress(0.0))

            processed_wb = process_file(
                input_path= input_path, 
                progress_callback= lambda v: call(on_progress(v)), 
                status_callback= lambda m: call(on_status(m)),
            )

            call(on_status("Splitting files by company..."))

            created_files: list[str] = split_and_protect(
                processed_wb= processed_wb,
                output_folder= output_folder,
                passwords= passwords,
                progress_callback= on_progress,
                status_callback= on_status,
            )

            duration = time.time() - start

            results = ProcessResult(
                success= True,
                total_rows= processed_wb.active.max_row - 1,
                files_created= len(created_files),
                companies_found= [os.path.basename(filepath).split("_")[0] for filepath in created_files],
                created_files= created_files,
                status_callback = on_status,
            )

            call(on_complete(results))

        except Exception as error:
            results_error = ProcessResult(
                success= False, 
                errors=[str(error)],
            )

            call(on_complete(results_error))
    
    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()