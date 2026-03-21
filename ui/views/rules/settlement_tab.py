import flet as ft
from core.models import SettlementRule
from ui.services.rules_service import get_settlement_rules, delete_settlement_rule
from ui.views.rules.settlement_dialog import open_settlement_dialog


def build_settlement_table(
    rules: list[SettlementRule],
    on_edit: callable,
    on_delete: callable,
) -> ft.DataTable:

    columns = [
        ft.DataColumn(ft.Text("Prefix")),
        ft.DataColumn(ft.Text("Threshold"), numeric=True),
        ft.DataColumn(ft.Text("Z High"), numeric=True),
        ft.DataColumn(ft.Text("AK High"), numeric=True),
        ft.DataColumn(ft.Text("Z Low"), numeric=True),
        ft.DataColumn(ft.Text("AK Low"), numeric=True),
        ft.DataColumn(ft.Text("Mark AM")),
        ft.DataColumn(ft.Text("Mark AQ")),
        ft.DataColumn(ft.Text("Copy Z→AK")),
        ft.DataColumn(ft.Text("Description")),
        ft.DataColumn(ft.Text("Actions")),
    ]

    rows = []
    for rule in rules:
        current_rule = rule

        row = ft.DataRow(
            cells= [
                ft.DataCell(ft.Text(rule.prefix)),
                ft.DataCell(ft.Text(str(rule.balance_threshold))),
                ft.DataCell(ft.Text(str(rule.z_high))),
                ft.DataCell(ft.Text(str(rule.ak_high))),
                ft.DataCell(ft.Text(str(rule.z_low))),
                ft.DataCell(ft.Text(str(rule.ak_low))),
                ft.DataCell(ft.Text("✓" if rule.mark_am else "")),
                ft.DataCell(ft.Text("✓" if rule.mark_aq else "")),
                ft.DataCell(ft.Text("✓" if rule.copy_z_to_ak else "")),
                ft.DataCell(ft.Text(rule.description)),
                ft.DataCell(
                    ft.Row(
                        controls= [
                            ft.IconButton(
                                icon=ft.icons.EDIT_OUTLINED,
                                tooltip="Edit",
                                on_click=lambda _, r=current_rule: on_edit(r),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE,
                                tooltip="Delete",
                                icon_color=ft.colors.ERROR,
                                on_click=lambda _, r=current_rule: on_delete(r.prefix),
                            ),
                        ],
                        tight= True,
                    )
                ),
            ]
        )
        rows.append(row)

    return ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=8,
        vertical_lines=ft.BorderSide(1, ft.colors.OUTLINE_VARIANT),
        horizontal_lines=ft.BorderSide(1, ft.colors.OUTLINE_VARIANT),
    )


def build_settlement_tab(page: ft.Page) -> ft.Container:

    table_container = ft.Column(scroll=ft.ScrollMode.AUTO)

    def refresh_table() -> None:
        rules = get_settlement_rules()
        table_container.controls = [
            build_settlement_table(rules, on_edit, on_delete)
        ]
        table_container.update()

    def on_edit(rule: SettlementRule) -> None:
        open_settlement_dialog(page, rule, on_save=refresh_table)

    def on_delete(prefix: str) -> None:
        delete_settlement_rule(prefix)
        refresh_table()

    def on_add_clicked(event: ft.ControlEvent) -> None:
        open_settlement_dialog(page, None, on_save=refresh_table)

    rules = get_settlement_rules()
    table_container.controls = [
        build_settlement_table(rules, on_edit, on_delete)
    ]

    return ft.Container(
        content= ft.Column(
            controls=[
                ft.ElevatedButton(
                    content= ft.Row(
                        controls= [ft.Icon(ft.icons.ADD), ft.Text("Add Rule")],
                        tight= True,
                    ),
                    on_click= on_add_clicked,
                ),
                table_container,
            ],
            spacing= 12,
            scroll= ft.ScrollMode.AUTO,
        ),
        padding= ft.padding.only(top=20),
    )