# import asyncio
# import flet as ft


# def main(page: ft.Page):
#     # 用于存储对话框和确认按钮的引用
#     dlg = None
#     confirm_btn = None

#     async def long_task():
#         print("任务开始...")
#         await asyncio.sleep(5)  # 模拟耗时操作
#         print("任务完成！")

#         # 任务完成后，启用确认按钮
#         nonlocal confirm_btn
#         if confirm_btn:
#             confirm_btn.disabled = False
#             page.update()  # 异步更新界面

#         return "长时间任务完成啦！"

#     def handle_confirm(e):
#         print("确认按钮被点击，关闭对话框")
#         page.pop_dialog()

#     def show_modal_dialog(e):
#         nonlocal dlg, confirm_btn

#         # 创建确认按钮（初始禁用）
#         confirm_btn = ft.Button("确认", disabled=True, on_click=handle_confirm)

#         dlg = ft.AlertDialog(
#             modal=True,
#             title=ft.Text("确认操作"),
#             content=ft.Column(
#                 [
#                     ft.Text("比价进行中，请稍候..."),
#                     ft.ProgressRing(),  # 一直转圈
#                 ],
#                 horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#             ),
#             actions=[
#                 confirm_btn,
#             ],
#         )
#         page.show_dialog(dlg)  # 注意：建议使用 open 而不是 show_dialog

#         # 对话框显示后，启动后台任务
#         page.run_task(long_task)

#     # 页面主按钮
#     page.add(ft.Button("打开任务对话框", on_click=show_modal_dialog))


# ft.app(main)


# import asyncio
# from dataclasses import dataclass
# import flet as ft


# # ---------- 1. 定义响应式状态 ----------
# @dataclass
# @ft.observable
# class LoadingDialogState:
#     """控制加载对话框的状态"""

#     open: bool = False  # 对话框是否显示
#     loading: bool = (
#         True  # 是否处于加载中（True=转圈且按钮禁用，False=停止转圈并启用按钮）
#     )

#     def start_loading(self):
#         """开始加载：显示对话框，进入加载状态"""
#         self.open = True
#         self.loading = True

#     def finish_loading(self):
#         """结束加载：退出加载状态（对话框保持打开，按钮变为可用）"""
#         self.loading = False

#     def close(self):
#         """关闭对话框"""
#         self.open = False


# # ---------- 2. 声明式主组件 ----------
# @ft.component
# def App():
#     # 创建响应式状态实例
#     state, _ = ft.use_state(LoadingDialogState)

#     # ---------- 声明式对话框 ----------
#     # 当 state.open 为 True 时渲染 AlertDialog，否则不渲染
#     ft.use_dialog(
#         (
#             ft.AlertDialog(
#                 modal=True,
#                 title=ft.Text("请稍候"),
#                 content=ft.Column(
#                     [
#                         ft.Text("比价进行中，请稍候..."),
#                         # 加载中 => value=None (无限旋转)；加载结束 => value=1.0 (停止，显示100%)
#                         ft.ProgressRing(value=None if state.loading else 1.0),
#                     ],
#                     horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#                 ),
#                 actions=[
#                     ft.TextButton(
#                         "确定",
#                         # 加载中按钮禁用，加载结束按钮启用
#                         disabled=state.loading,
#                         on_click=lambda _: state.close(),
#                     ),
#                 ],
#                 actions_alignment=ft.MainAxisAlignment.END,
#             )
#             if state.open
#             else None
#         ),
#     )

#     # ---------- 后台任务 ----------
#     async def long_task():
#         state.start_loading()  # 显示对话框并进入加载状态
#         print("任务开始...")
#         await asyncio.sleep(5)  # 模拟耗时操作（如网络请求、数据处理）
#         print("任务完成！")
#         state.finish_loading()  # 结束加载，按钮变为可用

#     # ---------- 按钮点击处理 ----------
#     def on_run_click(e):
#         ft.context.page.run_task(long_task)  # 在后台启动异步任务，不阻塞 UI

#     # ---------- UI 布局 ----------
#     return ft.Column(
#         [
#             ft.ElevatedButton("开始比价", on_click=on_run_click),
#         ],
#         horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#     )


# def main(page: ft.Page):
#     page.render(App)


# if __name__ == "__main__":
#     ft.app(target=main)

# import asyncio
# from dataclasses import dataclass
# import flet as ft

# # 1. 定义加载对话框的独立状态
# @dataclass
# @ft.observable
# class LoadingDialogState:
#     open: bool = False
#     loading: bool = True
#     title: str = "请稍候"
#     content: str = "加载中..."

#     def open_dialog(self):
#         self.open = True
#         self.loading = True

#     def finish_loading(self):
#         self.loading = False

#     def close_dialog(self):
#         self.open = False

# # 2. 封装加载对话框的 UI (这就是一个组件)
# @ft.component
# def LoadingDialog():
#     # 每个组件实例都拥有自己独立的状态
#     state, _ = ft.use_state(LoadingDialogState)

#     ft.use_dialog(
#         ft.AlertDialog(
#             modal=True,
#             title=ft.Text(state.title),
#             content=ft.Column(
#                 [
#                     ft.Text(state.content),
#                     ft.ProgressRing(value=None if state.loading else 1.0),
#                 ],
#                 horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#             ),
#             actions=[
#                 ft.TextButton(
#                     "确定",
#                     disabled=state.loading,
#                     on_click=lambda _: state.close_dialog(),
#                 ),
#             ],
#             actions_alignment=ft.MainAxisAlignment.END,
#         )
#     )

#     # 关键：将状态控制器返回给父组件
#     return state

# # 3. 在主界面中使用组件
# @ft.component
# def App():
#     # ✅ 直接调用函数，获取其状态控制器
#     dialog_state = LoadingDialog()

#     async def start_long_task():
#         dialog_state.open_dialog()
#         print("任务开始...")
#         await asyncio.sleep(5)
#         print("任务完成！")
#         dialog_state.finish_loading()

#     def on_button_click(e):
#         ft.context.page.run_task(start_long_task)

#     return ft.Column(
#         [
#             ft.ElevatedButton("开始比价", on_click=on_button_click),
#         ],
#         horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#     )

# def main(page: ft.Page):
#     page.render(App)

# if __name__ == "__main__":
#     ft.app(target=main)


import asyncio

import flet as ft


@ft.component
def App():
    show, set_show = ft.use_state(False)
    deleting, set_deleting = ft.use_state(False)

    async def handle_delete():
        set_deleting(True)
        # Simulate async operation
        await asyncio.sleep(2)
        set_deleting(False)
        set_show(False)

    ft.use_dialog(
        ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete report.pdf?"),
            content=ft.Text(
                "Deleting, please wait..." if deleting else "This cannot be undone."
            ),
            actions=[
                ft.Button(
                    "Deleting..." if deleting else "Delete",
                    disabled=deleting,
                    on_click=handle_delete,
                ),
                ft.TextButton(
                    "Cancel",
                    on_click=lambda: set_show(False),
                    disabled=deleting,
                ),
            ],
            on_dismiss=lambda: set_show(False),
        )
        if show
        else None
    )

    return ft.Column(
        controls=[
            ft.Text("Declarative Dialog Example", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Click the button to open a confirmation dialog."),
            ft.Button(
                "Delete File",
                icon=ft.Icons.DELETE,
                on_click=lambda: set_show(True),
            ),
        ],
    )


def main(page: ft.Page):
    page.render(App)


if __name__ == "__main__":
    ft.run(main)
