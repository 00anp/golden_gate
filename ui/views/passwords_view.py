import flet as ft
from ui.services.password_service import load_passwords, save_passwords
from core.models import CompanyPassword

def build_passwords_row(
        cp: CompanyPassword, 
        rows_column: ft.Column,
        on_delete: callable) -> ft.Row:

    company_field = ft.TextField(
        value= cp.company,
        hint_text= "Company name",
        width= 250,
    )
    
    checkbox = ft.Checkbox(
        value= cp.requires_password,
        label= cp.company,
        width= 150,
    )

    password_field = ft.TextField(
        value= cp.password,
        password= True,
        width= 200,
        hint_text= "Password",
    )

    def on_toggle_visibility(event: ft.ControlEvent) -> None:
        password_field.password = not password_field.password

        if password_field.password:
            toggle_btn.icon = ft.icons.VISIBILITY_OFF
        else:
            toggle_btn.icon = ft.icons.VISIBILITY
        
        password_field.update()
        toggle_btn.update()

    toggle_btn = ft.IconButton(
        icon= ft.icons.VISIBILITY_OFF,
        on_click= on_toggle_visibility,
        tooltip= "Show/hide password",
    )

    def on_delete_clicked(event: ft.ControlEvent) -> None:
        on_delete(row)

    delete_btn = ft.IconButton(
        icon= ft.icons.DELETE_OUTLINE,
        on_click= on_delete_clicked,
        tooltip= "Remove company",
        icon_color= ft.colors.ERROR,
    )

    row = ft.Row(
        controls= [
            company_field,
            checkbox,
            password_field,
            toggle_btn,
            delete_btn
        ],
        alignment= ft.MainAxisAlignment.START,
    )

    return row


def build_passwords_view() -> ft.Column:
    passwords: list[CompanyPassword] = load_passwords()

    rows_column = ft.Column(
        spacing= 8,
        scroll= ft.ScrollMode.AUTO,
    )

    status_label = ft.Text(
        value= "",
        color= ft.colors.SECONDARY,
        italic= True,
        size= 13,
    )


    def on_delete_row(row: ft.Row) -> None:
        rows_column.controls.remove(row)
        rows_column.update()

    
    def on_add_company(event: ft.ControlEvent) -> None:
        new_company = CompanyPassword(
            company= "",
            password= "",
            requires_password= False,
        )

        new_row = build_passwords_row(
            cp= new_company,
            rows_column= rows_column,
            on_delete= on_delete_row,
        )

        rows_column.controls.append(new_row)
        rows_column.update()

    
    def on_save_clicked(event: ft.ControlEvent) -> None:
        passwords_to_save: list[CompanyPassword] = []

        for row in rows_column.controls:
            company_field = row.controls[0]
            checkbox = row.controls[1]
            password_field = row.controls[2]

            if company_field.value.strip() != "":
                passwords_to_save.append(CompanyPassword(
                    company= company_field.value.strip(),
                    password= password_field.value.strip(),
                    requires_password= checkbox.value,
                ))
        
        save_passwords(passwords_to_save)
        status_label.value = f"Saved {len(passwords_to_save)} companies."
        status_label.update()


    for cp in passwords:
        row = build_passwords_row(
            cp= cp,
            rows_column= rows_column,
            on_delete= on_delete_row,
        )
        rows_column.controls.append(row)
    
    return ft.Column(
        controls= [
            ft.Text("Password Configuration", size=22, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.ElevatedButton(
                content= ft.Row(
                    controls= [
                        ft.Icon(ft.icons.ADD),
                        ft.Text("Add Company"),
                    ],
                    tight= True,
                ),
                on_click= on_add_company,
            ),

            ft.Divider(height=5, color=ft.colors.TRANSPARENT),

            ft.Row(controls=[
                ft.Text("Company",  width=250, weight=ft.FontWeight.W_500),
                ft.Text("Requires password",   width=250,  weight=ft.FontWeight.W_500),
                ft.Text("Password", width=200, weight=ft.FontWeight.W_500),
            ]),

            rows_column,

            ft.Divider(height=20, color=ft.colors.TRANSPARENT),
            
            ft.ElevatedButton(
                content= ft.Row(
                    controls= [
                        ft.Icon(ft.icons.SAVE),
                        ft.Text("Save"),
                    ],
                    tight= True,
                ),
                on_click= on_save_clicked,
            ),

            status_label,
        ],
        spacing= 12,
        expand= True,
        scroll= ft.ScrollMode.AUTO,
    )