"""
Playwright API 请求抓取 + 异步处理示例
用法:
  1. 修改下面的 URL_PATTERN 为目标 API 关键字
  2. 将该文件 import 后自行启动浏览器，然后将 context 传入 ApiWatcher

示例:
    watcher = ApiWatcher(context, pattern_handlers={
        "mtop.1688.wosc.queryofferskuselectormodel": process_api_data,
        "mtop.1688.xxx.xxx": another_handler,
    })
    await watcher.start()
    # ... 你的正常页面逻辑 ...
    await watcher.stop()
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Callable, Coroutine, Any, List

from playwright.async_api import BrowserContext

from src.similarity.resnet_similarity import ResNetSimilarityEngine

# ============================================================
# 配置区 —— 按需修改
# ============================================================
SKU_URL_PATTERN = "mtop.1688.wosc.queryofferskuselectormodel"
IMAGE_URL_PATTERN = "mtop.relationrecommend.wirelessrecommend.recommend"


# ============================================================
# 模拟耗时处理（替换成你的真实逻辑）
# ============================================================
async def process_api_data(data: dict) -> None:
    """抓到数据后的处理逻辑，可能耗时较长，放在后台异步执行。"""
    print(f"[处理] 开始处理 API 数据，时间戳: {time.time():.3f}")
    await asyncio.sleep(5)  # 模拟耗时操作
    print(
        f"[处理] 数据处理完成，数据摘要: {json.dumps(data, ensure_ascii=False)[:200]}"
    )


# ============================================================
# API 抓取器 — 不关心页面，只认 BrowserContext
# ============================================================
class APIWatcher:
    """
    监听 BrowserContext 级别的网络响应，匹配指定 API 并异步处理。
    完全与 page 解耦——同 context 下任意页面的请求都能捕获。
    """

    def __init__(
        self,
        context: BrowserContext,
        pattern_handlers: (
            dict[str, Callable[[dict], Coroutine[Any, Any, None]]] | None
        ) = None,
    ):
        self._context = context
        self._pattern_handlers = pattern_handlers
        self._running = False

        # 比对模型初始化
        self.similarity = ResNetSimilarityEngine()

    async def start(self):
        """开始监听（context 下所有页面的网络响应）。"""
        self._running = True
        self._context.on("response", self._on_response)
        print(f"[监听] 开始匹配 API: {list(self._pattern_handlers.keys())}")

    async def stop(self):
        """停止监听。"""
        self._running = False
        self._context.remove_listener("response", self._on_response)
        print("[监听] 已停止")

    async def _on_response(self, response):
        """响应到达时的回调——快速过滤，耗时处理抛到后台。"""
        if not self._running:
            return

        url = response.url
        matched = next((p for p in self._pattern_handlers if p in url), None)
        if matched is None:
            return

        if not response.ok:
            print(f"[跳过] API 返回非正常状态: {response.status} -> {url[:120]}")
            return

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return

        print(f"[命中] {url[:120]}")

        try:
            data = await response.json()
        except Exception as e:
            print(f"[错误] JSON 解析失败: {e}")
            return

        # 耗时处理丢到后台，不阻塞页面继续加载
        asyncio.create_task(self._pattern_handlers[matched](data))


@dataclass
class SimilarityItem:
    offerPicUrl: str = field(default="")
    odPicUrl: str = field(default="")
    offerId: str = field(default="")
    skuId: str = field(default="")
    linkUrl: str = field(default="")


@dataclass
class Similarity:
    data: SimilarityItem = field(default_factory={})


# 相似图查询数据捕获
async def catch_similarity_network(items: List[Similarity]):

    ResNetSimilarityEngine()
    pass


# sku 数据捕获
