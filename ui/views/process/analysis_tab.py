import flet as ft
from core.filter_engine import get_prefix_analysis
from core.rules_engine import load_rules
from ui.views.rules.settlement_dialog import open_settlement_dialog
from core.models import SettlementRule
from core.helpers import safe_str

COL_CUSTOMER = 17   # Q — gmc_customer


def build_analysis_tab(
    page:           ft.Page,
    ws,
    rows_to_remove: set[int],       # already accumulated from prefilter_tab
    on_process:     callable,       # on_process(final_rows_to_remove: set[int])
) -> ft.Container:
    """Builds the Analysis tab showing unique prefixes, rule coverage, and exclusions."""

    settlement_rules, _ = load_rules()
    analysis = get_prefix_analysis(ws, settlement_rules)

    # Local exclusion set: prefixes chosen to exclude here
    local_excluded_prefixes: set[str] = set()
    status_label = ft.Text(value="", italic=True, color=ft.colors.SECONDARY)

    def build_table(analysis_data: list[dict]) -> ft.DataTable:
        rows = []
        for entry in analysis_data:
            prefix     = entry["prefix"]
            count      = entry["count"]
            has_rule   = entry["has_rule"]
            rule_label = entry["rule_prefix"] if has_rule else "—"
            rule_color = ft.colors.GREEN if has_rule else ft.colors.ERROR

            is_excluded = prefix in local_excluded_prefixes

            exclude_btn = ft.ElevatedButton(
                text=("Excluded" if is_excluded else "Exclude"),
                disabled=is_excluded,
                icon=(ft.icons.BLOCK if is_excluded else ft.icons.REMOVE_CIRCLE_OUTLINE),
                on_click=lambda _, p=prefix: on_exclude_prefix(p),
            )

            add_rule_btn = ft.ElevatedButton(
                text="Add Rule",
                icon=ft.icons.ADD,
                disabled=has_rule,
                on_click=lambda _, p=prefix: on_add_rule(p),
            )

            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(prefix)),
                ft.DataCell(ft.Text(str(count))),
                ft.DataCell(ft.Text(rule_label, color=rule_color)),
                ft.DataCell(ft.Row(controls=[exclude_btn, add_rule_btn], tight=True)),
            ]))

        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Prefix")),
                ft.DataColumn(ft.Text("Occurrences"), numeric=True),
                ft.DataColumn(ft.Text("Matched Rule")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=rows,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=8,
            divider_thickness=1,
        )

    table_container = ft.Column(scroll=ft.ScrollMode.AUTO)
    table_container.controls = [build_table(analysis)]

    def refresh_table() -> None:
        table_container.controls = [build_table(analysis)]
        table_container.update()

    def on_exclude_prefix(prefix: str) -> None:
        local_excluded_prefixes.add(prefix)
        count = sum(
            1 for i in range(2, ws.max_row + 1)
            if safe_str(ws.cell(i, COL_CUSTOMER).value) == prefix
        )
        status_label.value = f"Prefix {prefix} excluded ({count} rows will be removed)"
        status_label.update()
        refresh_table()

    def on_add_rule(prefix: str) -> None:
        blank_rule = SettlementRule(
            prefix=prefix,
            balance_threshold=0,
            z_high=0.0,
            ak_high=0.0,
            z_low=0.0,
            ak_low=0.0,
        )
        open_settlement_dialog(page, blank_rule, on_save=on_rule_saved)

    def on_rule_saved() -> None:
        nonlocal analysis, settlement_rules
        settlement_rules, _ = load_rules()
        analysis = get_prefix_analysis(ws, settlement_rules)
        refresh_table()

    def on_process_clicked(event: ft.ControlEvent) -> None:
        extra_rows: set[int] = set()
        for i in range(2, ws.max_row + 1):
            prefix = safe_str(ws.cell(i, COL_CUSTOMER).value)
            if prefix in local_excluded_prefixes:
                extra_rows.add(i)
        final_rows = rows_to_remove | extra_rows
        on_process(final_rows)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Analysis — Prefix Review", size=22, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(
                    f"{len(analysis)} unique prefixes found",
                    italic=True,
                    color=ft.colors.SECONDARY,
                ),
                status_label,
                table_container,
                ft.Divider(),
                ft.ElevatedButton(
                    content=ft.Row(
                        controls=[ft.Icon(ft.icons.PLAY_ARROW), ft.Text("Process File")],
                        tight=True,
                    ),
                    on_click=on_process_clicked,
                ),
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
    )