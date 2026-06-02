"""初始表结构

生成日期: 2026-06-03

包含:
- categories: 分类表
- transactions: 流水表
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(50), nullable=False, comment="分类名称"),
        sa.Column("type", sa.Enum("income", "expense", name="category_type"), nullable=False, comment="分类类型"),
        sa.Column("icon", sa.String(20), default="📁", comment="图标 emoji"),
        sa.Column("color", sa.String(7), default="#409EFF", comment="颜色 hex"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False, comment="金额"),
        sa.Column("type", sa.Enum("income", "expense", name="transaction_type"), nullable=False, comment="收支类型"),
        sa.Column("category_id", sa.Integer(), nullable=False, comment="分类ID"),
        sa.Column("description", sa.Text(), nullable=True, comment="备注"),
        sa.Column("date", sa.Date(), nullable=False, comment="交易日期"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, comment="创建时间"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("categories")
