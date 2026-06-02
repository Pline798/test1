"""初始化数据库：创建默认分类"""
from app.database import engine, SessionLocal, Base
from app.models import Category

Base.metadata.create_all(bind=engine)

DEFAULT_CATEGORIES = [
    {"name": "工资", "type": "income", "icon": "💰", "color": "#67C23A"},
    {"name": "兼职", "type": "income", "icon": "💼", "color": "#409EFF"},
    {"name": "投资收益", "type": "income", "icon": "📈", "color": "#E6A23C"},
    {"name": "红包", "type": "income", "icon": "🧧", "color": "#F56C6C"},
    {"name": "其他收入", "type": "income", "icon": "💵", "color": "#909399"},
    {"name": "餐饮", "type": "expense", "icon": "🍜", "color": "#F56C6C"},
    {"name": "交通", "type": "expense", "icon": "🚌", "color": "#E6A23C"},
    {"name": "购物", "type": "expense", "icon": "🛒", "color": "#409EFF"},
    {"name": "住房", "type": "expense", "icon": "🏠", "color": "#67C23A"},
    {"name": "娱乐", "type": "expense", "icon": "🎮", "color": "#9B59B6"},
    {"name": "医疗", "type": "expense", "icon": "💊", "color": "#E74C3C"},
    {"name": "教育", "type": "expense", "icon": "📚", "color": "#3498DB"},
    {"name": "通讯", "type": "expense", "icon": "📱", "color": "#1ABC9C"},
    {"name": "其他支出", "type": "expense", "icon": "📦", "color": "#95A5A6"},
]


def init_seed_categories():
    """供 main.py lifespan 调用的种子数据函数，跳过已有数据的场景"""
    db = SessionLocal()
    try:
        existing = db.query(Category).count()
        if existing > 0:
            return
        for item in DEFAULT_CATEGORIES:
            db.add(Category(**item))
        db.commit()
        print(f"✅ 成功插入 {len(DEFAULT_CATEGORIES)} 条默认分类")
    finally:
        db.close()


def init():
    """独立运行时的完整初始化（含创建表）"""
    db = SessionLocal()
    try:
        existing = db.query(Category).count()
        if existing > 0:
            print(f"⚠️ 数据库已有 {existing} 条分类记录，跳过初始化")
            return
        for item in DEFAULT_CATEGORIES:
            db.add(Category(**item))
        db.commit()
        print(f"✅ 成功插入 {len(DEFAULT_CATEGORIES)} 条默认分类")
    finally:
        db.close()


if __name__ == "__main__":
    init()