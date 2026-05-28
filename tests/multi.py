import flet as ft


def main(page: ft.Page):
    def button_click(e, custom_param):
        print(f"点击了按钮，参数：{custom_param}")
        page.add(ft.Text(f"参数值: {custom_param}"))

    # 使用 lambda 传递额外参数
    btn1 = ft.Button("按钮1", on_click=lambda e: button_click(e, "参数1"))

    btn2 = ft.Button("按钮2", on_click=lambda e: button_click(e, "参数2"))

    page.add(btn1, btn2)


ft.app(target=main)
