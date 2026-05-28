import flet as ft
import asyncio


def main(page: ft.Page):
    page.title = "日志组件示例"
    page.window_width = 500
    page.window_height = 400

    # 创建一个 ListView 作为日志容器
    # auto_scroll=True 是实现自动滚到底部的关键
    log_list = ft.ListView(
        expand=True,  # 填满可用空间
        spacing=5,  # 每条日志之间的间距
        padding=10,  # 内边距
        auto_scroll=True,  # 当添加新内容时自动滚动到底部
    )

    # 添加日志的函数
    def add_log(message: str, level: str = "INFO"):
        # 可以根据日志级别设置不同的颜色
        color = {
            "INFO": ft.Colors.GREEN,
            "WARNING": ft.Colors.ORANGE,
            "ERROR": ft.Colors.RED,
        }.get(level, ft.Colors.WHITE)

        log_list.controls.append(ft.Text(f"[{level}] {message}", color=color, size=14))
        page.update()  # 更新页面，新日志会立即出现并自动滚动到底部

    # 模拟异步产生日志（例如从后台任务或网络请求接收日志）
    async def simulate_logs():
        for i in range(30):
            await asyncio.sleep(0.5)
            if i % 10 == 0:
                add_log(f"这是一条警告日志 #{i}", "WARNING")
            elif i % 15 == 0:
                add_log(f"发生错误了 #{i}", "ERROR")
            else:
                add_log(f"这是一条普通日志 #{i}")

    # 启动模拟日志任务（实际使用中可以是真实的日志接收函数）
    page.run_task(simulate_logs)

    # 页面布局：一个用于控制的面板加上日志列表
    page.add(
        ft.Row(
            [
                ft.ElevatedButton(
                    "添加测试日志", on_click=lambda e: add_log("手动添加的测试日志")
                ),
                ft.ElevatedButton(
                    "清空日志",
                    on_click=lambda e: (log_list.controls.clear(), page.update()),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Divider(),
        log_list,  # 日志列表占据剩余空间
    )


ft.app(target=main)
