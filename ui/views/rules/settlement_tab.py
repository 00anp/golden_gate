import flet as ft
from ui.services.rules_service import get_settlement_rules, delete_settlement_rule, update_settlement_rule
from ui.views.rules.settlement_dialog import open_settlement_dialog
from core.models import SettlementRule

# Renamed column headers
COLUMN_HEADERS = [
    "Enabled",
    "Prefix",
    "Threshold",
    "SIF High",
    "Lump Sum High",
    "SIF Low",
    "Lump Sum Low",
    "Prelit",
    "Precharge Off",
    "Copy SIF→Lump Sum",
    "Description",
    "Actions",
]


def build_settlement_table(
    rules: list[SettlementRule],
    sort_ascending: bool,
    on_edit: callable,
    on_delete: callable,
    on_toggle: callable,
    on_sort_toggled: callable,
) -> ft.DataTable:
    """Builds the settlement rules DataTable with sort, toggle, edit, delete."""

    sorted_rules = sorted(rules, key=lambda r: r.prefix, reverse=not sort_ascending)

    columns = [ft.DataColumn(ft.Text(h)) for h in COLUMN_HEADERS]

    # Prefix column with sort indicator
    columns[1] = ft.DataColumn(
        ft.Row(
            controls=[
                ft.Text("Prefix"),
                ft.Icon(
                    ft.icons.ARROW_UPWARD if sort_ascending else ft.icons.ARROW_DOWNWARD,
                    size=16,
                ),
            ],
            tight=True,
        ),
        on_sort=lambda _: on_sort_toggled(),
    )

    rows = []
    for rule in sorted_rules:
        enabled_checkbox = ft.Checkbox(
            value=rule.enabled,
            on_change=lambda e, p=rule.prefix: on_toggle(p, e.control.value),
        )
        rows.append(ft.DataRow(cells=[
            ft.DataCell(enabled_checkbox),
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
            ft.DataCell(ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.icons.EDIT_OUTLINED,
                        on_click=lambda _, r=rule: on_edit(r),
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        icon_color=ft.colors.ERROR,
                        on_click=lambda _, r=rule: on_delete(r.prefix),
                    ),
                ],
                tight=True,
            )),
        ]))

    return ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
        border_radius=8,
        divider_thickness=1,
    )


def build_settlement_tab(page: ft.Page) -> ft.Container:
    """Builds the settlement rules tab with search, sort, add, edit, delete, and toggle."""

    sort_ascending = [True]    # mutable state via single-element list

    search_field = ft.TextField(
        hint_text="Search by prefix...",
        prefix_icon=ft.icons.SEARCH,
        width=300,
        on_change=lambda _: refresh_table(),
    )

    table_container = ft.Column(scroll=ft.ScrollMode.AUTO)

    def get_filtered_rules() -> list[SettlementRule]:
        all_rules = get_settlement_rules()
        query = search_field.value.strip().upper()
        if not query:
            return all_rules
        return [r for r in all_rules if query in r.prefix.upper()]

    def refresh_table() -> None:
        rules = get_filtered_rules()
        table_container.controls = [
            build_settlement_table(
                rules, sort_ascending[0], on_edit, on_delete, on_toggle, on_sort_toggled
            )
        ]
        table_container.update()

    def on_sort_toggled() -> None:
        sort_ascending[0] = not sort_ascending[0]
        refresh_table()

    def on_edit(rule: SettlementRule) -> None:
        open_settlement_dialog(page, rule, on_save=refresh_table)

    def on_delete(prefix: str) -> None:
        delete_settlement_rule(prefix)
        refresh_table()

    def on_toggle(prefix: str, new_value: bool) -> None:
        all_rules = get_settlement_rules()
        for rule in all_rules:
            if rule.prefix == prefix:
                rule.enabled = new_value
                update_settlement_rule(rule)
                break
        # No UI refresh needed — checkbox already reflects the new state

    def on_add_clicked(event: ft.ControlEvent) -> None:
        open_settlement_dialog(page, None, on_save=refresh_table)

    # Initial load
    refresh_table()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            content=ft.Row(
                                controls=[ft.Icon(ft.icons.ADD), ft.Text("Add Rule")],
                                tight=True,
                            ),
                            on_click=on_add_clicked,
                        ),
                        search_field,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                table_container,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.only(top=20),
    )