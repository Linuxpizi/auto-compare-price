import base64
import numpy as np
from typing import List, Tuple
import dashscope

# ========== 配置部分 ==========
# 从阿里云百炼平台获取（https://bailian.console.aliyun.com）
DASHSCOPE_API_KEY = ""

# 百炼模型 API 地址
EMBEDDING_MODEL = "qwen2.5-vl-embedding"
# https://dashscope.aliyuncs.com/compatible-mode/v1

#
API_URL = "https://dashscope.aliyuncs.com/api/v1"


# ========== 辅助函数 ==========
def encode_image_to_base64(image_path: str) -> str:
    """将图片文件转为 Base64 编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_embedding(image_path: str) -> List[float]:
    """
    调用百炼 API 获取图片的向量表示（Embedding）

    参数:
        image_path: 图片文件路径

    返回:
        向量列表（通常是 1536 维或 2048 维）
    """
    image_base64 = encode_image_to_base64(image_path)

    try:

        completion = dashscope.MultiModalEmbedding.call(
            model="qwen3-vl-embedding",
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
            api_key=DASHSCOPE_API_KEY,
            input=[{"image": f"data:image/jpeg;base64,{image_base64}"}],
        )
        # completion = client.embeddings.create(
        # completion = client.embeddings.create(
        # model="qwen3-vl-embedding",  # qwen-vl-plus
        # messages=[
        #     {
        #         "role": "user",
        #         "content": [
        #             {
        #                 "type": "image_url",
        #                 "image_url": {
        #                     "url": f"data:image/jpeg;base64,{image_base64}"
        #                 },
        #             }
        #         ],
        #     }
        # ],
        #     input={"contents": [{"image": f"data:image/jpeg;base64,{image_base64}"}]},
        # )
        print("completion.output -> ", completion.output)
        embedding = completion.output["embeddings"][0]["embedding"]
        return embedding

    except Exception as e:
        print(f"获取图片向量失败 [{image_path}]: {e}")


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    计算两个向量的余弦相似度

    返回值范围: [-1, 1]
    - 越接近 1: 越相似
    - 越接近 0: 不相关
    - 越接近 -1: 越相反
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    # 避免除零
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(np.dot(v1, v2) / (norm1 * norm2))


# ========== 核心类：图片相似度检测引擎 ==========
class ImageSimilarityEngine:
    """
    基于 Qwen2.5-VL-Embedding 的图片相似度检测引擎
    """

    def __init__(self):
        self.embeddings_cache = {}

    def compute_similarity(
        self, query_image: str, target_images: List[str]
    ) -> List[Tuple[str, float]]:
        """
        计算查询图片与一组目标图片的相似度

        参数:
            query_image: 原始图片 A 的路径
            target_images: 目标图片列表 [b.jpg, c.jpg, d.jpg, ...]

        返回:
            列表，每个元素为 (图片路径, 相似度得分)，按相似度从高到低排序
        """
        print(f"📷 正在处理查询图片: {query_image}")
        query_embedding = self._get_embedding_with_cache(query_image)

        results = []
        for i, target_path in enumerate(target_images, 1):
            print(f"🔄 正在处理目标图片 [{i}/{len(target_images)}]: {target_path}")
            target_embedding = self._get_embedding_with_cache(target_path)

            similarity = cosine_similarity(query_embedding, target_embedding)
            results.append((target_path, similarity))

        # 按相似度从高到低排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def _get_embedding_with_cache(self, image_path: str) -> List[float]:
        """获取图片向量（带缓存）"""
        if image_path not in self.embeddings_cache:
            self.embeddings_cache[image_path] = get_image_embedding(image_path)
        return self.embeddings_cache[image_path]

    def clear_cache(self):
        """清空向量缓存"""
        self.embeddings_cache.clear()


# ========== 使用示例 ==========
def main():
    # 1. 初始化引擎
    engine = ImageSimilarityEngine()

    # 2. 准备图片路径
    query_image = "11.jpg"  # 原始图 A
    target_images = [
        "22.jpg",
        "33.jpg",
        "44.webp",
    ]

    # 3. 计算相似度
    print("=" * 50)
    print("开始计算图片相似度...")
    print("=" * 50)

    results = engine.compute_similarity(query_image, target_images)

    # 4. 输出结果
    print("\n" + "=" * 50)
    print("相似度计算结果 (按相似度从高到低排序):")
    print("=" * 50)

    for i, (image_path, score) in enumerate(results, 1):
        # 将相似度转换为百分比
        percentage = score * 100
        # 相似度评级
        if score >= 0.8:
            rating = "🔴 高度相似"
        elif score >= 0.6:
            rating = "🟡 较为相似"
        elif score >= 0.4:
            rating = "🟢 一般相似"
        else:
            rating = "⚪ 不太相似"

        print(f"{i}. 📷 {image_path}")
        print(f"   相似度得分: {score:.6f} ({percentage:.2f}%)")
        print(f"   评级: {rating}")
        print("-" * 40)

    # 可选：清空缓存
    # engine.clear_cache()


if __name__ == "__main__":
    main()
