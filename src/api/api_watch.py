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
from typing import Callable, Coroutine, Any

from playwright.async_api import BrowserContext, Response


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

    async def _on_response(self, response: Response):
        """响应到达时的回调——快速过滤，耗时处理抛到后台。"""
        if not self._running:
            return

        url = response.url
        matched = next((p for p in self._pattern_handlers if p in url), None)
        if matched is None:
            return

        print(response.url)

        if not response.ok:
            print(f"[跳过] API 返回非正常状态: {response.status} -> {url[:120]}")
            return

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return

        try:
            data = await response.json()
        except Exception as e:
            print(f"[错误] JSON 解析失败: {e}")
            return

        # 耗时处理丢到后台，不阻塞页面继续加载
        asyncio.create_task(self._pattern_handlers[matched](data))
