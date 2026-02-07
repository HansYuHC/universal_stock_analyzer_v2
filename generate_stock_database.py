#!/usr/bin/env python3
"""
生成股票数据库 - 修复分类问题
"""
import json
import os
import sys
from datetime import datetime

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DATABASE_PATH = os.path.join(DATA_DIR, "stock_database_fixed.json")


# 直接加载你现有的数据库
def load_existing_database():
    """加载现有数据库"""
    existing_path = os.path.join(DATA_DIR, "stock_database.json")
    if os.path.exists(existing_path):
        with open(existing_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def improved_categorize_stock(symbol, name):
    """改进版股票分类"""
    name_lower = name.lower()

    # 先检查symbol中的模式
    symbol_lower = symbol.lower()

    # 技术股特征词（更全面）
    tech_keywords = [
        'tech', 'software', 'hardware', 'semiconductor', 'internet',
        'cloud', 'digital', 'data', 'network', 'cyber', 'comput',
        'electronic', 'software', 'platform', 'systems', 'solution',
        'analytics', 'intelligence', 'ai', 'machine learning',
        'mobile', 'web', 'online', 'ecommerce', 'social media',
        'gaming', 'streaming', 'media', 'entertainment', 'content'
    ]

    # 金融股特征词
    finance_keywords = [
        'bank', 'financial', 'finance', 'insurance', 'credit',
        'capital', 'payment', 'investment', 'asset', 'wealth',
        'broker', 'exchange', 'trading', 'card', 'money',
        'lending', 'mortgage', 'loan', 'fund', 'trust',
        'holding', 'group', 'partners', 'advisors'
    ]

    # 医疗保健特征词
    healthcare_keywords = [
        'health', 'medical', 'pharma', 'biotech', 'care',
        'diagnostic', 'therapeutic', 'surgical', 'hospital',
        'clinic', 'laboratory', 'medicine', 'drug', 'vaccine',
        'treatment', 'therapy', 'device', 'imaging', 'scan',
        'patient', 'doctor', 'nurse', 'wellness', 'fitness'
    ]

    # 消费股特征词
    consumer_keywords = [
        'retail', 'store', 'shop', 'market', 'mall',
        'consumer', 'goods', 'product', 'brand', 'apparel',
        'clothing', 'shoe', 'footwear', 'fashion', 'luxury',
        'food', 'beverage', 'drink', 'restaurant', 'cafe',
        'hotel', 'travel', 'tourism', 'leisure', 'entertainment',
        'auto', 'car', 'vehicle', 'motor', 'home', 'house',
        'furniture', 'appliance', 'garden', 'pet', 'animal'
    ]

    # 工业股特征词
    industrial_keywords = [
        'industrial', 'manufactur', 'factory', 'plant',
        'machinery', 'equipment', 'tool', 'machine',
        'engineering', 'construction', 'build', 'contractor',
        'defense', 'aerospace', 'aviation', 'aircraft',
        'marine', 'naval', 'ship', 'boat', 'rail',
        'transport', 'logistics', 'shipping', 'delivery',
        'mining', 'metal', 'steel', 'aluminum', 'copper',
        'chemical', 'paint', 'coating', 'material', 'composite'
    ]

    # 能源股特征词
    energy_keywords = [
        'energy', 'power', 'electric', 'utility', 'gas',
        'oil', 'petroleum', 'fuel', 'diesel', 'gasoline',
        'renewable', 'solar', 'wind', 'hydro', 'nuclear',
        'coal', 'mineral', 'resource', 'exploration', 'drilling',
        'pipeline', 'transmission', 'distribution', 'grid',
        'generation', 'plant', 'facility', 'refinery'
    ]

    # 通信股特征词
    communication_keywords = [
        'communication', 'telecom', 'telephone', 'phone',
        'wireless', 'cellular', 'mobile', 'broadband',
        'internet', 'network', 'cable', 'fiber', 'satellite',
        'media', 'broadcast', 'television', 'tv', 'radio',
        'newspaper', 'magazine', 'publishing', 'advertising',
        'marketing', 'public relations', 'agency', 'studio'
    ]

    # 房地产股特征词
    real_estate_keywords = [
        'real estate', 'property', 'estate', 'reit',
        'development', 'developer', 'builder', 'construction',
        'management', 'manager', 'leasing', 'rental',
        'apartment', 'condo', 'office', 'commercial',
        'industrial', 'warehouse', 'storage', 'logistics',
        'mall', 'shopping center', 'retail center', 'hotel',
        'resort', 'hospitality', 'lodging', 'accommodation'
    ]

    # 公用事业股特征词
    utilities_keywords = [
        'utility', 'utilities', 'electric', 'power',
        'gas', 'water', 'waste', 'sewage', 'sanitation',
        'environmental', 'clean', 'green', 'sustainable',
        'renewable', 'solar', 'wind', 'hydro', 'geothermal'
    ]

    # 检查每个分类
    for keyword in tech_keywords:
        if keyword in name_lower:
            return 'technology'

    for keyword in finance_keywords:
        if keyword in name_lower:
            return 'financial'

    for keyword in healthcare_keywords:
        if keyword in name_lower:
            return 'healthcare'

    for keyword in consumer_keywords:
        if keyword in name_lower:
            return 'consumer'

    for keyword in industrial_keywords:
        if keyword in name_lower:
            return 'industrial'

    for keyword in energy_keywords:
        if keyword in name_lower:
            return 'energy'

    for keyword in communication_keywords:
        if keyword in name_lower:
            return 'communication'

    for keyword in real_estate_keywords:
        if keyword in name_lower:
            return 'real_estate'

    for keyword in utilities_keywords:
        if keyword in name_lower:
            return 'utilities'

    # 基于symbol的特殊规则
    if symbol_lower.endswith('.b'):
        return 'financial'  # Berkshire Hathaway等

    # 常见科技公司
    tech_symbols = ['aapl', 'msft', 'googl', 'amzn', 'meta', 'nvda', 'tsla', 'intc', 'amd', 'adbe', 'crm', 'csco',
                    'orcl', 'ibm', 'qcom', 'txn', 'avgo']
    if symbol_lower in tech_symbols:
        return 'technology'

    # 常见金融公司
    finance_symbols = ['jpm', 'bac', 'wfc', 'c', 'gs', 'ms', 'schw', 'blk', 'axp', 'v', 'ma', 'fisv', 'fis', 'brk.b']
    if symbol_lower in finance_symbols:
        return 'financial'

    # 常见医疗公司
    healthcare_symbols = ['jnj', 'pfe', 'mrk', 'abt', 'tmo', 'unh', 'lly', 'amgn', 'gild', 'bmy', 'isrg']
    if symbol_lower in healthcare_symbols:
        return 'healthcare'

    # 常见消费公司
    consumer_symbols = ['wmt', 'pg', 'ko', 'pep', 'mcd', 'sbux', 'nke', 'dis', 'cost', 'hd', 'low', 'tgt']
    if symbol_lower in consumer_symbols:
        return 'consumer'

    return 'other'


def fix_categories_in_database():
    """修复数据库中的分类"""
    print("🔧 正在修复股票数据库分类...")

    # 加载现有数据库
    data = load_existing_database()
    if not data:
        print("❌ 找不到现有数据库")
        return

    stocks = data.get("stocks", [])
    print(f"   加载了 {len(stocks)} 只股票")

    # 修复分类
    fixed_count = 0
    for stock in stocks:
        if stock.get("is_correction"):
            # 修正条目保持原样
            continue

        old_category = stock.get("category", "unknown")
        new_category = improved_categorize_stock(stock["symbol"], stock["name"])

        if old_category != new_category:
            stock["category"] = new_category
            fixed_count += 1

    # 统计新分类
    categories = {}
    for stock in stocks:
        cat = stock.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    # 更新数据库
    data["stocks"] = stocks
    data["last_updated"] = datetime.now().isoformat()
    data["version"] = "2.1"
    data["categories"] = categories

    # 保存到新文件
    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ 分类修复完成！")
    print(f"   修复了 {fixed_count} 只股票的分类")
    print(f"   保存位置: {DATABASE_PATH}")

    # 显示分类统计
    print("\n📊 新的分类统计:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat:15s}: {count:3d} 只股票")

    # 显示一些示例
    print("\n🔍 示例股票分类:")
    example_stocks = [
        ("AAPL", "Apple Inc."),
        ("JPM", "JPMorgan Chase & Co."),
        ("JNJ", "Johnson & Johnson"),
        ("WMT", "Walmart Inc."),
        ("CAT", "Caterpillar Inc."),
        ("XOM", "Exxon Mobil Corporation"),
        ("CMCSA", "Comcast Corporation"),
        ("PLD", "Prologis Inc."),
        ("NEE", "NextEra Energy"),
        ("TSLA", "Tesla Inc."),
    ]

    for symbol, name in example_stocks:
        category = improved_categorize_stock(symbol, name)
        print(f"   {symbol:6s} - {name[:25]:25s} → {category}")

    return data


if __name__ == "__main__":
    try:
        fix_categories_in_database()
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)