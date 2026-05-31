import asyncio
import random
import cv2
import numpy as np
from playwright.async_api import async_playwright
from ultralytics import YOLO

# ---------- 初始化 OCR 和目标检测 ----------
model = YOLO("yolov8n.pt")  # 检测裙子等物体


# ---------- 工具函数 ----------
def generate_human_track(distance):
    """生成模拟人类拖拽的轨迹点（贝塞尔曲线）"""
    track = []
    current = 0
    mid = distance * 0.6
    while current < distance:
        if current < mid:
            move = random.randint(8, 18)
        else:
            move = random.randint(5, 12)
        current += move
        track.append(min(move, distance - current + move))
    return track


async def drag_to_end(page, slider_selector, track_selector):
    """
    全程按住鼠标，将滑块拖到最右端，返回拖拽过程中滑块的移动距离
    """
    slider = page.locator(slider_selector)
    track = page.locator(track_selector)

    slider_box = await slider.bounding_box()
    track_box = await track.bounding_box()
    max_distance = track_box["width"] - slider_box["width"]  # 需要滑动的总像素

    start_x = slider_box["x"] + slider_box["width"] / 2
    start_y = slider_box["y"] + slider_box["height"] / 2

    await page.mouse.move(start_x, start_y)
    await page.mouse.down()  # 按住不放

    track_points = generate_human_track(max_distance)
    current_x = start_x
    for step in track_points:
        current_x += step
        await page.mouse.move(current_x, start_y, steps=random.randint(3, 6))
        await asyncio.sleep(random.uniform(0.01, 0.03))

    # 此时滑块已到达最右端，但尚未松开
    return max_distance, start_x, start_y


def parse_tip_text(tip_text):
    """从提示文字中提取目标物体名称和所需数量，例如：找到两个裙子 -> ('裙子', 2)"""
    import re

    match = re.search(r"找到(\d+)([^0-9]+)", tip_text)
    if match:
        return match.group(2).strip(), int(match.group(1))
    return None, 0


def count_objects_in_image(image_bytes, target_name):
    """使用 YOLO 检测图片中目标物体的数量"""
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    results = model(img)
    detections = results[0].boxes
    count = 0
    for box in detections:
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id].lower()
        if target_name in class_name:  # 例如 'skirt' 包含在 'skirt' 中
            count += 1
    return count


async def solve_complex_slider(
    page, slider_selector, track_selector, canvas_selector, tip_selector
):
    """
    处理复杂滑块（一次性滑到底，识别完整图片，满足条件后松手）
    """
    # 1. 获取提示文字并解析
    tip_text = await page.locator(tip_selector).inner_text()
    target, required = parse_tip_text(tip_text)
    if not target:
        raise ValueError(f"无法解析提示: {tip_text}")
    print(f"需要找到 {required} 个 {target}")

    # 2. 拖拽到底（全程按住鼠标）
    await drag_to_end(page, slider_selector, track_selector)

    # 3. 截取滑块下方露出的完整图片区域（此时图片已完全显示）
    #    注意：有些网站图片是 canvas 元素，有些是 img，需要根据实际情况调整
    canvas = page.locator(canvas_selector)
    img_bytes = await canvas.screenshot()

    # 4. 识别目标数量
    found = count_objects_in_image(img_bytes, target)
    print(f"完整图片中检测到 {found} 个 {target}")

    # 5. 如果数量满足，松开鼠标（提交验证）；否则可能需要重试
    if found >= required:
        await page.mouse.up()
        print("验证成功")
        return True
    else:
        # 不满足条件时，不能松手（否则会刷新验证码），需要重置
        # 通常可以点击验证码区域的刷新按钮，或者刷新页面重新获取
        await page.mouse.up()  # 但这里松手会导致失败并刷新，可改为直接刷新页面
        print("验证失败，准备重试")
        return False


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        page = await browser.new_page()
        await page.goto("https://example.com")  # 替换为目标网址

        # 等待验证码出现
        await page.wait_for_selector(".slider-container", timeout=10000)

        # 判断验证码类型（简单/复杂），此处假设为复杂
        success = await solve_complex_slider(
            page,
            slider_selector=".slider-button",
            track_selector=".slider-track",
            canvas_selector=".slider-canvas",  # 图片展示区域
            tip_selector=".tip-text",
        )

        if not success:
            # 重试逻辑：刷新验证码或刷新页面
            refresh_btn = page.locator(".refresh-icon")
            if await refresh_btn.count():
                await refresh_btn.click()
                await asyncio.sleep(1)
                await solve_complex_slider(...)  # 递归或循环重试
            else:
                await page.reload()

        await asyncio.sleep(5)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
