import flet as ft
from core.models import PaymentTier
from ui.services.rules_service import get_payment_tiers, delete_payment_tier
from ui.views.rules.tiers_dialog import open_tiers_dialog


def build_tiers_table(
    tiers: list[PaymentTier],
    on_edit: callable,
    on_delete: callable,
) -> ft.DataTable:

    columns = [
        ft.DataColumn(ft.Text("Min Settlement"), numeric=True),
        ft.DataColumn(ft.Text("Max Settlement"), numeric=True),
        ft.DataColumn(ft.Text("Min Payment"), numeric=True),
        ft.DataColumn(ft.Text("Max Term"), numeric=True),
        ft.DataColumn(ft.Text("Max Term (LPL)"), numeric=True),
        ft.DataColumn(ft.Text("Actions")),
    ]

    rows = []
    for index, tier in enumerate(tiers):
        current_index = index
        current_tier  = tier

        max_display = "∞" if tier.max_settlement == float("inf") else f"${tier.max_settlement:,.2f}"

        row = ft.DataRow(
            cells= [
                ft.DataCell(ft.Text(f"${tier.min_settlement:,.2f}")),
                ft.DataCell(ft.Text(max_display)),
                ft.DataCell(ft.Text(f"${tier.min_payment:,.2f}")),
                ft.DataCell(ft.Text(str(tier.max_term_default))),
                ft.DataCell(ft.Text(str(tier.max_term_lpl))),
                ft.DataCell(
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon= ft.icons.EDIT_OUTLINED,
                                tooltip="Edit",
                                on_click=lambda _, t=current_tier, i=current_index: on_edit(t, i),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE,
                                tooltip= "Delete",
                                icon_color=ft.colors.ERROR,
                                on_click= lambda _, i=current_index: on_delete(i),
                            ),
                        ],
                        tight= True,
                    )
                ),
            ]
        )
        rows.append(row)

    return ft.DataTable(
        columns= columns,
        rows=rows,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=8,
        vertical_lines=ft.BorderSide(1, ft.colors.OUTLINE_VARIANT),
        horizontal_lines=ft.BorderSide(1, ft.colors.OUTLINE_VARIANT),
    )


def build_tiers_tab(page: ft.Page) -> ft.Container:

    table_container = ft.Column(scroll=ft.ScrollMode.AUTO)

    def refresh_table() -> None:
        tiers = get_payment_tiers()
        table_container.controls = [
            build_tiers_table(tiers, on_edit, on_delete)
        ]
        table_container.update()

    def on_edit(tier: PaymentTier, index: int) -> None:
        open_tiers_dialog(page, tier, index, on_save=refresh_table)

    def on_delete(index: int) -> None:
        delete_payment_tier(index)
        refresh_table()

    def on_add_clicked(event: ft.ControlEvent) -> None:
        open_tiers_dialog(page, None, None, on_save=refresh_table)

    # Carga inicial
    tiers = get_payment_tiers()
    table_container.controls = [
        build_tiers_table(tiers, on_edit, on_delete)
    ]

    return ft.Container(
        content= ft.Column(
            controls= [
                ft.ElevatedButton(
                    content=ft.Row(
                        controls=[ft.Icon(ft.icons.ADD), ft.Text("Add Tier")],
                        tight=True,
                    ),
                    on_click=on_add_clicked,
                ),
                table_container,
            ],
            spacing= 12,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.only(top=20),
    )