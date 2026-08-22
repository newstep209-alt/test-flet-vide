import flet as ft
def main(page: ft.Page):
    page.title = "TEST VIDE"
    page.bgcolor = "white"
    page.add(ft.Text("CA MARCHE ENFIN", size=40, color="green"))

ft.app(target=main)
