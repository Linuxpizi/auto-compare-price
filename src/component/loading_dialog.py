from dataclasses import dataclass

import flet as ft


@ft.observable
@dataclass
class LoadingState:
    def __init__(self, title: str, content: str, loading: bool = True):
        self.title = title
        self.content = content
        self.loading = loading

    def set_loading(self, loading: bool):
        self.loading = loading


@ft.component
def LoadingDialog(state: LoadingState) -> ft.AlertDialog:
    def _loading(loading: bool) -> float:
        return None if loading else 1

    return ft.AlertDialog(
        modal=True,
        title=ft.Text(state.title),
        content=ft.Column(
            [
                ft.Text("比价进行中，请稍候..."),
                ft.ProgressRing(_loading(state.loading)),
            ],
            alignment=ft.CrossAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        actions=[
            ft.TextButton(
                "确定",
                disabled=state.loading,
                on_click=lambda e: state.set_loading(False),
            ),
        ],
        on_dismiss=lambda e: state.set_loading(False),
    )


@ft.component
def App():
    import asyncio

    state = LoadingState("这是一个测试", "hhhhhhhhhhh")

    async def long_task():
        nonlocal state
        print("任务开始...")
        await asyncio.sleep(5)  # 模拟耗时操作
        print("任务完成！")

        # 任务完成后，启用确认按钮
        state.set_loading(False)
        return "长时间任务完成啦！"

    ft.context.page.run_task(long_task)

    ft.use_dialog(LoadingDialog(state) if state.loading else None)

    return ft.SafeArea(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Main App", size=22, weight=ft.FontWeight.BOLD),
                    ft.Button(
                        "Open User Panel",
                        on_click=lambda: state.set_loading(False),
                    ),
                ]
            ),
        )
    )

def main(page: ft.Page):
    page.render(App)


if __name__ == "__main__":
    ft.run(main)
