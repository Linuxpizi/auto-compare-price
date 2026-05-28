# # import flet as ft

# # def main(page: ft.Page):
# #     page.title = "图片与双按钮示例"
# #     page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
# #     page.vertical_alignment = ft.MainAxisAlignment.CENTER
# #     page.padding = 20

# #     # 创建一个容器作为卡片
# #     card = ft.Container(
# #         width=350,  # 固定宽度
# #         # height=450, # 高度可选，让内容撑开
# #         border_radius=20,  # 圆角半径
# #         bgcolor=ft.Colors.WHITE,  # 背景色
# #         padding=10,  # 内边距
# #         shadow=ft.BoxShadow(
# #             spread_radius=1,
# #             blur_radius=15,
# #             color=ft.Colors.GREY_300,
# #         ),
# #         content=ft.Column(
# #             spacing=15,  # 列内控件间距
# #             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
# #             controls=[
# #                 # 1. 上方图片
# #                 ft.Image(
# #                     src="https://picsum.photos/id/1015/300/200",  # 示例图片URL
# #                     width=300,
# #                     height=200,
# #                     fit=ft.BoxFit.COVER,  # 图片填充方式
# #                     border_radius=10,
# #                 ),
# #                 # 2. 下方的两个按钮 (放在一个 Row 中)
# #                 ft.Row(
# #                     alignment=ft.MainAxisAlignment.SPACE_BETWEEN, # 两端对齐
# #                     controls=[
# #                         ft.ElevatedButton(
# #                             "左边按钮",
# #                             icon=ft.Icons.ARROW_BACK,
# #                             on_click=lambda e: print("左边按钮被点击"),
# #                         ),
# #                         ft.ElevatedButton(
# #                             "右边按钮",
# #                             icon=ft.Icons.ARROW_FORWARD,
# #                             on_click=lambda e: print("右边按钮被点击"),
# #                         ),
# #                     ],
# #                 ),
# #             ],
# #         ),
# #     )

# #     page.add(card)

# # ft.app(target=main)


# import flet as ft

# def main(page: ft.Page):
#     page.title = "点击按钮显示图片"
#     page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
#     page.vertical_alignment = ft.MainAxisAlignment.CENTER
#     page.padding = 20

#     # 创建一个状态变量，控制图片是否显示
#     # 初始值为 False，表示图片隐藏
#     show_image = False

#     # 左边按钮的点击事件：将 show_image 设置为 True
#     def on_left_click(e):
#         nonlocal show_image
#         show_image = True
#         page.update()  # 更新页面，让图片显示出来

#     # 右边按钮的点击事件：可以清空图片或执行其他操作
#     def on_right_click(e):
#         print("右边按钮被点击")
#         # 可选：点击右边按钮时隐藏图片
#         # show_image.value = False
#         # page.update()

#     # 卡片容器
#     card = ft.Container(
#         width=350,
#         border_radius=20,
#         bgcolor=ft.Colors.WHITE,
#         padding=20,
#         shadow=ft.BoxShadow(
#             spread_radius=1,
#             blur_radius=15,
#             color=ft.Colors.GREY_300,
#         ),
#         content=ft.Column(
#             spacing=20,
#             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#             controls=[
#                 # 图片区域：根据 show_image.value 决定是否显示
#                 # 使用 ft.Column 作为容器，避免图片不显示时占用空间
#                 ft.Column(
#                     controls=[
#                         ft.Image(
#                             src="https://picsum.photos/id/1015/300/200",  # 示例图片
#                             width=300,
#                             height=200,
#                             fit=ft.BoxFit.COVER,
#                             border_radius=10,
#                         )
#                     ],
#                     visible=show_image,  # 关键：通过 visible 控制显示/隐藏
#                 ),
#                 # 两个按钮
#                 ft.Row(
#                     alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
#                     controls=[
#                         ft.ElevatedButton(
#                             "显示图片",
#                             icon=ft.Icons.IMAGE,
#                             on_click=on_left_click,
#                         ),
#                         ft.ElevatedButton(
#                             "右边按钮",
#                             icon=ft.Icons.ARROW_FORWARD,
#                             on_click=on_right_click,
#                         ),
#                     ],
#                 ),
#             ],
#         ),
#     )

#     page.add(card)

# ft.app(target=main)


import flet as ft

def main(page: ft.Page):
    # 设置表格的列宽不受限制
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(
                ft.Text("图片"),
                # 关键：设置合适的列宽，让图片能完全显示
                numeric=True,  # 如果希望列宽由内容决定
            ),
            ft.DataColumn(ft.Text("描述")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Image(
                            src="https://picsum.photos/id/1015/600/400",  # 示例图片
                            # width=600,
                            # height=400,
                            fit=ft.BoxFit.CONTAIN,  # 保持原始比例
                        ),
                    ),
                    ft.DataCell(ft.Text("这是一张大图")),
                ]
            ),
        ],
        # 解除行高限制
        # data_row_max_height=float("inf"),
        # 设置列的最小和最大宽度（可选）
        column_spacing=20,  # 列间距
    )
    
    # 将表格放在一个可水平滚动的容器中
    page.add(
        ft.Row(
            [data_table],
            scroll=ft.ScrollMode.AUTO,  # 允许水平滚动
            expand=True,
        )
    )
    page.update()

ft.app(target=main)