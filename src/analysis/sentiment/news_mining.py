import akshare as ak
import pandas as pd
from datetime import datetime
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from src.llm.client import get_llm_client

class NewsMiner:
    def __init__(self):
        try:
            self.llm_client = get_llm_client()
        except Exception as e:
            print(f"Warning: LLM Client initialization failed: {e}")
            self.llm_client = None

    def fetch_recent_news(self, limit=15):
        """
        获取财联社全球财经快讯
        """
        try:
            # 尝试获取财联社电报
            df = ak.stock_info_global_cls()
            if df is None or df.empty:
                return []
            
            # 简单去重和格式化
            news_list = []
            # Akshare returns newest first usually
            for _, row in df.head(limit).iterrows():
                # 安全获取数据，避免列名乱码问题，假设前几列是固定的
                # 观察 debug 输出: ['标题', '内容', '发布日期', '发布时间']
                title = str(row.iloc[0]).strip()
                content = str(row.iloc[1]).strip()
                pub_time = str(row.iloc[3]).strip()
                
                # 过滤掉显然无效的短新闻
                if len(content) < 5:
                    continue
                    
                news_list.append({
                    "title": title,
                    "content": content,
                    "time": pub_time
                })
            return news_list
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def analyze_news_sentiment(self, news_items):
        """
        利用 LLM 分析新闻列表的情绪
        """
        if not self.llm_client:
            return "LLM Client not available."
            
        if not news_items:
            return "暂无重要新闻。"

        news_text = ""
        for i, item in enumerate(news_items):
            # 截断过长的内容以节省 Token
            content_snippet = item['content'][:200]
            news_text += f"{i+1}. [{item['time']}] {item['title']}\n   内容: {content_snippet}\n"

        prompt = f"""
        【角色设定】
        你是A股市场顶级游资的情报官，擅长从海量资讯中捕捉驱动股价上涨的“胜负手”。你极度厌恶没有实际驱动力的“口水新闻”。

        【待分析情报】
        {news_text}
        
        【任务要求】
        1. **筛选**：从上述列表中挑选出 1-3 条可能引发资金关注的**核心消息**。如果没有值得关注的，请直接输出“当前市场无重要驱动消息”。
        2. **评级**：对每条入选消息打分 (1-5星)。
           - ⭐: 普通资讯，无影响。
           - ⭐⭐⭐: 局部热点，可能引发板块异动。
           - ⭐⭐⭐⭐⭐: 重大题材，可能引发涨停潮或大盘变盘。
        3. **推演**：
           - **关联板块/个股**：明确指出代码或名称。
           - **情绪预判**：这是“突发利好(抢筹)”、“利好兑现(砸盘)”还是“不及预期(核按钮)”？
        
        【输出格式】
        请直接输出 Markdown 分析结果，不要废话。
        """
        
        return self.llm_client.generate_content(prompt)

if __name__ == "__main__":
    miner = NewsMiner()
    print("Fetching news...")
    news = miner.fetch_recent_news()
    print(f"Fetched {len(news)} items.")
    
    if news:
        print("Analyzing with AI...")
        report = miner.analyze_news_sentiment(news)
        print("\n" + "="*30)
        print(report)
        print("="*30 + "\n")
