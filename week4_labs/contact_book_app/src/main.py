import flet as ft
from database import init_db
from app_logic import add_contact, load_contacts

def main(page: ft.Page):
    page.title = "Contact Book"
    page.window.width = 1000
    page.window.height = 700
    page.window.center()

    db_conn = init_db()

    # Refs for inputs
    name_field = ft.Ref[ft.TextField]()
    phone_field = ft.Ref[ft.TextField]()
    email_field = ft.Ref[ft.TextField]()

    contacts_list_view = ft.ListView(expand=True, spacing=10, padding=10)

    # Search bar
    search_input = ft.TextField(
        hint_text="Search Contact",
        prefix_icon=ft.Icons.SEARCH,
        width=250,
        border_radius=20,
        border_color="black",
        on_change=lambda e: load_contacts(db_conn, contacts_list_view, search_input.value),
    )

    # Dark mode switch
    def toggle_dark_mode(e):
        page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        apply_textfield_styles_for_theme()
        page.update()

    dark_mode_switch = ft.Switch(label="Dark Mode", on_change=toggle_dark_mode)

    # Ensure TextFields have appropriate borders in current theme
    def apply_textfield_styles_for_theme():
        is_dark = page.theme_mode == ft.ThemeMode.DARK
        border = "white" if is_dark else "black"
        # Update search field
        try:
            search_input.border_color = border
        except Exception:
            pass
        # Update form fields
        for tf_ref in (name_field, phone_field, email_field):
            if tf_ref.current is not None:
                tf_ref.current.border_color = border
                tf_ref.current.focused_border_color = border
                tf_ref.current.update()

    # Live validation: clear name error when user types a non-empty value
    def on_name_change(e):
        if name_field.current and name_field.current.value and name_field.current.error_text:
            name_field.current.error_text = None
            name_field.current.update()

    # Phone: enforce digits-only
    def on_phone_change(e):
        if phone_field.current is None:
            return
        value = phone_field.current.value or ""
        digits_only = "".join(ch for ch in value if ch.isdigit())
        if value != digits_only:
            phone_field.current.value = digits_only
            phone_field.current.update()

    # Email row + Add button
    add_contact_row = ft.Row(
        [
            ft.Container(
                content=ft.ElevatedButton(
                    "Add Contact",
                    on_click=lambda e: add_contact(
                        name_field.current.value,
                        phone_field.current.value,
                        email_field.current.value,
                        db_conn,
                        contacts_list_view,
                        name_field,
                        phone_field,
                        email_field,
                        page,
                    ),
                    style=ft.ButtonStyle(
                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                        shape=ft.RoundedRectangleBorder(radius=20),
                    ),
                ),
                alignment=ft.alignment.center_right,
                width=400,  # increases container width → shifts button right
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Layout
    page.add(
        # Top bar
        ft.Row(
            [
                search_input,
                ft.Container(dark_mode_switch, padding=ft.padding.only(left=12)),
            ],
            alignment=ft.MainAxisAlignment.END,
        ),

        # Centered form
        ft.Column(
            [
                ft.Text("Enter Contact Details", size=20, weight="bold"),
                ft.TextField(
                    ref=name_field,
                    label="Name",
                    width=400,
                    height=55,
                    on_change=on_name_change,
                    suffix_text="*",
                    hint_text="Required",
                ),
                ft.TextField(
                    ref=phone_field,
                    label="Phone",
                    width=400,
                    height=55,
                    keyboard_type=ft.KeyboardType.PHONE,
                    on_change=on_phone_change,
                ),
                ft.TextField(ref=email_field, label="Email", width=400, height=55),
                add_contact_row,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        ),

        ft.Text("Contacts:", size=18, weight="bold"),
        contacts_list_view,
    )

    # Apply theme-based styles once UI is constructed
    apply_textfield_styles_for_theme()

    load_contacts(db_conn, contacts_list_view)

if __name__ == "__main__":
    ft.app(target=main)
