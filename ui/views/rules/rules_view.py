import flet as ft
from ui.views.rules.settlement_tab import build_settlement_tab
from ui.views.rules.tiers_tab import build_tiers_tab


def build_rules_view(page: ft.Page) -> ft.Column:

    tabs = ft.Tabs(
        selected_index= 0,
        tabs= [
            ft.Tab(
                text="Settlement Rules",
                content=build_settlement_tab(page),
            ),
            ft.Tab(
                text="Payment Tiers",
                content=build_tiers_tab(page),
            ),
        ],
        expand=True,
    )

    return ft.Column(
        controls=[
            ft.Text("Business Rules", size=22, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            tabs,
        ],
        spacing=12,
        expand=True,
    )