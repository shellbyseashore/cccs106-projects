import flet as ft
import mysql.connector
from db_connection import connect_db

def main(page: ft.Page):
    page.title = "User Login"
    page.window.center()
    page.window.frameless = True
    page.window.title_bar_buttons_hidden = True
    page.window.width = 400
    page.window.height = 350
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.Colors.AMBER_ACCENT

    header = ft.Text(
        value="User Login",
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial",
        text_align=ft.TextAlign.CENTER
    )

    user_field = ft.TextField(
        label="User name",
        hint_text="Enter your user name",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        icon=ft.Icons.PERSON,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT
    )

    pass_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your secret key",
        width=300,
        password=True,
        can_reveal_password=True,
        icon=ft.Icons.PASSWORD,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT
    )

    def login_action(e):
        success_dialog = ft.AlertDialog(
            icon=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
            title=ft.Text("Login Successful", text_align=ft.TextAlign.CENTER),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(success_dialog))]
        )

        fail_dialog = ft.AlertDialog(
            icon=ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED),
            title=ft.Text("Login Failed", text_align=ft.TextAlign.CENTER),
            content=ft.Text("Invalid username or password", text_align=ft.TextAlign.CENTER),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(fail_dialog))]
        )

        input_error_dialog = ft.AlertDialog(
            icon=ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE),
            title=ft.Text("Input Error", text_align=ft.TextAlign.CENTER),
            content=ft.Text("Please enter username and password", text_align=ft.TextAlign.CENTER),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(input_error_dialog))]
        )

        db_error_dialog = ft.AlertDialog(
            title=ft.Text("Database Error"),
            content=ft.Text("An error occurred while connecting to the database"),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(db_error_dialog))]
        )

        if not user_field.value or not pass_field.value:
            page.open(input_error_dialog)
            return

        try:
            with connect_db() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM users WHERE username=%s AND password=%s LIMIT 1",
                    (user_field.value, pass_field.value)
                )
                if cur.fetchone():
                    success_dialog.content = ft.Text(f"Welcome, {user_field.value}!", text_align=ft.TextAlign.CENTER)
                    page.open(success_dialog)
                else:
                    page.open(fail_dialog)
            page.update()
        except mysql.connector.Error:
            page.open(db_error_dialog)
            page.update()

    login_btn = ft.ElevatedButton(
        text="Login",
        icon=ft.Icons.LOGIN,
        width=100,
        on_click=login_action
    )

    page.add(
        header,
        ft.Container(ft.Column([user_field, pass_field], spacing=20)),
        ft.Container(login_btn, alignment=ft.alignment.top_right, margin=ft.Margin(0, 20, 40, 0))
    )

ft.app(target=main)
