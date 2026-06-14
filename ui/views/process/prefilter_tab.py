import flet as ft
from core.filter_engine import get_all_flagged_rows, get_row_preview

PAGE_SIZE_OPTIONS = [25, 50]
DEFAULT_PAGE_SIZE = 25


def build_section(
    title:          str,
    description:    str,
    previews:       list[dict],
    checked_rows:   set[int],          # shared mutable set across all sections
    on_toggle:      callable,          # on_toggle(row_index, is_checked)
    show_select_all: bool = False,     # opt-in: show the "Select all" menu
    on_bulk_change: callable = None,   # called once after a bulk op (optional)
) -> ft.Column:
    """Builds one paginated section with a DataTable of flagged rows.
    Each row has a Checkbox + company + status + balance + customer + dates.
    Checkbox state survives page changes because it is read back from
    `checked_rows` every time the table is rebuilt.

    When `show_select_all` is True, a popup menu is added next to the
    pagination controls offering: select current page, select every page,
    or clear this section's selection."""

    if not previews:
        return ft.Column(controls=[
            ft.Text(title, weight=ft.FontWeight.BOLD, size=15),
            ft.Text("No rows found for this criterion.", italic=True, color=ft.colors.SECONDARY),
        ])

    total           = len(previews)
    section_row_ids = {p["row"] for p in previews}   # only this section's rows
    state           = {"page": 0, "page_size": DEFAULT_PAGE_SIZE}

    table_holder = ft.Column()
    info_label   = ft.Text(italic=True, color=ft.colors.SECONDARY, size=12)

    def total_pages() -> int:
        return max(1, (total + state["page_size"] - 1) // state["page_size"])

    def current_page_row_ids() -> set[int]:
        start = state["page"] * state["page_size"]
        end   = start + state["page_size"]
        return {p["row"] for p in previews[start:end]}

    def build_table_for_page() -> ft.DataTable:
        start = state["page"] * state["page_size"]
        end   = start + state["page_size"]
        page_previews = previews[start:end]

        rows = []
        for preview in page_previews:
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

        return ft.DataTable(
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

    prev_btn = ft.IconButton(icon=ft.icons.CHEVRON_LEFT,  tooltip="Previous page")
    next_btn = ft.IconButton(icon=ft.icons.CHEVRON_RIGHT, tooltip="Next page")

    page_size_dropdown = ft.Dropdown(
        width=110,
        value=str(DEFAULT_PAGE_SIZE),
        options=[ft.dropdown.Option(str(n), f"{n} / page") for n in PAGE_SIZE_OPTIONS],
    )

    def render() -> None:
        """Rebuilds the visible page WITHOUT calling .update().
        Safe during the initial build (control not yet on the page)."""
        table_holder.controls = [build_table_for_page()]

        start = state["page"] * state["page_size"] + 1
        end   = min((state["page"] + 1) * state["page_size"], total)
        info_label.value = (
            f"Showing {start}-{end} of {total}  ·  "
            f"Page {state['page'] + 1} of {total_pages()}"
        )
        prev_btn.disabled = state["page"] <= 0
        next_btn.disabled = state["page"] >= total_pages() - 1

    def push_updates() -> None:
        """Pushes the rebuilt page to the UI (event-driven only)."""
        table_holder.update()
        info_label.update()
        prev_btn.update()
        next_btn.update()

    def on_prev(event: ft.ControlEvent) -> None:
        if state["page"] > 0:
            state["page"] -= 1
            render()
            push_updates()

    def on_next(event: ft.ControlEvent) -> None:
        if state["page"] < total_pages() - 1:
            state["page"] += 1
            render()
            push_updates()

    def on_page_size_changed(event: ft.ControlEvent) -> None:
        state["page_size"] = int(page_size_dropdown.value)
        state["page"]      = 0
        render()
        push_updates()

    prev_btn.on_click            = on_prev
    next_btn.on_click            = on_next
    page_size_dropdown.on_change = on_page_size_changed

    # ── Bulk selection helpers ────────────────────────────────────
    def _apply_bulk(target_ids: set[int], add: bool) -> None:
        if add:
            checked_rows.update(target_ids)
        else:
            checked_rows.difference_update(target_ids)
        render()
        push_updates()
        if on_bulk_change is not None:
            on_bulk_change()

    def on_select_page(event: ft.ControlEvent) -> None:
        _apply_bulk(current_page_row_ids(), add=True)

    def on_select_all_pages(event: ft.ControlEvent) -> None:
        _apply_bulk(section_row_ids, add=True)

    def on_clear_selection(event: ft.ControlEvent) -> None:
        _apply_bulk(section_row_ids, add=False)

    select_all_menu = ft.PopupMenuButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.icons.CHECKLIST, size=18),
                ft.Text("Select all"),
                ft.Icon(ft.icons.ARROW_DROP_DOWN, size=18),
            ],
            tight=True,
        ),
        items=[
            ft.PopupMenuItem(text="This page only",            on_click=on_select_page),
            ft.PopupMenuItem(text=f"All pages ({total} rows)", on_click=on_select_all_pages),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(text="Clear selection",           on_click=on_clear_selection),
        ],
    )

    # Initial render — no .update() (control not attached to the page yet)
    render()

    left_controls = [page_size_dropdown]
    if show_select_all:
        left_controls.append(select_all_menu)

    pagination_bar = ft.Row(
        controls=[
            ft.Row(controls=left_controls, tight=True, spacing=12),
            ft.Row(controls=[prev_btn, info_label, next_btn], tight=True),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    return ft.Column(controls=[
        ft.Text(title, weight=ft.FontWeight.BOLD, size=15),
        ft.Text(f"{description} ({total} rows)", italic=True, color=ft.colors.SECONDARY),
        pagination_bar,
        table_holder,
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

    def _refresh_summary() -> None:
        summary_label.value = f"{len(rows_to_remove)} rows marked for removal"

    def on_toggle(row_index: int, is_checked: bool) -> None:
        if is_checked:
            rows_to_remove.add(row_index)
        else:
            rows_to_remove.discard(row_index)
        _refresh_summary()
        summary_label.update()

    def on_bulk_change() -> None:
        """Called once after a bulk select/clear operation."""
        _refresh_summary()
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
        show_select_all=True,
        on_bulk_change=on_bulk_change,
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