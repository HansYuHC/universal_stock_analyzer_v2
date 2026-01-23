import json
import os
import hashlib
from datetime import datetime, timedelta
import pickle


def get_cache_key(ticker: str, data_type: str = "all") -> str:
    """生成缓存键"""
    key_str = f"{ticker}_{data_type}_{datetime.now().strftime('%Y%m%d')}"
    return hashlib.md5(key_str.encode()).hexdigest()[:12]


def get_cache_path(ticker: str, data_type: str = "all") -> str:
    """获取缓存文件路径"""
    cache_dir = "data/cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_key = get_cache_key(ticker, data_type)
    return os.path.join(cache_dir, f"{ticker}_{cache_key}.pkl")


def is_cache_valid(cache_path: str, expiry_hours: int = 6) -> bool:
    """检查缓存是否有效（默认6小时）"""
    if not os.path.exists(cache_path):
        return False

    # 检查文件修改时间
    cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
    cache_age = datetime.now() - cache_time
    return cache_age.total_seconds() < expiry_hours * 3600


def load_from_cache(ticker: str, data_type: str = "all") -> dict:
    """从缓存加载数据"""
    cache_path = get_cache_path(ticker, data_type)

    if is_cache_valid(cache_path):
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
                # 添加缓存标记
                data['_cache'] = {
                    'cached': True,
                    'cache_time': os.path.getmtime(cache_path),
                    'cache_path': cache_path
                }
                return data
        except Exception as e:
            print(f"缓存加载失败: {e}")

    return None


def save_to_cache(data: dict, ticker: str, data_type: str = "all"):
    """保存数据到缓存"""
    cache_path = get_cache_path(ticker, data_type)

    try:
        # 删除可能存在的缓存标记
        if '_cache' in data:
            del data['_cache']

        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)

        # 清理旧缓存（最多保留20个文件）
        cleanup_old_cache(ticker)

        return True
    except Exception as e:
        print(f"缓存保存失败: {e}")
        return False


def cleanup_old_cache(ticker: str, max_files: int = 20):
    """清理旧缓存文件"""
    cache_dir = "data/cache"
    if not os.path.exists(cache_dir):
        return

    # 获取该ticker的所有缓存文件
    cache_files = []
    for filename in os.listdir(cache_dir):
        if filename.startswith(f"{ticker}_"):
            filepath = os.path.join(cache_dir, filename)
            mtime = os.path.getmtime(filepath)
            cache_files.append((filepath, mtime))

    # 按修改时间排序，保留最新的
    cache_files.sort(key=lambda x: x[1], reverse=True)

    # 删除旧文件
    for filepath, _ in cache_files[max_files:]:
        try:
            os.remove(filepath)
        except:
            pass


def get_cache_stats() -> dict:
    """获取缓存统计信息"""
    cache_dir = "data/cache"
    if not os.path.exists(cache_dir):
        return {'total_files': 0, 'total_size_mb': 0, 'stocks': []}

    files = os.listdir(cache_dir)
    total_size = sum(
        os.path.getsize(os.path.join(cache_dir, f)) for f in files if os.path.isfile(os.path.join(cache_dir, f)))

    # 按股票统计
    stock_files = {}
    for filename in files:
        if filename.endswith('.pkl'):
            ticker = filename.split('_')[0]
            stock_files.setdefault(ticker, 0)
            stock_files[ticker] += 1

    return {
        'total_files': len(files),
        'total_size_mb': total_size / (1024 * 1024),
        'stocks': list(stock_files.keys()),
        'stock_counts': stock_files
    }


def detect_industry(ticker, stock_data=None):
    """改进的行业检测"""
    ticker = ticker.upper()

    # 如果提供了股票数据，优先使用
    if stock_data and stock_data.get('basic_info', {}).get('sector'):
        basic_info = stock_data['basic_info']
        sector = basic_info.get('sector', '').lower()
        industry = basic_info.get('industry', '').lower()

        print(f"   检测行业: sector={sector}, industry={industry}")

        # 详细的行业映射
        sector_industry_map = {
            # 科技行业
            'technology': 'software',
            'technology services': 'software',
            'electronic technology': 'software',
            'software': 'software',
            'internet': 'software',

            # 能源行业
            'energy': 'energy',
            'energy minerals': 'energy',
            'oil & gas': 'energy',
            'oil & gas production': 'energy',
            'pipelines': 'energy',

            # 金融行业
            'financial services': 'financial',
            'finance': 'financial',
            'banking': 'financial',
            'investment': 'financial',
            'credit services': 'financial',
            'insurance': 'financial',
            'insurance companies': 'financial',

            # 医疗保健
            'healthcare': 'healthcare',
            'health technology': 'healthcare',
            'pharmaceuticals': 'healthcare',
            'biotechnology': 'healthcare',
            'medical': 'healthcare',

            # 工业
            'industrials': 'industrial',
            'industrial services': 'industrial',
            'manufacturing': 'industrial',
            'machinery': 'industrial',
            'engineering & construction': 'industrial',
            'aerospace & defense': 'industrial',
            'transportation': 'industrial',

            # 消费品
            'consumer defensive': 'consumer_staples',
            'consumer staples': 'consumer_staples',
            'consumer products': 'consumer_staples',
            'beverages': 'consumer_staples',
            'food & staples retailing': 'consumer_staples',
            'food products': 'consumer_staples',

            # 消费周期
            'consumer cyclical': 'consumer_discretionary',
            'consumer discretionary': 'consumer_discretionary',
            'retail': 'consumer_discretionary',
            'automobiles': 'consumer_discretionary',
            'apparel': 'consumer_discretionary',
            'entertainment': 'consumer_discretionary',

            # 公用事业
            'utilities': 'utilities',

            # 电信
            'communication services': 'communication',
            'telecommunications': 'communication',

            # 房地产
            'real estate': 'real_estate',
            'reit': 'real_estate',

            # 材料
            'basic materials': 'materials',
            'materials': 'materials',
            'chemicals': 'materials',
            'metals & mining': 'materials',
        }

        # 首先根据sector判断
        for key, value in sector_industry_map.items():
            if key in sector:
                return value

        # 然后根据industry判断
        for key, value in sector_industry_map.items():
            if key in industry:
                return value

        # 检查行业字段中的关键词
        if any(word in industry for word in ['bank', 'credit', 'insurance', 'financial', 'asset', 'capital']):
            return 'financial'
        if any(word in industry for word in ['oil', 'gas', 'energy', 'petroleum', 'drilling', 'exploration']):
            return 'energy'
        if any(word in industry for word in ['medical', 'pharma', 'health', 'biotech', 'drug', 'healthcare']):
            return 'healthcare'
        if any(word in industry for word in ['manufactur', 'industrial', 'machine', 'engineering', 'construction']):
            return 'industrial'
        if any(word in industry for word in ['beverage', 'food', 'consumer', 'staples', 'retail', 'product']):
            return 'consumer_staples'

    # 备用：常见公司映射（扩展到更多股票）
    ticker_map = {
        # 消费品（饮料/食品）
        'KO': 'consumer_staples',  # 可口可乐
        'PEP': 'consumer_staples',  # 百事可乐
        'PG': 'consumer_staples',  # 宝洁
        'UL': 'consumer_staples',  # 联合利华
        'NESTLE': 'consumer_staples',  # 雀巢
        'WMT': 'consumer_staples',  # 沃尔玛
        'COST': 'consumer_staples',  # 好市多
        'MCD': 'consumer_staples',  # 麦当劳
        'SBUX': 'consumer_staples',  # 星巴克

        # 金融
        'JPM': 'financial', 'BAC': 'financial', 'WFC': 'financial',
        'C': 'financial', 'GS': 'financial', 'MS': 'financial',
        'SCHW': 'financial', 'BLK': 'financial', 'AXP': 'financial',
        'PYPL': 'financial', 'V': 'financial', 'MA': 'financial',

        # 能源
        'XOM': 'energy', 'CVX': 'energy', 'COP': 'energy',
        'SLB': 'energy', 'EOG': 'energy', 'MPC': 'energy',
        'PSX': 'energy', 'VLO': 'energy', 'OXY': 'energy',

        # 医疗
        'JNJ': 'healthcare', 'PFE': 'healthcare', 'MRK': 'healthcare',
        'ABT': 'healthcare', 'TMO': 'healthcare', 'DHR': 'healthcare',
        'LLY': 'healthcare', 'UNH': 'healthcare', 'AMGN': 'healthcare',

        # 工业
        'CAT': 'industrial', 'GE': 'industrial', 'HON': 'industrial',
        'BA': 'industrial', 'MMM': 'industrial', 'UTX': 'industrial',
        'DE': 'industrial', 'LMT': 'industrial', 'RTX': 'industrial',

        # 软件（默认）
        'AAPL': 'software', 'MSFT': 'software', 'GOOGL': 'software',
        'META': 'software', 'NVDA': 'software', 'ADBE': 'software',
        'ORCL': 'software', 'CRM': 'software', 'INTC': 'software',
        'AMD': 'software', 'TSM': 'software', 'IBM': 'software',

        # 消费品周期
        'AMZN': 'consumer_discretionary', 'TSLA': 'consumer_discretionary',
        'NKE': 'consumer_discretionary', 'HD': 'consumer_discretionary',

        # 通信
        'T': 'communication', 'VZ': 'communication',

        # 公用事业
        'NEE': 'utilities', 'DUK': 'utilities',

        # 房地产
        'AMT': 'real_estate', 'PLD': 'real_estate',

        # 材料
        'LIN': 'materials', 'APD': 'materials',
    }

    return ticker_map.get(ticker, 'software')  # 默认返回software


def get_industry_display_name(industry_code):
    """获取行业显示名称"""
    display_names = {
        'software': '软件/科技',
        'energy': '能源行业',
        'financial': '金融行业',
        'healthcare': '医疗保健',
        'industrial': '工业制造',
        'consumer_staples': '消费品(必需)',
        'consumer_discretionary': '消费品(可选)',
        'utilities': '公用事业',
        'communication': '通信服务',
        'real_estate': '房地产',
        'materials': '原材料',
    }
    return display_names.get(industry_code, '软件/科技')