"""Common analyst scaffolding.

This module centralizes shared logic between pre-market and post-market analysts:
- fund list loading
- sources tracking + formatting
- run_all / run_one orchestration

Collector methods and prompt composition remain in the concrete analyst classes.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from config.settings import FUNDS_FILE
from src.data_sources.web_search import WebSearch
from src.llm.client import get_llm_client


class BaseAnalyst:
    """Shared base for analyst workflows."""

    SYSTEM_TITLE: str = "分析系统启动"
    FAILURE_SUFFIX: str = "分析失败"

    def __init__(self):
        self.web_search = WebSearch()
        self.llm = get_llm_client()
        self.funds = self._load_funds()
        self.today = self._compute_today()
        self.sources: List[Dict] = []

    # =========================================================================
    # Date / configuration
    # =========================================================================

    def _compute_today(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def _load_funds(self) -> List[Dict]:
        if not os.path.exists(FUNDS_FILE):
            print(f"Warning: Funds file not found at {FUNDS_FILE}")
            return []
        with open(FUNDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # =========================================================================
    # Source Tracking Utilities
    # =========================================================================

    def _reset_sources(self):
        """每次分析新基金前重置来源列表"""
        self.sources = []

    def _add_source(self, category: str, title: str, url: str = None, source_name: str = None):
        """添加一个数据来源"""
        source_entry = {
            "category": category,
            "title": title[:100] if title else "N/A",
            "url": url,
            "source": source_name,
        }
        if not any(
            s.get("title") == source_entry["title"] and s.get("url") == source_entry["url"]
            for s in self.sources
        ):
            self.sources.append(source_entry)

    def _market_data_sources_section_lines(self) -> List[str]:
        """Subclasses may override to customize fixed data source notes."""
        return [
            "- AkShare: A股指数、北向资金、行业资金流向",
            "- 东方财富: 基金数据",
            "- Tavily Search API: 实时新闻搜索",
        ]

    def _format_sources(self) -> str:
        """格式化数据来源为报告附录"""
        if not self.sources:
            return ""

        output: List[str] = []
        output.append("\n\n---")
        output.append("\n## 📚 数据来源 (Sources Used in This Report)")

        categories: Dict[str, List[Dict]] = {}
        for source in self.sources:
            cat = source.get("category") or "其他"
            categories.setdefault(cat, []).append(source)

        for cat, items in categories.items():
            output.append(f"\n### {cat}")
            for i, item in enumerate(items, 1):
                title = item.get("title") or "N/A"
                url = item.get("url")
                source_name = item.get("source") or ""

                if url:
                    output.append(f"{i}. [{title}]({url})")
                else:
                    source_suffix = f" - {source_name}" if source_name else ""
                    output.append(f"{i}. {title}{source_suffix}")

        output.append("\n### 📊 市场数据来源")
        output.extend(self._market_data_sources_section_lines())

        return "\n".join(output)

    # =========================================================================
    # Orchestration
    # =========================================================================

    def analyze_fund(self, fund: Dict) -> str:  # pragma: no cover
        raise NotImplementedError

    def run_all(self) -> str:
        """Run analysis for all configured funds."""
        print(f"\n{'#' * 60}")
        print(f"# {self.SYSTEM_TITLE} - {self.today}")
        print(f"# 待分析基金数量: {len(self.funds)}")
        print(f"{'#' * 60}")

        reports: List[str] = []
        for fund in self.funds:
            try:
                report = self.analyze_fund(fund)
                if report:
                    reports.append(report)
            except Exception as e:
                print(f"  ❌ {self.FAILURE_SUFFIX}: {e}")
                fund_name = fund.get("name") if isinstance(fund, dict) else "Unknown"
                reports.append(f"## {fund_name} {self.FAILURE_SUFFIX}\n错误: {str(e)}")

        return "\n\n---\n\n".join(reports)

    def run_one(self, fund_code: str) -> str:
        """Run analysis for a specific fund code."""
        target_fund: Optional[Dict] = next((f for f in self.funds if f.get("code") == fund_code), None)
        if not target_fund:
            return f"Error: Fund with code {fund_code} not found in configuration."

        return self.analyze_fund(target_fund)
