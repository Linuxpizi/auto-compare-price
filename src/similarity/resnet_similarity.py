import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
from typing import List, Tuple
from pathlib import Path
import warnings
from io import BytesIO
from urllib.request import urlopen

warnings.filterwarnings("ignore")


# ========== 特征提取器 ==========
class FeatureExtractor:
    """轻量级特征提取器"""

    def __init__(self, model_name: str = "resnet50", use_gpu: bool = False, model_path: str | None = None):
        """
        初始化特征提取器

        Args:
            model_name: 模型名称 (resnet50, resnet101, efficientnet_b0, vit_b_16)
            use_gpu: 是否使用GPU
            model_path: 自定义模型权重路径，指定后从此路径加载权重而非从网络下载
        """
        self.device = torch.device(
            "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        )

        # 加载模型
        self.model = self._load_model(model_name, model_path)
        self.model = self.model.to(self.device)
        self.model.eval()

        # 图像预处理
        self.transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        # 特征维度映射
        self.feature_dims = {
            "resnet50": 2048,
            "resnet101": 2048,
            "efficientnet_b0": 1280,
            "vit_b_16": 768,
        }
        self.feature_dim = self.feature_dims.get(model_name, 2048)

        print(
            f"✅ 初始化完成 | 模型: {model_name} | 特征维度: {self.feature_dim} | 设备: {self.device}"
            + (f" | 本地权重: {model_path}" if model_path else "")
        )

    def _load_model(self, model_name: str, model_path: str | None = None):
        """加载预训练模型"""
        if model_path:
            return self._load_from_local(model_name, model_path)

        if model_name == "resnet50":
            model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
            model = torch.nn.Sequential(*list(model.children())[:-1])
        elif model_name == "resnet101":
            model = models.resnet101(weights=models.ResNet101_Weights.IMAGENET1K_V1)
            model = torch.nn.Sequential(*list(model.children())[:-1])
        elif model_name == "efficientnet_b0":
            model = models.efficientnet_b0(
                weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1
            )
            model = torch.nn.Sequential(*list(model.children())[:-1])
        elif model_name == "vit_b_16":
            model = models.vit_b_16(weights=models.ViT_B_16_Weights.IMAGENET1K_V1)
            model.heads = torch.nn.Identity()
        else:
            raise ValueError(f"不支持的模型: {model_name}")
        return model

    def _load_from_local(self, model_name: str, model_path: str):
        """从本地路径加载模型权重"""
        if not Path(model_path).exists():
            raise FileNotFoundError(f"模型权重文件不存在: {model_path}")

        # 先创建不带权重的模型骨架
        if model_name == "resnet50":
            model = models.resnet50(weights=None)
            model = torch.nn.Sequential(*list(model.children())[:-1])
        elif model_name == "resnet101":
            model = models.resnet101(weights=None)
            model = torch.nn.Sequential(*list(model.children())[:-1])
        elif model_name == "efficientnet_b0":
            model = models.efficientnet_b0(weights=None)
            model = torch.nn.Sequential(*list(model.children())[:-1])
        elif model_name == "vit_b_16":
            model = models.vit_b_16(weights=None)
            model.heads = torch.nn.Identity()
        else:
            raise ValueError(f"不支持的模型: {model_name}")

        # 加载本地权重
        state_dict = torch.load(model_path, map_location=self.device, weights_only=True)
        model.load_state_dict(state_dict, strict=False)
        print(f"  📂 已加载本地权重: {model_path}")
        return model

    @torch.no_grad()
    def extract(self, image_path: str) -> np.ndarray:
        """
        提取单张图片的特征向量

        Args:
            image_path: 图片路径（本地路径或网络URL）

        Returns:
            特征向量 (feature_dim,)
        """
        # 加载图片（支持本地路径和网络URL）
        if image_path.startswith(("http://", "https://")):
            img = Image.open(BytesIO(urlopen(image_path).read())).convert("RGB")
        else:
            img = Image.open(image_path).convert("RGB")

        # 预处理
        img_tensor = self.transform(img).unsqueeze(0).to(self.device)

        # 提取特征
        features = self.model(img_tensor).cpu().numpy().flatten()

        # L2归一化（使后续余弦相似度计算更准确）
        features = features / (np.linalg.norm(features) + 1e-8)

        return features.astype("float32")

    def extract_batch(self, image_paths: List[str]) -> List[np.ndarray]:
        """
        批量提取多张图片的特征

        Args:
            image_paths: 图片路径列表

        Returns:
            特征向量列表
        """
        features = []
        for path in image_paths:
            try:
                feat = self.extract(path)
                features.append(feat)
            except Exception as e:
                print(f"⚠️ 提取失败 [{path}]: {e}")
                features.append(np.zeros(self.feature_dim, dtype="float32"))
        return features


# ========== 相似度计算器 ==========
class SimilarityCalculator:
    """图片相似度计算器"""

    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        余弦相似度

        Returns:
            相似度得分 [0, 1]，1表示完全相似
        """
        # 已经L2归一化，直接点积即可
        similarity = float(np.dot(vec1, vec2))
        # 确保在[0,1]范围内
        return max(0.0, min(1.0, similarity))

    @staticmethod
    def euclidean_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        欧氏距离转相似度

        Returns:
            相似度得分 [0, 1]，1表示完全相似
        """
        distance = np.linalg.norm(vec1 - vec2)
        # 将距离转换为相似度（距离越小相似度越高）
        similarity = 1.0 / (1.0 + distance)
        return similarity

    @staticmethod
    def pearson_correlation(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        皮尔逊相关系数

        Returns:
            相关系数 [-1, 1]，1表示完全正相关
        """
        v1 = vec1 - np.mean(vec1)
        v2 = vec2 - np.mean(vec2)

        denominator = np.sqrt(np.sum(v1**2)) * np.sqrt(np.sum(v2**2))
        if denominator == 0:
            return 0.0

        correlation = np.sum(v1 * v2) / denominator
        return float(correlation)


# ========== 主引擎（无状态） ==========
class ResNetSimilarityEngine:
    """
    轻量级图片相似度计算引擎
    无缓存、无索引库，每次调用实时计算
    """

    def __init__(self, model_name: str = "resnet50", use_gpu: bool = False, model_path: str | None = None):
        """
        初始化引擎

        Args:
            model_name: 特征提取模型 (resnet50, resnet101, efficientnet_b0, vit_b_16)
            use_gpu: 是否使用GPU加速
            model_path: 自定义模型权重路径，指定后从此路径加载权重而非从网络下载
        """
        self.extractor = FeatureExtractor(model_name, use_gpu, model_path)
        self.calculator = SimilarityCalculator()

    def compare_pair(
        self, src_image: str, target_image: str, method: str = "cosine"
    ) -> float:
        """
        比较两张图片的相似度

        Args:
            src_image: 图片1路径
            target_image: 图片2路径
            method: 相似度计算方法 (cosine, euclidean, pearson)

        Returns:
            相似度得分 [0, 1]，1表示完全相似
        """
        # 提取特征
        feat1 = self.extractor.extract(src_image)
        feat2 = self.extractor.extract(target_image)

        # 计算相似度
        if method == "cosine":
            return self.calculator.cosine_similarity(feat1, feat2)
        elif method == "euclidean":
            return self.calculator.euclidean_similarity(feat1, feat2)
        elif method == "pearson":
            sim = self.calculator.pearson_correlation(feat1, feat2)
            # 将[-1,1]映射到[0,1]
            return (sim + 1) / 2
        else:
            raise ValueError(f"不支持的相似度方法: {method}")

    def compare_query_to_targets(
        self,
        query_image: str,
        target_images: List[str],
        method: str = "cosine",
        sort: bool = True,
    ) -> List[Tuple[str, float]]:
        """
        将查询图片与一组目标图片进行比较

        Args:
            query_path: 查询图片路径
            target_paths: 目标图片路径列表
            method: 相似度计算方法
            sort: 是否按相似度排序

        Returns:
            [(图片路径, 相似度得分), ...]
        """
        print(f"📷 提取查询图片特征: {query_image}")
        query_feat = self.extractor.extract(query_image)

        results = []
        total = len(target_images)

        for i, target_path in enumerate(target_images, 1):
            print(f"🔄 处理目标图片 [{i}/{total}]: {target_path}")

            try:
                target_feat = self.extractor.extract(target_path)

                if method == "cosine":
                    sim = self.calculator.cosine_similarity(query_feat, target_feat)
                elif method == "euclidean":
                    sim = self.calculator.euclidean_similarity(query_feat, target_feat)
                elif method == "pearson":
                    sim = self.calculator.pearson_correlation(query_feat, target_feat)
                    sim = (sim + 1) / 2
                else:
                    raise ValueError(f"不支持的相似度方法: {method}")

                results.append((target_path, sim))
            except Exception as e:
                print(f"  ❌ 失败: {e}")
                results.append((target_path, 0.0))

        # 按相似度排序
        if sort:
            results.sort(key=lambda x: x[1], reverse=True)

        return results

    def compare_matrix(
        self, images: List[str], method: str = "cosine"
    ) -> np.ndarray:
        """
        计算多张图片之间的相似度矩阵

        Args:
            image_paths: 图片路径列表
            method: 相似度计算方法

        Returns:
            相似度矩阵 (n, n)，其中matrix[i][j]表示第i张和第j张的相似度
        """
        n = len(images)
        similarity_matrix = np.zeros((n, n))

        # 批量提取所有特征
        print(f"📷 提取 {n} 张图片的特征...")
        features = self.extractor.extract_batch(images)

        # 计算相似度矩阵
        print("📊 计算相似度矩阵...")
        for i in range(n):
            for j in range(i, n):
                if method == "cosine":
                    sim = self.calculator.cosine_similarity(features[i], features[j])
                elif method == "euclidean":
                    sim = self.calculator.euclidean_similarity(features[i], features[j])
                elif method == "pearson":
                    sim = self.calculator.pearson_correlation(features[i], features[j])
                    sim = (sim + 1) / 2
                else:
                    raise ValueError(f"不支持的相似度方法: {method}")

                similarity_matrix[i][j] = sim
                similarity_matrix[j][i] = sim

        return similarity_matrix


# ========== 使用示例 ==========
def main():
    # 1. 初始化引擎
    engine = ResNetSimilarityEngine(model_name="resnet50", use_gpu=False)

    # 2. 场景一：比较两张图片
    print("\n" + "=" * 60)
    print("场景一：比较两张图片")
    print("=" * 60)

    # sim = engine.compare_pair(
    #     "src/asserts/images/c0.webp", "src/asserts/images/c3.webp", method="cosine"
    # )
    # print(f"✅ 余弦相似度: {sim:.4f} ({sim*100:.2f}%)")

    sim2 = engine.compare_pair(
        "./111.jpg", "./2222.webp", method="cosine"
    )
    print(f"✅ 余弦相似度: {sim2:.4f} ({sim2*100:.2f}%)")

    sim3 = engine.compare_pair(
        "./111.jpg", "./33333.webp", method="cosine"
    )
    print(f"✅ 余弦相似度: {sim3:.4f} ({sim3*100:.2f}%)")

    # 3. 场景二：查询图片与一组图片比较
    print("\n" + "=" * 60)
    print("场景二：查询图片与目标库比较")
    print("=" * 60)

    query = "src/asserts/images/c0.webp"
    target_images = [
        "src/asserts/images/c2.webp",
        "src/asserts/images/c3.webp",
        "src/asserts/images/c4.webp",
        "src/asserts/images/c5.webp",
        "src/asserts/images/c6.webp",
        "src/asserts/images/c7.webp",
        # ... 更多图片
    ]

    results = engine.compare_query_to_targets(
        query, target_images, method="cosine", sort=True
    )

    print(f"\n📷 查询图片: {query}")
    print("相似度排名:")
    for i, (path, score) in enumerate(results, 1):
        # 相似度评级
        if score >= 0.9:
            rating = "🔴 极其相似"
        elif score >= 0.7:
            rating = "🟠 高度相似"
        elif score >= 0.5:
            rating = "🟡 较为相似"
        elif score >= 0.3:
            rating = "🟢 一般相似"
        else:
            rating = "⚪ 不太相似"

        print(f"{i}. {path}")
        print(f"   相似度: {score:.4f} ({score*100:.2f}%) | {rating}")
        print("-" * 40)

    # 4. 场景三：批量比较（相似度矩阵）
    print("\n" + "=" * 60)
    print("场景三：批量比较（相似度矩阵）")
    print("=" * 60)

    images = [
        "src/asserts/images/11.jpg",
        "src/asserts/images/22.jpg",
        "src/asserts/images/33.jpg",
        "src/asserts/images/44.webp",
    ]

    if all(Path(p).exists() for p in images):
        sim_matrix = engine.compare_matrix(images, method="cosine")

        print("\n相似度矩阵:")
        print("     ", end="")
        for i, path in enumerate(images):
            print(f"{i+1:>8}", end="")
        print()

        for i in range(len(images)):
            print(f"{i+1}: ", end="")
            for j in range(len(images)):
                print(f"{sim_matrix[i][j]:>8.4f}", end="")
            print()
    else:
        print("⚠️ 示例图片不存在，跳过相似度矩阵计算")


# ========== 便捷函数（直接调用） ==========
def quick_compare(src_image: str, target_image: str, model: str = "resnet50", model_path: str | None = None) -> float:
    """
    快速比较两张图片的相似度

    Args:
        img1: 图片1路径
        img2: 图片2路径
        model: 特征提取模型
        model_path: 自定义模型权重路径

    Returns:
        相似度得分
    """
    engine = ResNetSimilarityEngine(model_name=model, use_gpu=False, model_path=model_path)
    return engine.compare_pair(src_image, target_image)


if __name__ == "__main__":
    main()
