import flet as ft
from ui.services.rules_service import get_settlement_rules, get_payment_tiers
from core.models import SettlementRule, PaymentTier


def build_settlement_table(rules: list[SettlementRule]) -> ft.DataTable:
    columns = [
        ft.DataColumn(ft.Text("Prefix")),
        ft.DataColumn(ft.Text("Threshold"),  numeric=True),
        ft.DataColumn(ft.Text("Z High"),     numeric=True),
        ft.DataColumn(ft.Text("AK High"),    numeric=True),
        ft.DataColumn(ft.Text("Z Low"),      numeric=True),
        ft.DataColumn(ft.Text("AK Low"),     numeric=True),
        ft.DataColumn(ft.Text("Mark AM")),
        ft.DataColumn(ft.Text("Mark AQ")),
        ft.DataColumn(ft.Text("Copy Z→AK")),
        ft.DataColumn(ft.Text("Description")),
    ]

    rows = []
    for rule in rules:
        fila = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(rule.prefix)),
                ft.DataCell(ft.Text(str(rule.balance_threshold))),
                ft.DataCell(ft.Text(str(rule.z_high))),
                ft.DataCell(ft.Text(str(rule.ak_high))),
                ft.DataCell(ft.Text(str(rule.z_low))),
                ft.DataCell(ft.Text(str(rule.ak_low))),
                ft.DataCell(ft.Text("✓" if rule.mark_am     else "")),
                ft.DataCell(ft.Text("✓" if rule.mark_aq     else "")),
                ft.DataCell(ft.Text("✓" if rule.copy_z_to_ak else "")),
                ft.DataCell(ft.Text(rule.description)),
            ]
        )
        rows.append(fila)

    return ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=8,
        vertical_lines=ft.BorderSide(1, ft.colors.OUTLINE_VARIANT),
        horizontal_lines=ft.BorderSide(1, ft.colors.OUTLINE_VARIANT),
    )


def build_tiers_table(tiers: list[PaymentTier]) -> ft.DataTable:
    columns = [
        ft.DataColumn(ft.Text("Min Settlement"),  numeric=True),
        ft.DataColumn(ft.Text("Max Settlement"),  numeric=True),
        ft.DataColumn(ft.Text("Min Payment"),     numeric=True),
        ft.DataColumn(ft.Text("Max Term"),        numeric=True),
        ft.DataColumn(ft.Text("Max Term (LPL)"),  numeric=True),
    ]

    rows = []
    for tier in tiers:

        max_s = "∞" if tier.max_settlement == float("inf") else str(tier.max_settlement)

        fila = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(f"${tier.min_settlement:,.2f}")),
                ft.DataCell(ft.Text(max_s if max_s == "∞" else f"${tier.max_settlement:,.2f}")),
                ft.DataCell(ft.Text(f"${tier.min_payment:,.2f}")),
                ft.DataCell(ft.Text(str(tier.max_term_default))),
                ft.DataCell(ft.Text(str(tier.max_term_lpl))),
            ]
        )
        rows.append(fila)

    return ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=8,
        vertical_lines=ft.BorderSide(1, ft.colors.OUTLINE_VARIANT),
        horizontal_lines=ft.BorderSide(1, ft.colors.OUTLINE_VARIANT),
    )


def build_rules_view() -> ft.Column:

    settlement_rules = get_settlement_rules()
    payment_tiers    = get_payment_tiers()
    settlement_table = build_settlement_table(settlement_rules)
    tiers_table      = build_tiers_table(payment_tiers)

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text="Settlement Rules",
                content=ft.Container(
                    content=ft.Column(
                        controls=[settlement_table],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=ft.padding.only(top=20),
                ),
            ),
            ft.Tab(
                text="Payment Tiers",
                content=ft.Container(
                    content=ft.Column(
                        controls=[tiers_table],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=ft.padding.only(top=20),
                ),
            ),
        ],
        expand=True,
    )

    return ft.Column(
        controls=[
            ft.Text("Business Rules", size=22, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            tabs,
        ],
        spacing=12,
        expand=True,
    )