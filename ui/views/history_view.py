import flet as ft
from ui.services.history_service import load_history


def build_history_card(entry: dict) -> ft.Container:

    rules_applied: dict = entry.get("rules_applied", {})
    companies_found: list[str] = entry.get("companies_found", [])
    
    rules_applied_text = ", ".join([f"{prefix}: {count} rows" for prefix, count in rules_applied.items()])
    companies_text = ", ".join(companies_found)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            entry.get("timestamp", ""),
                            weight=ft.FontWeight.W_500,
                            size=14,
                        ),
                        ft.Text(
                            f"{int(entry.get('duration_seconds', 0))}s",
                            color=ft.colors.SECONDARY,
                            size=13,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=5, color=ft.colors.TRANSPARENT),
                ft.Text(
                    f"{entry.get('files_created', 0)} files generated",
                    size=13,
                ),
                ft.Text(
                    f"{companies_text}",
                    size=12,
                    color=ft.colors.SECONDARY,
                ),
                ft.Text(
                    f"{rules_applied_text}",
                    size=12,
                    color=ft.colors.SECONDARY,
                ),
            ],
            spacing=4,
        ),
        padding=16,
        border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
        border_radius=8,
        margin=ft.margin.only(bottom=8),
    )


def build_history_view() -> ft.Column:

    entries: list[dict] = load_history()

    if len(entries) == 0:
        empty_state = ft.Column(
            controls=[
                ft.Icon(ft.icons.HISTORY, size=48, color=ft.colors.SECONDARY),
                ft.Text(
                    "No processing history yet.",
                    color=ft.colors.SECONDARY,
                    size=16,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        )
        return ft.Column(
            controls=[
                ft.Text("Records", size=22, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                empty_state,
            ],
            spacing=12,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    cards = [build_history_card(entry) for entry in entries]

    return ft.Column(
        controls=[
            ft.Text("Records", size=22, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text(
                f"{len(entries)} processed records",
                color=ft.colors.SECONDARY,
                size=13,
                italic=True,
            ),
            ft.Column(
                controls=cards,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                spacing=4,
            ),
        ],
        spacing=12,
        expand=True,
    )