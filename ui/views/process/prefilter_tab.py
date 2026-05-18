import flet as ft
from core.filter_engine import get_all_flagged_rows, get_row_preview


def build_section(
    title:        str,
    description:  str,
    previews:     list[dict],
    checked_rows: set[int],    # shared mutable set across all sections
    on_toggle:    callable,    # on_toggle(row_index, is_checked)
) -> ft.Column:
    """Builds one section with a DataTable of flagged rows.
    Each row has a Checkbox + company + status + balance + customer + dates."""

    if not previews:
        return ft.Column(controls=[
            ft.Text(title, weight=ft.FontWeight.BOLD),
            ft.Text("No rows found for this criterion.", italic=True, color=ft.colors.SECONDARY),
        ])

    rows = []
    for preview in previews:
        row_index = preview["row"]
        checkbox = ft.Checkbox(
            value=row_index in checked_rows,
            on_change=lambda e, r=row_index: on_toggle(r, e.control.value),
        )
        lastpaid = preview["lastpaid"]
        nsfdate  = preview["nsfdate"]
        rows.append(ft.DataRow(cells=[
            ft.DataCell(checkbox),
            ft.DataCell(ft.Text(preview["company"])),
            ft.DataCell(ft.Text(preview["status"])),
            ft.DataCell(ft.Text(f"{preview['balance']:.2f}")),
            ft.DataCell(ft.Text(preview["customer"])),
            ft.DataCell(ft.Text(str(lastpaid.date()) if hasattr(lastpaid, "date") else str(lastpaid or ""))),
            ft.DataCell(ft.Text(str(nsfdate.date()) if hasattr(nsfdate, "date") else str(nsfdate or ""))),
        ]))

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Remove")),
            ft.DataColumn(ft.Text("Company")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Balance"), numeric=True),
            ft.DataColumn(ft.Text("Customer")),
            ft.DataColumn(ft.Text("Last Paid")),
            ft.DataColumn(ft.Text("NSF Date")),
        ],
        rows=rows,
        border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
        border_radius=8,
        divider_thickness=1,
    )

    return ft.Column(controls=[
        ft.Text(title, weight=ft.FontWeight.BOLD, size=15),
        ft.Text(f"{description} ({len(previews)} rows)", italic=True, color=ft.colors.SECONDARY),
        table,
    ])


def build_prefilter_tab(
    ws,
    on_next: callable,   # on_next(rows_to_remove: set[int])
) -> ft.Container:
    """Builds the Prefilter tab with PDC/PCC, PRM/PPA, and Low Balance sections."""

    flagged        = get_all_flagged_rows(ws)
    rows_to_remove = set()   # mutable, shared across sections

    pdc_pcc_previews = [get_row_preview(ws, r) for r in flagged["pdc_pcc"]]
    prm_ppa_previews = [get_row_preview(ws, r) for r in flagged["prm_ppa"]]
    low_bal_previews = [get_row_preview(ws, r) for r in flagged["low_balance"]]

    summary_label = ft.Text(value="", italic=True, color=ft.colors.SECONDARY)

    def on_toggle(row_index: int, is_checked: bool) -> None:
        if is_checked:
            rows_to_remove.add(row_index)
        else:
            rows_to_remove.discard(row_index)
        summary_label.value = f"{len(rows_to_remove)} rows marked for removal"
        summary_label.update()

    section_pdc_pcc = build_section(
        "PDC / PCC", "Rows with status PDC or PCC",
        pdc_pcc_previews, rows_to_remove, on_toggle,
    )
    section_prm_ppa = build_section(
        "PRM / PPA", "Active payment within last 31 days",
        prm_ppa_previews, rows_to_remove, on_toggle,
    )
    section_low_bal = build_section(
        "Low Balance", "Rows with balance under $100",
        low_bal_previews, rows_to_remove, on_toggle,
    )

    def on_next_clicked(event: ft.ControlEvent) -> None:
        on_next(rows_to_remove)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Review — Flagged Rows", size=22, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                summary_label,
                section_pdc_pcc,
                ft.Divider(),
                section_prm_ppa,
                ft.Divider(),
                section_low_bal,
                ft.Divider(),
                ft.ElevatedButton(
                    content=ft.Row(
                        controls=[ft.Icon(ft.icons.ARROW_FORWARD), ft.Text("Next →")],
                        tight=True,
                    ),
                    on_click=on_next_clicked,
                ),
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
    )