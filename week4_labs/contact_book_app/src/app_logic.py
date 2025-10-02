import flet as ft
from database import insert_contact_db, get_all_contacts_db, delete_contact_db

# Robust snackbar helper supporting multiple Flet API variants
def show_snack(page: ft.Page, message: str):
    if page is None:
        return
    try:
        # Newer API
        page.show_snack_bar(ft.SnackBar(ft.Text(message)))
        return
    except Exception:
        pass
    try:
        # Some versions expose open_snack_bar
        page.open_snack_bar(ft.SnackBar(ft.Text(message)))
        return
    except Exception:
        pass
    # Fallback to property
    page.snack_bar = ft.SnackBar(ft.Text(message))
    page.snack_bar.open = True
    page.update()

# Add contact with validation
def add_contact(name, phone, email, db_conn, contacts_list_view, name_ref, phone_ref, email_ref, page=None):
    if not name.strip():
        name_ref.current.error_text = "Name cannot be empty"
        name_ref.current.update()
        return

    insert_contact_db(db_conn, name, phone, email)
    name_ref.current.value = ""
    phone_ref.current.value = ""
    email_ref.current.value = ""
    name_ref.current.error_text = None
    # reflect cleared values in UI
    if name_ref.current:
        name_ref.current.update()
    if phone_ref.current:
        phone_ref.current.update()
    if email_ref.current:
        email_ref.current.update()

    load_contacts(db_conn, contacts_list_view)

    # Feedback to user
    page = page or getattr(contacts_list_view, "page", None)
    show_snack(page, "Contact added successfully")

# Display contacts
def load_contacts(db_conn, contacts_list_view, search_term=""):
    contacts = get_all_contacts_db(db_conn, search_term)
    contacts_list_view.controls.clear()

    for contact in contacts:
        contact_id, name, phone, email = contact

        # define click handler explicitly to avoid lambda capture edge cases
        def on_delete_click(e, cid=contact_id):
            # quick feedback to verify click handler is firing
            page = getattr(contacts_list_view, "page", None) or getattr(e, "page", None)
            if page is not None:
                page.snack_bar = ft.SnackBar(ft.Text("Preparing delete..."), open=True)
                page.update()
            confirm_delete(db_conn, cid, contacts_list_view)

        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(name, weight="bold", size=16),
                        ft.Row([ft.Icon(ft.Icons.PHONE), ft.Text(phone or "—")]),
                        ft.Row([ft.Icon(ft.Icons.EMAIL), ft.Text(email or "—")]),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Delete",
                                    bgcolor="red",
                                    color="white",
                                    on_click=on_delete_click,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                    ],
                    spacing=5,
                ),
                padding=15,
            ),
            elevation=2,
        )

        contacts_list_view.controls.append(card)

    contacts_list_view.update()

# Confirmation before deleting
def confirm_delete(db_conn, contact_id, contacts_list_view):
    # normalize id
    try:
        contact_id = int(contact_id)
    except Exception:
        pass
    # Try to get page from the list view to avoid relying on event.page
    page = getattr(contacts_list_view, "page", None)

    # If page is missing (unexpected), perform delete directly as a fallback
    if page is None:
        delete_contact_db(db_conn, contact_id)
        load_contacts(db_conn, contacts_list_view)
        return

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Delete"),
        content=ft.Text("Are you sure you want to delete this contact?"),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # ✅ define handlers AFTER dialog so they can reference it
    def yes_delete(e):
        try:
            deleted = delete_contact_db(db_conn, contact_id)
            load_contacts(db_conn, contacts_list_view)
            dialog.open = False
            if deleted > 0:
                page.snack_bar = ft.SnackBar(ft.Text("Contact deleted"), open=True)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Contact not found"), open=True)
            page.update()
        except Exception as ex:
            dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text(f"Delete failed: {ex}"), open=True)
            page.update()

    def no_cancel(e):
        dialog.open = False
        page.update()

    dialog.actions = [
        ft.TextButton("Yes", on_click=yes_delete),
        ft.TextButton("No", on_click=no_cancel),
    ]

    # Try multiple strategies to open the dialog
    page.dialog = dialog
    try:
        page.overlay.append(dialog)
    except Exception:
        pass
    dialog.open = True
    page.update()
