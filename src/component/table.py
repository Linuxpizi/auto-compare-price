import webbrowser
from typing import List

import flet as ft
from flet_datatable2 import DataTable2, DataColumn2, DataRow2

from src.db.db import SKU


# @ft.component
def TableRows(rows: List[SKU]) -> List[DataRow2]:
    return [
        DataRow2(
            cells=[
                ft.DataCell(
                    ft.Text(
                        row.origin_shop_name,
                        selectable=True,
                        weight=ft.FontWeight.BOLD,
                    ),
                    expand=2,
                ),
                ft.DataCell(
                    content=ft.Image(
                        src=row.origin_primary_image_link,
                        fit=ft.BoxFit.CONTAIN,
                        margin=5,
                    ),
                    expand=3,
                ),
                ft.DataCell(
                    ft.Button(
                        content=ft.Image(
                            src=row.match_image_link,
                            fit=ft.BoxFit.CONTAIN,
                            margin=5,
                        ),
                        on_click=lambda: webbrowser.open(row.match_image_link),
                        style=ft.ButtonStyle(
                            padding=0,
                            shape=ft.RoundedRectangleBorder(radius=4),
                            bgcolor=ft.Colors.TRANSPARENT,
                            elevation=0,
                        ),
                    ),
                    expand=3,
                ),
                ft.DataCell(
                    ft.Text(row.origin_price),
                    expand=True,
                ),
                ft.DataCell(ft.Text(row.match_score), expand=True),
                ft.DataCell(ft.Text(row.match_remark), expand=True),
                ft.DataCell(
                    ft.Text("比价完成" if row.status == "0" else "待比价"),
                    expand=True,
                ),
            ],
            color=ft.Colors.GREEN_50,  # 行背景色
        )
        for row in rows
    ]


@ft.component
def Table(rows: List[SKU]) -> DataTable2:
    return DataTable2(
        columns=[
            DataColumn2("店铺名称"),
            DataColumn2("主图"),
            DataColumn2("匹配图"),  # 包括链接
            DataColumn2("原始折扣价"),
            DataColumn2("相似度"),
            DataColumn2("备注"),
            DataColumn2("状态"),  # 0 - 待处理, 1 - 已处理
        ],
        rows=TableRows(rows),  # 添加更多行
        expand=True,
        fixed_top_rows=1,
        data_row_height=120,
    )
