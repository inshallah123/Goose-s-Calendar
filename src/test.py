import flet as ft
from viewmodels import PageViewModel
from src.view import PageView


def main(page: ft.Page):
    viewmodel = PageViewModel()
    viewmodel.title = "goose's calendar"
    viewmodel.width = 800
    viewmodel.height = 600
    viewmodel.bgcolor = "#f0f8ff"

    page_view = PageView(page, viewmodel)
    
    def on_button_click():
        viewmodel.bgcolor = "#99e3f2" if viewmodel.bgcolor == "#f0f8ff" else "#f0f8ff"

    content = ft.Column([
        ft.Text("MVVM Architecture Test", size=20),
        ft.Text("Click button to test ViewModel reactive updates"),
        ft.Row([
            ft.ElevatedButton("Toggle Background", on_click=on_button_click),
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Text("", size=10),
    ], alignment=ft.MainAxisAlignment.CENTER)
    
    page_view.set_content_container(content)
    page.add(content)


if __name__ == "__main__":
    ft.run(main)