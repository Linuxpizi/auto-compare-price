from playwright.async_api import (
    async_playwright,
    Page,
    BrowserContext,
    APIRequestContext,
)

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
        await page.goto("https://login.1688.com")

        await asyncio.sleep(60)

        # other actions...
        await browser.close()

    async def main():
        async with async_playwright() as playwright:
            await run(playwright)

    asyncio.run(main())
