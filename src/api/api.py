"""
1. 模拟浏览器相关的操作
"""

from dataclasses import dataclass

from playwright.async_api import (
    async_playwright,
    Page,
    BrowserContext,
    APIRequestContext,
)

# 淘宝
TAOBAO = "https://login.taobao.com/havanaone/login/login.htm?bizName=taobao"
# 1688
ALI1688 = "https://login.1688.com"


# 配置日志
@dataclass
class BrowserConfig:
    def __init__(self, ali1688_path: str, headless: bool = True):
        self.headless = headless
        self.ali1688_path = ali1688_path
        self.extensions = (
            "extensions/hsq_gu_v3_13.9.6"  # 这里可以添加需要加载的浏览器扩展路径
        )


# 模拟浏览器操作的类
class Playwright:
    def __init__(
        self,
        config: BrowserConfig,
    ):
        """
        初始化爬虫类
        """
        self.headless = config.headless
        self.extensions = config.extensions

        # self.taobao_path = config.taobao_path
        self.ali1688_path = config.ali1688_path

        # taobao
        # self.taobao_context: BrowserContext = None
        # self.taobao_page: Page = None

        # 1688
        self.ali1688_context: BrowserContext = None
        self.ali1688_page: Page = None

        # 确保存储目录存在
        self._setup()

        # 数据爬取线程
        self.running = False

    async def _setup(self):
        """启动浏览器和上下文"""
        self.playwright = async_playwright().start()

        # 启动浏览器
        self.taobao_context: BrowserContext = (
            await self.playwright.chromium.launch_persistent_context(
                headless=self.headless,
                args=[
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--remote-debugging-port=19988",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions-except=" + self.extensions,
                    "--load-extension=" + self.extensions,
                ],
                user_data_dir=self.taobao_path,
            )
        )

        # 添加防检测脚本
        await self.taobao_context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.navigator.chrome = {
                runtime: {},
            };
        """)

    async def close(self):
        """关闭所有资源"""
        if self.taobao_page and not self.taobao_page.is_closed():
            await self.taobao_page.close()
        if self.taobao_context:
            self.taobao_context.close()
        if hasattr(self, "playwright"):
            await self.playwright.close()

    async def check_login(
        self, home_url: str, check_selector: str, timeout: int = 5000
    ) -> bool:
        """
        检查用户是否已登录

        :param check_selector: 用于检查登录状态的CSS选择器
        :param timeout: 等待选择器的超时时间（毫秒）
        :return: 是否已登录
        """
        # 尝试定位登录状态元素
        await self.taobao_page.goto(home_url, wait_until="networkidle")
        check_login = await self.taobao_page.locator(
            "xpath=//div[@class='kpro-workbench-layout-avatar__username']"
        )
        if await check_login.count() == 1:
            return True
        return False

    async def get_qr_code(self, home_url: str) -> bytes:
        """
        获取二维码图像
        """
        if not await self.check_login():
            import base64
            from PIL import Image
            from io import BytesIO

            await self.taobao_page.goto(home_url, wait_until="networkidle")
            account = await self.taobao_page.wait_for_selector(
                "xpath=//div[@class='account-type__item__title']", timeout=5000
            )
            await account.click()

            qrcode = await self.taobao_page.wait_for_selector(
                "xpath=//div[@class='qrcodeImage___Gg2hK']/img", timeout=1000
            )
            # 去掉前缀
            header, encoded = await qrcode.get_attribute("src").split(",", 1)

            # 解码 Base64
            data = base64.b64decode(encoded)

            # 将数据转换为图像
            image = Image.open(BytesIO(data))

            # 保存图像为 PNG 文件
            image.show()

        return True

    async def qr_code_login(self, home_url: str) -> bool:
        """
        通过二维码扫码登录
        """
        if not await self.check_login():
            import base64
            from PIL import Image
            from io import BytesIO

            await self.taobao_page.goto(home_url, wait_until="networkidle")
            account = await self.taobao_page.wait_for_selector(
                "xpath=//div[@class='account-type__item__title']", timeout=5000
            )
            await account.click()

            qrcode = await self.taobao_page.wait_for_selector(
                "xpath=//div[@class='qrcodeImage___Gg2hK']/img", timeout=1000
            )
            # 去掉前缀
            header, encoded = await qrcode.get_attribute("src").split(",", 1)

            # 解码 Base64
            data = base64.b64decode(encoded)

            # 将数据转换为图像
            image = Image.open(BytesIO(data))

            # 保存图像为 PNG 文件
            image.show()

        return True

    # 1. 打开指定的页面
    # 2. 发现哈士奇插件，搜图到 1688
    async def goto_link_page(self, link: str, selector: str = "") -> bool:
        """登录淘宝"""
        return await self.qr_code_login(TAOBAO)
    
import flet as ft
import base64


async def get_qr_code() -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--remote-debugging-port=19988",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        page = await browser.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.navigator.chrome = {
                runtime: {},
            };
        """)

        page.goto(TAOBAO)

        # 定位元素并截图

        # 保存到文件，用于 debug
        # 已成功定位登录的二维码
        # 显示到 UI 界面，扫描登录
        # page.locator("#qrcode-img").screenshot(path="qrcode.png")

        browser.close()

        # base64 格式用于 UI 展示
        image_bytes = page.locator("#qrcode-img").screenshot()
        return base64.b64encode(image_bytes).decode()  # 解码 Base64 数据


def main(page: ft.Page):
    def show_qr_code(e):
        qr_code_base64 = get_qr_code()
        page.controls.append(ft.Image(src=f"data:image/png;base64,{qr_code_base64}"))

    page.controls.append(ft.Button("Click me", on_click=show_qr_code))
    # no need to call page.update() here either


if __name__ == "__main__":
    ft.run(main)
