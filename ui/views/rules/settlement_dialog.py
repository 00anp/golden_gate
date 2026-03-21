import flet as ft
from core.models  import SettlementRule
from core.helpers import safe_float
from ui.services.rules_service import add_settlement_rule, update_settlement_rule


def open_settlement_dialog(
    page: ft.Page,
    rule: SettlementRule | None,
    on_save: callable,
) -> None:

    is_new: bool = rule is None

    prefix_field = ft.TextField(
        label= "Prefix",
        value= rule.prefix if rule else "",
        width= 150,
    )
    threshold_field = ft.TextField(
        label= "Balance Threshold",
        value= str(rule.balance_threshold) if rule else "0",
        width= 180,
        keyboard_type= ft.KeyboardType.NUMBER,
    )
    z_high_field = ft.TextField(
        label= "Z High", value=str(rule.z_high) if rule else "0.45", width=130,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    ak_high_field = ft.TextField(
        label= "AK High", value=str(rule.ak_high) if rule else "0.40", width=130,
        keyboard_type= ft.KeyboardType.NUMBER,
    )
    z_low_field = ft.TextField(
        label="Z Low", value=str(rule.z_low) if rule else "0.50", width=130,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    ak_low_field = ft.TextField(
        label= "AK Low", value=str(rule.ak_low) if rule else "0.45", width=130,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    description_field = ft.TextField(
        label="Description",
        value=rule.description if rule else "",
        width=420,
    )

    # ── Checkboxes ────────────────────────────────────────────────
    mark_am_check = ft.Checkbox(
        label="Mark AM",
        value=rule.mark_am if rule else False,
    )
    mark_aq_check = ft.Checkbox(
        label="Mark AQ",
        value=rule.mark_aq if rule else False,
    )
    copy_z_check = ft.Checkbox(
        label="Copy Z → AK",
        value=rule.copy_z_to_ak if rule else False,
    )
    z_greater_check = ft.Checkbox(
        label="Z > threshold",
        value=rule.z_greater_than_threshold if rule else False,
    )
    z_lower_check = ft.Checkbox(
        label="Z < threshold",
        value=rule.z_lower_than_threshold if rule else False,
    )


    def on_save_clicked(event: ft.ControlEvent) -> None:

        new_rule = SettlementRule(
            prefix                   = prefix_field.value.strip().upper(),
            balance_threshold        = safe_float(threshold_field.value),
            z_high                   = safe_float(z_high_field.value),
            ak_high                  = safe_float(ak_high_field.value),
            z_low                    = safe_float(z_low_field.value),
            ak_low                   = safe_float(ak_low_field.value),
            mark_am                  = mark_am_check.value,
            mark_aq                  = mark_aq_check.value,
            copy_z_to_ak             = copy_z_check.value,
            z_greater_than_threshold = z_greater_check.value,
            z_lower_than_threshold   = z_lower_check.value,
            description              = description_field.value.strip(),
        )

        # Save to rules.json
        if is_new:
            add_settlement_rule(new_rule)
        else:
            update_settlement_rule(new_rule)

        on_save()
        dialog.open = False
        page.update()


    def on_cancel_clicked(event: ft.ControlEvent) -> None:
        dialog.open = False
        page.update()


    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Add Rule" if is_new else f"Edit Rule — {rule.prefix}"),
        content=ft.Column(
            controls=[
                ft.Row(controls=[prefix_field, threshold_field]),
                ft.Row(controls=[z_high_field, ak_high_field, z_low_field, ak_low_field]),
                ft.Row(controls=[mark_am_check, mark_aq_check, copy_z_check,
                                 z_greater_check, z_lower_check]),
                description_field,
            ],
            spacing= 16,
            width= 780,
            tight=True,
        ),
        actions=[
            ft.TextButton(text="Cancel", on_click=on_cancel_clicked),
            ft.ElevatedButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.icons.SAVE), ft.Text("Save")],
                    tight=True,
                ),
                on_click= on_save_clicked,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = dialog
    dialog.open = True
    page.update()