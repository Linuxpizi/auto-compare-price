import io
from asyncio import sleep
from random import random, randrange

import flet as ft
from PIL import Image

from src.db.db import DBConn
from src.api.api import Playwright


@ft.control
class Crawler(ft.Column):
    def __init__(
        self,
        db: DBConn,
        playwright: Playwright,
        price_ratio_factor: float = 1.2,
        dropshipping: bool = True,
    ):
        super().__init__()

        # 停止比价
        self.stopping: bool = False
        self.db: DBConn = db
        self.playwright: Playwright = playwright

        # 比价参数设置
        # 比价系数
        self.price_ratio_factor: float = price_ratio_factor
        # 一件代发
        self.dropshipping = dropshipping

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

    # 随机延时 1. 等待页面记载 2. 模拟
    async def await_sleep(self, delay: float = 0.0):
        await sleep(random() + delay)

    # 是否已登录,规则是查找是否有已登陆的标志
    # 已登录 -> True
    # 未登录 -> False
    async def already_logined(self) -> bool:
        await self.playwright.goto_home_page()
        await self.await_sleep(0.2)

        # Shadow DOM 不能使用 xpath 定位
        # login_item = self.playwright.ali1688_page.locator(
        #     "div.userInfo workbench-i18n.title[name='AlibarMe.Login']"
        # )

        # return (
        #     await login_item.count() > 0 and await login_item.text_content() == "登录"
        # )

        logined_item = self.playwright.ali1688_page.locator("div.userInfo.logged")

        return await logined_item.count() > 0

    # 剪切板
    async def clipboard(self, link: str):
        try:
            await self.playwright.ali1688_page.evaluate(
                f"navigator.clipboard.writeText('{link}')"
            )
            await self.playwright.ali1688_page.keyboard.press("Control+V")
            await self.await_sleep()

        except Exception as e:
            self.show_dialog("查找相似图", f"设置剪切板找图异常 {e}", ft.Colors.RED)

    # 对话框
    async def show_dialog(self, title: str, content: str, color: ft.Colors):
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
                await self.show_dialog("登录状态", "✅ 已登录", ft.Colors.GREEN)
            else:
                await self.show_dialog(
                    "登录状态", "❌ 未登录，请重新登录", ft.Colors.RED
                )
        except Exception as e:
            await self.show_dialog(
                "登录检查", f"检查异常，请稍后重试 {e}", ft.Colors.RED
            )

    # 登录
    async def handle_login_1688(self, e):
        try:
            if await self.already_logined():
                await self.show_dialog(
                    "登录状态", "✅ 已登录，不需要重新登录", ft.Colors.GREEN
                )
                return

            # 进入登录页
            await self.playwright.goto_login_page()
            await self.await_sleep(0.2)

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
            await self.show_dialog("登录", f"登陆异常，请稍后重试 {e}", ft.Colors.GREEN)

    # 开始采集
    async def handle_start_crawler(self, e):
        self.stopping = False

        # 启动网络监听
        await self.playwright.watch_api_network.start()

        # 开始比价
        while True:
            sku = self.db.get_compare_sku()
            if sku:
                # 1. 进入主页
                await self.playwright.goto_home_page()
                await self.await_sleep(0.8)

                # 2. 复制/粘贴
                await self.clipboard(sku.origin_primary_image_link)
                # 3. 搜索 //div[@class='copy-image-container']//div[@data-tracker="pasteImagePreview"]
                # 这里操作完成后，需要捕获数据，目前采集前 12 调数据
                await self.search_image()

                # 选择一件代发
                if self.dropshipping:
                    await self.set_dropshipping()

                if self.stopping:
                    # 模态框处理
                    self.stopping = False
                    break

    async def search_image(self):
        search_image_item = self.playwright.ali1688_page.locator(
            "xpath=//div[@class='copy-image-container']//div[@data-tracker='pasteImagePreview']"
        )

        await search_image_item.click(delay=random())

    async def set_dropshipping(self):
        # 等待页面加载完成
        await self.await_sleep(randrange(3, 5))
        dropshipping_item = self.playwright.ali1688_page.locator(
            "xpath=//div[@id='root-container']//div[starts-with(@class, 'filterBottomContainer')]//div[starts-with(@class, 'bottomFilterOption')][3]"
        )

        await dropshipping_item.click(delay=random())

    # 停止采集
    async def handle_stop_crawler(self, e):
        # 显示模态弹窗
        self.stopping = True
        await self.playwright.close()
