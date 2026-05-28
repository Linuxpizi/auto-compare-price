import flet as ft

from src.db.db import DBConn
from src.api.api import Playwright


@ft.component
def Crawler(db: DBConn, playwright: Playwright) -> ft.Column:

    async def handle_start_crawler(e):
        if sku := await db.get_random_sku():
            print("开始采集")

            # 1. 打开 SKU
            await playwright.goto_link_page(sku.sku_link)


            await db.modify_sku_status(sku.sku_link)  # 更新状态为正在比价
        else:
            print("没有待比价的 SKU 了")

    async def handle_stop_crawler(e):
        print("停止采集")

    async def handle_login_1688(e):
        print("登录1688")

    async def handle_check_login_1688(e):
        print("验证登录状态")

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Button("开始采集", on_click=handle_start_crawler),
                    ft.Button("停止采集", on_click=handle_stop_crawler),
                ],
                spacing=10,
            ),
            ft.Row(
                controls=[
                    ft.Button("登录1688", on_click=handle_login_1688),
                    ft.Button("验证登录状态", on_click=handle_check_login_1688),
                ],
                spacing=10,
            ),  # 登录 1688
        ],
        spacing=10,
        margin=10,
    )
