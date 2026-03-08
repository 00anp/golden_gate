import flet as ft
from ui.app import build_app



async def main(page: ft.Page) -> None:
    await build_app(page)

if __name__  == '__main__':
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        port=8080,)