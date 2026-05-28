from dataclasses import dataclass, field

import flet as ft
from openpyxl import load_workbook

from src.resnet_similarity import ResNetSimilarityEngine
from src.db.db import DBConn, SKU
from src.api.api import Playwright, BrowserConfig
from src.component.log_viewer import LogViewer
from src.component.table import Table
from src.component.crawler import Crawler


# 数据库和自动化操作
@ft.observable
@dataclass
class AppState:
    def __init__(self, config: BrowserConfig):
        super().__init__()
        self.db = DBConn()
        self.api = Playwright(config=config)


@ft.component
def App(log_viewer: LogViewer) -> ft.Row:

    page = ft.use_page()
    app, _ = ft.use_state(AppState(BrowserConfig(ali1688_path="ali1688")))
    db = app.db
    _picker = ft.use_ref()

    # 初始化 FilePicker（只执行一次）
    if _picker.current is None:

        def _on_result(e: ft.FilePickerResultEvent):
            if e.files is None:
                return
            for f in e.files:
                wb = load_workbook(f.path)
                for ws in wb.worksheets:
                    for row in ws.iter_rows(min_row=1, values_only=True):
                        if len(row) < 7:
                            continue
                        db.create_sku(
                            SKU(
                                origin_id=row[1],
                                origin_shop_name=row[1],
                                origin_primary_image_link=row[2],
                                origin_price=row[6],
                            )
                        )

        picker = ft.FilePicker(on_result=_on_result)
        page.overlay.append(picker)
        page.update()
        _picker.current = picker

    async def _on_import_click(e):
        await _picker.current.pick_files(
            dialog_title="选择文件进行导入",
            allowed_extensions=["xlsx"],
        )

    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Button(
                            "导入",
                            icon=ft.Icons.UPLOAD_FILE,
                            on_click=_on_import_click,
                        ),
                        ft.Divider(),
                        ft.Column(
                            controls=[
                                Table(
                                    [
                                        SKU(
                                            origin_shop_name="店铺A",
                                            origin_primary_image_link="https://cbu01.alicdn.com/img/ibank/O1CN01Y6tpy129Wrl2dlnmX_!!2171508076-0-cib.jpg",
                                            origin_price="9.99",
                                            match_link="https://example.com/match",
                                            match_image_link="https://cbu01.alicdn.com/img/ibank/O1CN01Y6tpy129Wrl2dlnmX_!!2171508076-0-cib.jpg",
                                            match_score=0.85,
                                            status=1,
                                        ),
                                        SKU(
                                            origin_shop_name="店铺A",
                                            origin_primary_image_link="https://cbu01.alicdn.com/img/ibank/O1CN01Y6tpy129Wrl2dlnmX_!!2171508076-0-cib.jpg",
                                            origin_price="9.99",
                                            match_link="https://example.com/match",
                                            match_image_link="https://cbu01.alicdn.com/img/ibank/O1CN01Y6tpy129Wrl2dlnmX_!!2171508076-0-cib.jpg",
                                            match_score=0.85,
                                            status=1,
                                        ),
                                        SKU(
                                            origin_shop_name="店铺A",
                                            origin_primary_image_link="https://cbu01.alicdn.com/img/ibank/O1CN01Y6tpy129Wrl2dlnmX_!!2171508076-0-cib.jpg",
                                            origin_price="9.99",
                                            match_link="https://example.com/match",
                                            match_image_link="https://cbu01.alicdn.com/img/ibank/O1CN01Y6tpy129Wrl2dlnmX_!!2171508076-0-cib.jpg",
                                            match_score=0.85,
                                            status=1,
                                        ),
                                        SKU(
                                            origin_shop_name="店铺A",
                                            origin_primary_image_link="https://cbu01.alicdn.com/img/ibank/O1CN01Y6tpy129Wrl2dlnmX_!!2171508076-0-cib.jpg",
                                            origin_price="9.99",
                                            match_link="https://example.com/match",
                                            match_image_link="https://cbu01.alicdn.com/img/ibank/O1CN01Y6tpy129Wrl2dlnmX_!!2171508076-0-cib.jpg",
                                            match_score=0.85,
                                            status=1,
                                        ),
                                        SKU(
                                            origin_shop_name="店铺A",
                                            origin_primary_image_link="https://cbu01.alicdn.com/img/ibank/O1CN01Y6tpy129Wrl2dlnmX_!!2171508076-0-cib.jpg",
                                            origin_price="9.99",
                                            match_link="https://example.com/match",
                                            match_image_link="https://cbu01.alicdn.com/img/ibank/O1CN01Y6tpy129Wrl2dlnmX_!!2171508076-0-cib.jpg",
                                            match_score=0.85,
                                            status=1,
                                        ),
                                    ]
                                )
                            ],
                            height=1200,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ]
                ),
                expand=7,
                bgcolor=ft.Colors.YELLOW,
                border=ft.Border.all(color=ft.Colors.ORANGE_900),
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=Crawler(app.db, app.api),
                            expand=2,
                            bgcolor=ft.Colors.RED,
                        ),
                        ft.Container(
                            content=log_viewer, expand=8, bgcolor=ft.Colors.GREEN
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,  # 列内内容从顶部开始排列
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                expand=True,
                bgcolor=ft.Colors.PURPLE,
            ),
        ],
    )


def main(page: ft.Page):
    page.title = "SKU 比价工具"

    page.window.width = 1100
    page.window.min_width = 1100
    page.window.min_height = 600

    log_viewer = LogViewer()  # 创建日志查看器实例
    page.render(lambda: App(log_viewer))


if __name__ == "__main__":
    ft.run(main)
