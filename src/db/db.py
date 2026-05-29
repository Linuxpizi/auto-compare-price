import sqlite3
from typing import List, Optional
from dataclasses import dataclass, field
from os import path

sku_table = """
CREATE TABLE IF NOT EXISTS sku (
    origin_id TEXT PRIMARY KEY,
    origin_shop_name TEXT NOT NULL DEFAULT '',
    origin_primary_image_link TEXT NOT NULL DEFAULT '',
    origin_price TEXT NOT NULL DEFAULT '',

    match_link TEXT NOT NULL DEFAULT '',
    match_image_link TEXT NOT NULL DEFAULT '',
    match_score TEXT NOT NULL DEFAULT '',

    status INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (origin_id)
);
"""


@dataclass
class SKU:
    """
    店铺类，包含店铺名称、店铺链接和主图链接
    """

    # 原始信息
    origin_id: str = field(default="")
    origin_shop_name: str = field(default="")
    origin_primary_image_link: str = field(default="")
    origin_price: str = field(default="")  # 原始优惠价

    # 比价采集信息
    match_link: str = field(default="")
    match_image_link: float = field(default=0.0)
    match_score: float = field(default=0.0)

    status: int = field(
        default=0
    )  # 0 - 待处理, 1 - 已处理，2 - 已导出(已比对完成，导出 excel)， 99 - 删除

    def to_tuple(self):
        return (
            self.origin_id,
            self.origin_shop_name,
            self.origin_primary_image_link,
            self.origin_price,
            self.match_link,
            self.match_image_link,
            self.match_score,
        )  # 转换为元组


class DBConn:
    def __init__(self, db_path: str = "storage/db", db_name=".sku.db"):
        """
        Initialize a database connection.
        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.connection: sqlite3.Connection = sqlite3.connect(
            path.join(db_path, db_name)
        )
        self.connection.execute("PRAGMA journal_mode=WAL;")
        self.connection.execute("PRAGMA synchronous=NORMAL;")

    def get_conn(self) -> sqlite3.Connection:
        """
        Get the underlying SQLite connection object.
        Returns:
            sqlite3.Connection: SQLite connection instance.
        """
        return self.connection

    def close(self):
        """
        Close the database connection.
        """
        self.connection.close()

    def create_tables(self):
        """
        Create necessary tables in the database.
        """
        cursor = self.connection.cursor()
        cursor.executescript(sku_table)
        self.connection.commit()
        cursor.close()

    async def create_sku(self, info: SKU):
        try:
            conn = self.connection
            cursor = conn.cursor()
            cursor = cursor.execute(
                """
                INSERT INTO sku (
                    origin_id,
                    origin_shop_name,
                    origin_primary_image_link,
                    origin_price,
                    
                    match_link,
                    match_image_link,
                    match_score
                )
                VALUES
                    (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(origin_id)
                DO NOTHING
                """,
                (
                    info.origin_id,
                    info.origin_shop_name,
                    info.origin_primary_image_link,
                    info.origin_price,
                    info.match_link,
                    info.match_image_link,
                    info.match_score,
                ),
            )
            conn.commit()
            cursor.close()

        except Exception as e:
            conn.commit()
            cursor.close()

    def batch_create_sku(self, infos: List[SKU]):
        skus = [u.to_tuple() for u in infos]
        try:
            conn = self.connection
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            cursor.executemany(
                """
                INSERT INTO sku (
                    origin_id,
                    origin_shop_name,
                    origin_primary_image_link,
                    origin_price,
                    
                    match_link,
                    match_image_link,
                    match_score
                )
                VALUES
                    (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(origin_id)
                DO NOTHING
                """,
                skus,
            )
            cursor.execute("COMMIT")
            cursor.close()
        except Exception as e:
            print(
                "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd ",
                e,
            )

    async def delete_sku(self, origin_id: str = ""):
        conn = self.connection
        cursor = conn.cursor()
        cursor = cursor.execute(
            f"""
            UPDATE
                sku
            SET
                status = 99
            WHERE
                origin_id = ?
            """,
            (origin_id,),
        )
        conn.commit()
        cursor.close()

    async def modify_sku_status(
        self,
        origin_id: str,
    ):
        conn = self.connection
        cursor = conn.cursor()
        cursor = cursor.execute(
            """
                UPDATE
                    sku
                SET
                    status = 1
                WHERE
                    origin_id = ?
            """,
            (origin_id,),
        )

        conn.commit()
        cursor.close()

    async def get_sku(self, origin_id: str) -> Optional[SKU]:
        cursor = self.connection.cursor()
        cursor = cursor.execute(
            """
                SELECT
                    origin_id,
                    origin_shop_name,
                    origin_primary_image_link,
                    origin_price,
                    
                    match_link,
                    match_image_link,
                    match_score,
                    
                    status
                FROM
                    sku
                WHERE
                    origin_id = ?
            """,
            (origin_id,),
        )

        sku = cursor.fetchone()
        if sku:
            return SKU(sku[0])
        return None

    def query_sku(self, limit=50000) -> List[SKU]:
        cursor = self.connection.cursor()
        cursor = cursor.execute(f"""
            SELECT
                origin_id,
                origin_shop_name,
                origin_primary_image_link,
                origin_price,
                
                match_link,
                match_image_link,
                match_score,
            
                status
            FROM
                sku
            WHERE
                1 == 1
            LIMIT {limit if limit > 0 else 1000}
            """)
        skus = cursor.fetchall()
        out: List[SKU] = []
        for row in skus:
            out.append(
                SKU(
                    origin_id=row[0],
                    origin_shop_name=row[1],
                    origin_primary_image_link=row[2],
                    origin_price=row[3],
                    match_link=row[4],
                    match_image_link=row[5],
                    match_score=row[6],
                    status=row[7],
                )
            )
        return out

    # 获取随机 SKU
    async def get_random_sku(self) -> Optional[SKU]:
        cursor = self.connection.cursor()
        cursor = cursor.execute(
            """
                SELECT
                    origin_id,
                    origin_shop_name,
                    origin_primary_image_link,
                    origin_price,
                    
                    match_link,
                    match_image_link,
                    match_score,
                
                    status
                FROM
                    sku
                WHERE
                    status = 0
                ORDER BY
                    created_at ASC
                LIMIT 1
            """,
        )

        sku = cursor.fetchone()
        if sku:
            return SKU(sku[0])
        return None


if __name__ == "__main__":
    db = DBConn(".sku.db")
    db.create_tables()
    db.create_sku(SKU("1"))
    print(db.get_random_sku())
    print(db.query_sku())
