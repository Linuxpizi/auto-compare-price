from random import random

from playwright.async_api import (
    async_playwright,
    Response,
)


async def _handle_watch_similarity_sku_network(response: Response):
    # 单个 SKU 详情
    if (
        "mtop.relationrecommend.wirelessrecommend.recommend" in response.request.url
        and response.ok
    ):

        request = response.request
        print("request.post_data_json", request.post_data_json)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>1111>")

        content_type = response.headers.get("content-type")
        if "application/json" in content_type:
            # try:
            #     # 3. 在try块中安全地解析JSON
            #     data = await response.json()
            #     print("API数据:", data)
            # except Exception as e:
            #     print(f"JSON解析失败: {e}")

            result = await response.text()
            print(result)

            print(";;;;")


if __name__ == "__main__":
    import asyncio
    from playwright.async_api import async_playwright, Playwright

    async def run(playwright: Playwright):
        chromium = playwright.chromium  # or "firefox" or "webkit".
        browser = await chromium.launch(
            headless=False,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        page = await browser.new_page()

        # page.once("response", _handle_watch_similarity_sku_network)

        await page.goto("https://1688.com")

        link = "https://g-search2.alicdn.com/img/bao/uploaded/i4/i1/2208909092216/O1CN01unRoXJ1SEyW2hT5Hf_!!2208909092216.jpg"
        await page.evaluate(f"navigator.clipboard.writeText('{link}')")
        await page.keyboard.press("Control+V")
        await asyncio.sleep(random())

        search_image_item = page.locator(
            "xpath=//div[@class='copy-image-container']//div[@data-tracker='pasteImagePreview']"
        )

        # page.on("response", _handle_watch_similarity_sku_network)

        await search_image_item.click(delay=random() + 0.3)

        # async with browser.contexts[0].expect_page() as new_page_info:
        #     await search_image_item.click(delay=random())
        #     new_page = await new_page_info.value

        #     # 方式1：使用 once 监听
        #     new_page.wait_for_event("response", _handle_watch_similarity_sku_network)
        #     # new_page.close()

        await asyncio.sleep(5)
        # other actions...
        await browser.close()

    async def main():
        async with async_playwright() as playwright:
            await run(playwright)

    asyncio.run(main())
