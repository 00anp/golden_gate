import flet as ft
from core.models import PaymentTier
from core.helpers import safe_float
from ui.services.rules_service import add_payment_tier, update_payment_tier


def open_tiers_dialog(
    page: ft.Page,
    tier: PaymentTier | None,
    index: int | None,
    on_save: callable,
) -> None:

    is_new: bool = tier is None

    min_field = ft.TextField(
        label="Min Settlement",
        value= str(tier.min_settlement) if tier else "0",
        width= 180,
        keyboard_type= ft.KeyboardType.NUMBER,
    )
    max_field = ft.TextField(
        label= "Max Settlement",
        value= "inf" if (tier and tier.max_settlement == float("inf"))
              else (str(tier.max_settlement) if tier else "0"),
        width= 180,
        hint_text= "Use 'inf' for no limit",
        keyboard_type= ft.KeyboardType.NUMBER,
    )
    payment_field = ft.TextField(
        label= "Min Payment",
        value= str(tier.min_payment) if tier else "0",
        width= 180,
        keyboard_type= ft.KeyboardType.NUMBER,
    )
    term_field = ft.TextField(
        label="Max Term (default)",
        value=str(tier.max_term_default) if tier else "12",
        width=180,
        keyboard_type= ft.KeyboardType.NUMBER,
    )
    term_lpl_field = ft.TextField(
        label="Max Term (LPL)",
        value=str(tier.max_term_lpl) if tier else "12",
        width=180,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    def on_save_clicked(event: ft.ControlEvent) -> None:
        max_value = (float("inf") if max_field.value.strip().lower() == "inf"
                     else safe_float(max_field.value))

        new_tier = PaymentTier(
            min_settlement=safe_float(min_field.value),
            max_settlement=max_value,
            min_payment=safe_float(payment_field.value),
            max_term_default=int(safe_float(term_field.value)),
            max_term_lpl=int(safe_float(term_lpl_field.value)),
        )

        if is_new:
            add_payment_tier(new_tier)
        else:
            update_payment_tier(index, new_tier)

        on_save()
        dialog.open = False
        page.update()

    def on_cancel_clicked(event: ft.ControlEvent) -> None:
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal= True,
        title= ft.Text("Add Tier" if is_new else "Edit Payment Tier"),
        content= ft.Column(
            controls=[
                ft.Row(controls=[min_field, max_field]),
                ft.Row(controls=[payment_field, term_field, term_lpl_field]),
            ],
            spacing=16,
            width= 780,
            tight= True,
        ),
        actions= [
            ft.TextButton(text="Cancel", on_click=on_cancel_clicked),
            ft.ElevatedButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.icons.SAVE), ft.Text("Save")],
                    tight=True,
                ),
                on_click=on_save_clicked,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = dialog
    dialog.open = True
    page.update()