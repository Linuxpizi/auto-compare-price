import flet as ft


class Crawler(ft.BaseControl):
    def build(self):
        # ... 其他控件
        self.page = None  # 挂载后由框架赋值

    async def handle_check_login_1688(self, e):
        # 创建确认按钮（保存引用）
        confirm_btn = ft.TextButton(
            "验证登录",
            on_click=lambda e: self.start_login_check(e, confirm_btn, dialog),
        )

        dialog = ft.AlertDialog(
            title=ft.Text("登录状态检查"),
            content=ft.Text("点击确认开始验证"),
            actions=[
                confirm_btn,
                ft.TextButton("取消", on_click=lambda e: self.close_dialog(dialog)),
            ],
        )

        dialog.open = True
        self.page.dialog = dialog
        await self.page.update_async()

    async def start_login_check(self, e, confirm_btn, dialog):
        # 1. 按钮进入加载状态
        confirm_btn.disabled = True
        confirm_btn.text = None  # 移除文字
        confirm_btn.icon = None  # 清除原有图标
        # 将内容替换为转圈（ProgressRing）
        confirm_btn.content = ft.ProgressRing(width=20, height=20, stroke_width=2)
        await dialog.update_async()  # 立即刷新弹窗

        # 2. 模拟耗时操作（替换为你的真实验证逻辑）
        try:
            is_logged_in = await self.check_login_status()  # 你的异步验证方法
        except Exception as ex:
            is_logged_in = False

        # 3. 关闭弹窗，或者显示结果后关闭
        dialog.open = False
        self.page.dialog = None
        await self.page.update_async()

        # 可选：外部提示
        if is_logged_in:
            await self.page.show_snack_bar(ft.SnackBar(content=ft.Text("✅ 已登录")))
        else:
            await self.page.show_snack_bar(ft.SnackBar(content=ft.Text("❌ 未登录")))

    async def check_login_status(self):
        # 模拟异步操作，例如 Playwright 页面检查
        import asyncio

        await asyncio.sleep(2)
        return True

    async def close_dialog(self, dialog):
        dialog.open = False
        self.page.dialog = None
        await self.page.update_async()
