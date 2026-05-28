import flet as ft


class LogViewer(ft.Column):
    """一个可复用的日志查看器组件"""

    def __init__(self, max_logs: int = 1000):
        super().__init__()
        self.max_logs = max_logs  # 最大保留日志条数，防止内存溢出
        self.logs = []  # 存储原始日志数据
        self.filter_levels = {"INFO", "WARNING", "ERROR"}  # 当前显示的日志级别

        self._build_ui()

    def _build_ui(self):
        """构建UI界面"""
        # 日志级别筛选按钮
        self.filter_row = ft.Row(
            controls=[
                ft.Chip(
                    label=ft.Text("INFO"),
                    selected="INFO" in self.filter_levels,
                    on_select=lambda e: self._toggle_filter("INFO"),
                ),
                ft.Chip(
                    label=ft.Text("WARNING"),
                    selected="WARNING" in self.filter_levels,
                    on_select=lambda e: self._toggle_filter("WARNING"),
                ),
                ft.Chip(
                    label=ft.Text("ERROR"),
                    selected="ERROR" in self.filter_levels,
                    on_select=lambda e: self._toggle_filter("ERROR"),
                ),
            ],
            spacing=10,
        )

        # 搜索框
        self.search_field = ft.TextField(
            hint_text="搜索日志...",
            on_change=lambda e: self.refresh_display(),
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
        )

        # 控制栏
        self.controls = [
            ft.Row(
                controls=[
                    self.search_field,
                    ft.IconButton(
                        icon=ft.Icons.CLEAR, on_click=lambda e: self._clear_logs()
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DOWNLOAD, on_click=lambda e: self._export_logs()
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            self.filter_row,
            ft.Divider(),
        ]

        # 日志列表容器
        self.log_list = ft.ListView(
            expand=True,
            spacing=3,
            padding=10,
            auto_scroll=True,
        )
        self.controls.append(self.log_list)

    def add_log(self, message: str, level: str = "INFO"):
        """添加一条日志"""
        # 存储原始数据
        self.logs.insert(0, {"message": message, "level": level})  # 最新在前
        if len(self.logs) > self.max_logs:
            self.logs.pop()

        # 刷新显示
        self.refresh_display()

    def _toggle_filter(self, level: str):
        """切换日志级别筛选"""
        if level in self.filter_levels:
            self.filter_levels.remove(level)
        else:
            self.filter_levels.add(level)
        self.refresh_display()

    def refresh_display(self):
        """根据筛选条件和搜索词刷新显示"""
        search_text = self.search_field.value.lower() if self.search_field.value else ""

        self.log_list.controls.clear()

        # 注意：因为最新日志在列表开头，这里直接遍历显示
        # 如果不想要倒序，可以在 add_log 时改为 append()
        for log in self.logs:
            # 级别筛选
            if log["level"] not in self.filter_levels:
                continue
            # 搜索筛选
            if search_text and search_text not in log["message"].lower():
                continue

            # 设置颜色
            color = {
                "INFO": ft.Colors.GREEN,
                "WARNING": ft.Colors.ORANGE,
                "ERROR": ft.Colors.RED,
            }.get(log["level"], ft.Colors.WHITE)

            self.log_list.controls.append(
                ft.Text(f"[{log['level']}] {log['message']}", color=color, size=12)
            )

        self.update()

    def _clear_logs(self):
        """清空所有日志"""
        self.logs.clear()
        self.refresh_display()

    def _export_logs(self):
        """导出日志到剪贴板"""
        import pyperclip

        log_text = "\n".join(
            [f"[{log['level']}] {log['message']}" for log in self.logs]
        )
        pyperclip.copy(log_text)
        print("日志已复制到剪贴板")


# 使用示例
def main(page: ft.Page):
    page.title = "日志组件"
    page.window_width = 600
    page.window_height = 500

    log_viewer = LogViewer(max_logs=500)

    # 模拟添加日志
    import asyncio

    async def add_test_logs():
        for i in range(20):
            await asyncio.sleep(0.3)
            if i % 3 == 0:
                log_viewer.add_log(f"完成第 {i} 项任务")
            elif i % 7 == 0:
                log_viewer.add_log(f"网络请求超时 {i}", "WARNING")
            elif i % 11 == 0:
                log_viewer.add_log(f"无法连接到服务器 {i}", "ERROR")
            else:
                log_viewer.add_log(f"处理数据项 {i}")

    page.run_task(add_test_logs)

    page.add(log_viewer)


ft.app(target=main)
