"""
1. 模拟浏览器相关的操作
"""

from playwright.async_api import (
    async_playwright,
    Page,
    BrowserContext,
)

from src.api.api_watch import APIWatcher

# 淘宝
TAOBAO = "https://login.taobao.com/havanaone/login/login.htm?bizName=taobao"

# 1688
ALI1688_LOGIN = "https://login.1688.com/"
ALI1688_HOME = "https://www.1688.com/"


# 配置日志
class BrowserConfig:
    def __init__(
        self, ali1688_session_path: str = "storage/session", headless: bool = True
    ):
        self.headless = headless
        self.ali1688_session_path = ali1688_session_path
        # self.extensions = (
        #     "extensions/hsq_gu_v3_13.9.6"  # 这里可以添加需要加载的浏览器扩展路径
        # )


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
        # self.extensions = config.extensions
        self.ali1688_session_path = config.ali1688_session_path

        # 1688
        self.ali1688_context: BrowserContext = None
        self.ali1688_page: Page = None

        # 数据爬取线程
        self.running = False

    # 此方法必须要限制性
    async def setup(self):
        """启动浏览器和上下文"""
        self.playwright = await async_playwright().start()

        # 启动浏览器
        self.ali1688_context: BrowserContext = (
            await self.playwright.chromium.launch_persistent_context(
                headless=self.headless,
                args=[
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--remote-debugging-port=19988",
                    "--disable-blink-features=AutomationControlled",
                    # "--disable-extensions-except=" + self.extensions,
                    # "--load-extension=" + self.extensions,
                ],
                user_data_dir=self.ali1688_session_path,
            )
        )

        # 网络监听
        self.watch_api_network = APIWatcher(self.ali1688_context)

        # 添加防检测脚本
        await self.ali1688_context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.navigator.chrome = {
                runtime: {},
            };
        """)

        # 初始化页面
        self.ali1688_page = await self.ali1688_context.new_page()

    async def close(self):
        """关闭所有资源"""
        if self.ali1688_page and not self.ali1688_page.is_closed():
            await self.ali1688_page.close()
        if self.ali1688_context:
            self.ali1688_context.close()
        if hasattr(self, "playwright"):
            await self.playwright.close()

        self.watch_api_network.stop()

    # # 监控网络--------------------
    # # 监控网络--------------------end

    # 基础功能
    # 1. 登录页
    async def goto_login_page(self):
        await self.ali1688_page.goto(ALI1688_LOGIN, wait_until="load")

    # 2. 主页
    async def goto_home_page(self):
        await self.ali1688_page.goto(ALI1688_HOME, wait_until="load")

    # 4. 登录

    # 5. 搜索图片(在 1688 主页，复制的任何图片链接，都会触发搜索图片弹窗)
    # 6. 点击获取图片后利用 API 捕获需要的数据，需要注意条件选择
    # 1. 一件代发、1件代发包邮
    # 2. 只选择最靠前的数据(前 20)，进行相似度比对，过滤相似度(80%以上的，然后其中选择匹配度最高的)
    # 3. 进入对应的详情页，选择匹配度最高的 SKU，进行价格比对(1.2倍)
    # 4. 留下符合条件的数据


if __name__ == "__main__":
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

            page.goto(ALI1688_LOGIN)

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
            page.controls.append(
                ft.Image(src=f"data:image/png;base64,{qr_code_base64}")
            )

        page.controls.append(ft.Button("Click me", on_click=show_qr_code))
        # no need to call page.update() here either

    ft.run(main)
