#!/usr/bin/env python3
"""
Script chạy parallel scraper - dùng cho Colab
"""

import sys
import os

# Thêm thư mục src vào path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    print("🚀 Starting ArXiv Parallel Scraper...")
    print("="*80)
    print("📝 Features:")
    print("   - Parallel processing với 6 workers")
    print("   - Auto checkpoint mỗi 50 papers")
    print("   - Realtime CSV updates")
    print("   - Memory & performance tracking")
    print("="*80)
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("✅ Progress đã được lưu tại checkpoint cuối cùng")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
