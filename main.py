import argparse
import sys
import os
from datetime import datetime

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analysis.pre_market import PreMarketAnalyst
from src.analysis.post_market import PostMarketAnalyst

def save_report(content: str, mode: str):
    """
    Save the report to a markdown file in the reports/ directory.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    filename = f"{today}_{mode}_report.md"
    filepath = os.path.join(report_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"\nReport saved to: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="Deep Data Mining System for Fund Investment")
    parser.add_argument("--mode", choices=["pre", "post"], required=True, help="Analysis mode: 'pre' (Pre-market) or 'post' (Post-market)")
    
    args = parser.parse_args()
    
    print(f"Starting {args.mode.upper()}-market analysis...")
    
    if args.mode == "pre":
        analyst = PreMarketAnalyst()
        report = analyst.run_all()
    elif args.mode == "post":
        analyst = PostMarketAnalyst()
        report = analyst.run_all()
    
    print("\n=== REPORT GENERATED ===\n")
    print(report)
    
    save_report(report, args.mode)

if __name__ == "__main__":
    main()
