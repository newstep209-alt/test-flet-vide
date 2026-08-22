import flet as ft

def main(page: ft.Page):
    page.title = "TEST VIDE - ENFIN"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.add(
        ft.Icon(ft.icons.CHECK_CIRCLE, size=80, color=ft.colors.GREEN),
        ft.Text("CA MARCHE ENFIN !!!", size=30, weight=ft.FontWeight.BOLD),
        ft.Text("L'ancien repo était maudit 😂", size=16),
        ft.ElevatedButton("Clique moi", on_click=lambda e: page.add(ft.Text("Bouton marche !")))
    )

ft.app(target=main)
