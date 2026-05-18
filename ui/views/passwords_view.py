import flet as ft
from ui.services.password_service import load_passwords, save_passwords
from core.models import (
    CompanyPassword,
    DELIVERY_REQUIRES_PASSWORD,
    DELIVERY_SFTP,
    DELIVERY_SFTP_WITH_PASSWORD,
)

DELIVERY_OPTIONS = [
    ft.dropdown.Option(key=DELIVERY_REQUIRES_PASSWORD,  text="Requires Password"),
    ft.dropdown.Option(key=DELIVERY_SFTP,               text="SFTP"),
    ft.dropdown.Option(key=DELIVERY_SFTP_WITH_PASSWORD, text="SFTP with Password"),
]


def build_password_row(cp: CompanyPassword, on_delete: callable) -> ft.Row:
    """Builds a single company password row with company name, delivery method
    dropdown, password field, visibility toggle, and delete button."""

    company_field = ft.TextField(
        value=cp.company,
        hint_text="Company name",
        width=200,
    )

    delivery_dropdown = ft.Dropdown(
        value=cp.delivery_method,
        options=DELIVERY_OPTIONS,
        width=220,
    )

    needs_pwd = cp.delivery_method in {DELIVERY_REQUIRES_PASSWORD, DELIVERY_SFTP_WITH_PASSWORD}

    password_field = ft.TextField(
        value=cp.password,
        password=True,
        width=200,
        hint_text="Password",
        visible=needs_pwd,
    )

    toggle_btn = ft.IconButton(
        icon=ft.icons.VISIBILITY_OFF,
        tooltip="Show/hide password",
        visible=needs_pwd,
    )

    def on_delivery_changed(event: ft.ControlEvent) -> None:
        method = delivery_dropdown.value
        needs_password = method in {DELIVERY_REQUIRES_PASSWORD, DELIVERY_SFTP_WITH_PASSWORD}
        password_field.visible = needs_password
        toggle_btn.visible     = needs_password
        password_field.update()
        toggle_btn.update()

    delivery_dropdown.on_change = on_delivery_changed

    def on_toggle_visibility(event: ft.ControlEvent) -> None:
        password_field.password = not password_field.password
        toggle_btn.icon = (
            ft.icons.VISIBILITY_OFF if password_field.password else ft.icons.VISIBILITY
        )
        password_field.update()
        toggle_btn.update()

    toggle_btn.on_click = on_toggle_visibility

    delete_btn = ft.IconButton(
        icon=ft.icons.DELETE_OUTLINE,
        icon_color=ft.colors.ERROR,
        on_click=lambda _: on_delete(row),
    )

    row = ft.Row(controls=[company_field, delivery_dropdown, password_field, toggle_btn, delete_btn])
    return row


def build_passwords_view() -> ft.Column:
    """Builds the Password Configuration view with add, delete, and save support."""

    passwords    = load_passwords()
    rows_column  = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    status_label = ft.Text(value="", italic=True, color=ft.colors.SECONDARY)

    def on_delete_row(row: ft.Row) -> None:
        rows_column.controls.remove(row)
        rows_column.update()

    def on_add_company(event: ft.ControlEvent) -> None:
        new_cp = CompanyPassword(
            company="",
            requires_password=True,
            delivery_method=DELIVERY_REQUIRES_PASSWORD,
        )
        rows_column.controls.append(build_password_row(new_cp, on_delete_row))
        rows_column.update()

    def on_save_clicked(event: ft.ControlEvent) -> None:
        to_save = []
        for row in rows_column.controls:
            company_field     = row.controls[0]
            delivery_dropdown = row.controls[1]
            password_field    = row.controls[2]
            if company_field.value.strip():
                method = delivery_dropdown.value
                to_save.append(CompanyPassword(
                    company=company_field.value.strip(),
                    password=password_field.value.strip(),
                    requires_password=True,
                    delivery_method=method,
                ))
        save_passwords(to_save)
        status_label.value = f"Saved {len(to_save)} companies."
        status_label.update()

    # Populate existing rows
    for cp in passwords:
        rows_column.controls.append(build_password_row(cp, on_delete_row))

    return ft.Column(
        controls=[
            ft.Text("Password Configuration", size=22, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text(
                "All files are protected by default. Configure exceptions below.",
                italic=True,
                color=ft.colors.SECONDARY,
            ),
            ft.ElevatedButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.icons.ADD), ft.Text("Add Company")],
                    tight=True,
                ),
                on_click=on_add_company,
            ),
            ft.Row(
                controls=[
                    ft.Text("Company",         weight=ft.FontWeight.W_500, width=200),
                    ft.Text("Delivery Method", weight=ft.FontWeight.W_500, width=220),
                    ft.Text("Password",        weight=ft.FontWeight.W_500, width=200),
                ],
            ),
            rows_column,
            ft.ElevatedButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.icons.SAVE), ft.Text("Save")],
                    tight=True,
                ),
                on_click=on_save_clicked,
                style=ft.ButtonStyle(
                    padding=ft.padding.symmetric(horizontal=30, vertical=15)
                ),
            ),
            status_label,
        ],
        spacing=12,
        expand=True,
    )