import io

import flet as ft
from PIL import Image
from src.db.db import DBConn
from src.api.api import Playwright


@ft.control
class Crawler(ft.Column):
    def __init__(self, db: DBConn, playwright: Playwright):
        super().__init__()

        # 比价中
        self.comparing: bool = False
        # 停止中
        self.stopping: bool = False
        self.db: DBConn = db
        self.playwright: Playwright = playwright

        # 构建 UI 界面
        self._build_ui()

    def _build_ui(self):
        """构建UI界面"""
        self.spacing = 10
        self.margin = 10
        self.controls = [
            ft.Row(
                controls=[
                    ft.Button(
                        "开始采集",
                        on_click=self.handle_start_crawler,
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_600,
                    ),
                    ft.Button(
                        "停止采集",
                        on_click=self.handle_stop_crawler,
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_600,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),  # 登录 1688
            ft.Row(
                controls=[
                    ft.Button(
                        "登录1688",
                        on_click=self.handle_login_1688,
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_600,
                    ),
                    ft.Button(
                        "登录状态",
                        on_click=self.handle_check_login_1688,
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_600,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            ft.Column(
                controls=[
                    ft.Text(
                        "比价参数设定",
                        size=18,
                        bgcolor=ft.Colors.BLACK,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Divider(),
                    ft.Row(
                        controls=[
                            ft.Switch(
                                label="一件代发",  # 使用 label 参数
                                value=True,  # 使用 value 参数
                                expand=6,
                            ),
                            ft.TextField(
                                label="比价系数",
                                value="1.2",
                                expand=4,
                            ),
                        ],
                        #     expand=True,
                    ),
                ],
            ),
        ]

    # 是否已登录,规则是查找是否有已登陆的标志
    # 已登录 -> True
    # 未登录 -> False
    async def already_logined(self) -> bool:
        await self.playwright.goto_home_page()

        # Shadow DOM 不能使用 xpath 定位

        # login_item = self.playwright.ali1688_page.locator(
        #     "div.userInfo workbench-i18n.title[name='AlibarMe.Login']"
        # )

        # return (
        #     await login_item.count() > 0 and await login_item.text_content() == "登录"
        # )

        logined_item = self.playwright.ali1688_page.locator("div.userInfo.logged")

        return await logined_item.count() > 0

    # 对话框
    def show_dialog(self, title: str, content: str, color: ft.Colors):
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text(title),
                content=ft.Text(value=content, color=color),
                actions=[
                    ft.TextButton("确定", on_click=lambda e: self.page.pop_dialog()),
                ],
            )
        )

    async def handle_check_login_1688(self, e):
        try:
            # 显示弹窗
            if await self.already_logined():
                self.show_dialog("登录状态", "✅ 已登录", ft.Colors.GREEN)
            else:
                self.show_dialog("登录状态", "❌ 未登录，请重新登录", ft.Colors.RED)
        except Exception as e:
            self.show_dialog("登录检查", f"检查异常，请稍后重试 {e}", ft.Colors.RED)

    # 登录
    async def handle_login_1688(self, e):
        try:
            if await self.already_logined():
                self.show_dialog(
                    "登录状态", "✅ 已登录，不需要重新登录", ft.Colors.GREEN
                )
                return

            # 进入登录页
            await self.playwright.goto_login_page()

            # 登录二维码元素
            qr_code = self.playwright.ali1688_page.locator(
                "xpath=//div[@id='page']//div[@class='qrcode-login']//div[@id='qrcode-img']/canvas"
            )

            # 二维码
            image_bytes = await qr_code.screenshot()

            # 展现登录二维码
            image = Image.open(io.BytesIO(image_bytes))
            image.show()

        except Exception as e:
            self.show_dialog("登录", f"登陆异常，请稍后重试 {e}", ft.Colors.GREEN)

    # 开始采集
    async def handle_start_crawler(self, e):
        # 开始比价
        self.comparing = True
        while self.comparing:
            for sku in self.db.get_random_sku():
                # 1. 进入主页
                # 2. 复制/粘贴
                # 3. 搜索 //div[@class='copy-image-container']//div[@data-tracker="pasteImagePreview"]
                # 4. 匹配
                pass

    # 停止采集
    async def handle_stop_crawler(self, e):
        print("停止采集")
        self.comparing = True
