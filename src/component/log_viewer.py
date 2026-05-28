import flet as ft


@ft.control
class LogViewer(ft.ListView):
    """一个可复用的日志查看器组件"""

    def __init__(self, max_logs: int = 100):
        super().__init__()
        self.max_logs = max_logs  # 最大保留日志条数，防止内存溢出
        self.logs = []  # 存储原始日志数据
        self.filter_levels = {"INFO", "WARNING", "ERROR"}  # 当前显示的日志级别

        self._build_ui()

    def _build_ui(self):
        """构建UI界面"""
        # 日志列表容器
        self.log_list = ft.ListView(
            expand=True,
            spacing=3,
            padding=10,
            auto_scroll=True,
        )
        self.controls = [
            ft.Text(
                "日志", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400
            ),
            ft.Divider(),
            self.log_list,
        ]

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
        self.log_list.controls.clear()

        # 注意：因为最新日志在列表开头，这里直接遍历显示
        # 如果不想要倒序，可以在 add_log 时改为 append()
        for log in self.logs:
            # 级别筛选
            if log["level"] not in self.filter_levels:
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
