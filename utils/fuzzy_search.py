"""
模糊搜索工具 - 支持股票代码和名称的模糊匹配
"""
import json
import os
import re
from difflib import SequenceMatcher, get_close_matches
from typing import List, Dict, Optional, Tuple
import sys

# 添加路径以便导入
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class FuzzyStockSearch:
    """股票模糊搜索器"""

    def __init__(self, database_path: str = None):
        # 默认数据库路径
        if database_path is None:
            # 尝试多个可能的路径
            possible_paths = [
                "data/stock_database_fixed.json",
                "data/stock_database.json",
                os.path.join(os.path.dirname(__file__), "..", "data", "stock_database_fixed.json"),
                os.path.join(os.path.dirname(__file__), "..", "data", "stock_database.json")
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    self.database_path = path
                    break
            else:
                # 如果都没找到，使用默认路径
                self.database_path = "data/stock_database_fixed.json"
        else:
            self.database_path = database_path

        self.stocks = self._load_database()

    def _load_database(self) -> List[Dict]:
        """加载股票数据库"""
        # 如果数据库文件不存在，创建基础数据库
        if not os.path.exists(self.database_path):
            print(f"⚠️  数据库文件不存在: {self.database_path}")
            print("   创建基础数据库...")
            return self._create_basic_database()

        try:
            with open(self.database_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                stocks = data.get("stocks", [])
                print(f"✅ 加载了 {len(stocks)} 只股票的数据库")
                return stocks
        except Exception as e:
            print(f"❌ 加载数据库失败: {e}")
            return self._create_basic_database()

    def _create_basic_database(self) -> List[Dict]:
        """创建基础数据库（应急用）"""
        basic_stocks = [
            {"symbol": "AAPL", "name": "Apple Inc.", "category": "technology"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "category": "technology"},
            {"symbol": "GOOGL", "name": "Alphabet Inc. (Google)", "category": "technology"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "category": "technology"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "category": "technology"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "category": "technology"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "category": "technology"},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "category": "financial"},
            {"symbol": "FISV", "name": "Fiserv Inc.", "category": "financial"},
            {"symbol": "CMCSA", "name": "Comcast Corporation", "category": "communication"},
            {"symbol": "XOM", "name": "Exxon Mobil Corporation", "category": "energy"},
            {"symbol": "JNJ", "name": "Johnson & Johnson", "category": "healthcare"},
            {"symbol": "WMT", "name": "Walmart Inc.", "category": "consumer"},
        ]

        # 为每只股票添加搜索词
        for stock in basic_stocks:
            stock["search_terms"] = self._generate_search_terms(stock["symbol"], stock["name"])

        return basic_stocks

    def _generate_search_terms(self, symbol: str, name: str) -> List[str]:
        """生成搜索关键词"""
        terms = [
            symbol.lower(),
            name.lower(),
            symbol.lower().replace("0", "o").replace("1", "i"),
        ]

        # 添加常见拼写错误
        common_mistakes = {
            "fiserv": ["fiserw", "fiserb", "fiserve"],
            "google": ["goog", "googel", "gogle"],
            "microsoft": ["msft", "micro soft"],
            "apple": ["aapl"],
            "comcast": ["cmcst", "cmcsa"],
            "facebook": ["fb", "meta"],
        }

        for correct, mistakes in common_mistakes.items():
            if correct in name.lower():
                terms.extend(mistakes)

        return list(set(terms))  # 去重

    def find_stock(self, query: str, max_results: int = 5) -> List[Dict]:
        """查找股票"""
        query = query.lower().strip()

        if not query or len(query) < 2:
            return []

        results = []

        # 1. 精确匹配股票代码
        for stock in self.stocks:
            if query == stock["symbol"].lower():
                stock["match_type"] = "exact_symbol"
                stock["score"] = 1.0
                return [stock]

        # 2. 精确匹配公司名称
        for stock in self.stocks:
            if query == stock["name"].lower():
                stock["match_type"] = "exact_name"
                stock["score"] = 0.95
                results.append(stock)

        # 3. 部分匹配（公司名称包含查询）
        for stock in self.stocks:
            if query in stock["name"].lower():
                # 计算相似度
                similarity = SequenceMatcher(None, query, stock["name"].lower()).ratio()
                if similarity > 0.3:
                    stock["match_type"] = "partial_name"
                    stock["score"] = similarity * 0.8
                    results.append(stock)

        # 4. 搜索词匹配
        for stock in self.stocks:
            search_terms = stock.get("search_terms", [])
            for term in search_terms:
                if query in term or term in query:
                    similarity = SequenceMatcher(None, query, term).ratio()
                    if similarity > 0.5:
                        stock["match_type"] = "search_term"
                        stock["score"] = similarity * 0.7
                        if stock not in results:
                            results.append(stock)

        # 5. 模糊匹配（使用difflib）
        if len(results) < max_results:
            all_names = []
            name_to_stock = {}

            for stock in self.stocks:
                # 股票代码
                all_names.append(stock["symbol"].lower())
                name_to_stock[stock["symbol"].lower()] = stock

                # 公司名称
                all_names.append(stock["name"].lower())
                name_to_stock[stock["name"].lower()] = stock

                # 搜索词
                for term in stock.get("search_terms", []):
                    all_names.append(term)
                    name_to_stock[term] = stock

            # 使用difflib进行模糊匹配
            close_matches = get_close_matches(query, all_names, n=max_results * 2, cutoff=0.3)

            for match in close_matches:
                stock = name_to_stock.get(match)
                if stock and stock not in results:
                    similarity = SequenceMatcher(None, query, match).ratio()
                    stock["match_type"] = "fuzzy_match"
                    stock["score"] = similarity * 0.6
                    results.append(stock)

        # 按分数排序并限制数量
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:max_results]

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """计算两个字符串的相似度"""
        # 清理字符串
        str1_clean = re.sub(r'[^a-z0-9]', '', str1.lower())
        str2_clean = re.sub(r'[^a-z0-9]', '', str2.lower())

        return SequenceMatcher(None, str1_clean, str2_clean).ratio()

    def auto_correct(self, input_str: str) -> Tuple[str, str, float]:
        """自动修正输入的股票代码/名称"""
        results = self.find_stock(input_str, max_results=1)

        if results:
            best_match = results[0]
            return best_match["symbol"], best_match["name"], best_match.get("score", 0)

        # 如果没有找到匹配，返回原始输入
        return input_str.upper(), f"未找到匹配的股票", 0.0

    def get_suggestions(self, query: str, max_suggestions: int = 10) -> List[str]:
        """获取搜索建议"""
        results = self.find_stock(query, max_results=max_suggestions)
        suggestions = []

        for stock in results:
            suggestions.append(f"{stock['symbol']} - {stock['name']}")

        return suggestions

    def get_stocks_by_category(self, category: str) -> List[Dict]:
        """按类别获取股票"""
        return [stock for stock in self.stocks if stock.get("category") == category]


# 全局实例
_stock_searcher = None


def get_stock_searcher() -> FuzzyStockSearch:
    """获取股票搜索器单例"""
    global _stock_searcher
    if _stock_searcher is None:
        _stock_searcher = FuzzyStockSearch()
    return _stock_searcher


def fuzzy_search_stock(query: str) -> Optional[Dict]:
    """模糊搜索股票（快捷函数）"""
    searcher = get_stock_searcher()
    results = searcher.find_stock(query, max_results=1)
    return results[0] if results else None


def auto_correct_symbol(input_str: str) -> Tuple[str, str]:
    """自动修正股票代码（快捷函数）"""
    searcher = get_stock_searcher()
    symbol, name, score = searcher.auto_correct(input_str)
    return symbol, name


def get_popular_stocks() -> List[Dict]:
    """获取热门股票列表"""
    popular_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "FISV", "CMCSA"]
    searcher = get_stock_searcher()

    popular_stocks = []
    for symbol in popular_symbols:
        results = searcher.find_stock(symbol, max_results=1)
        if results:
            popular_stocks.append(results[0])

    return popular_stocks