# test_generate.py
from ai_engine import AIEngine

ai = AIEngine()

# テスト生成
result = ai.generate_post("AIと働き方の未来")
print("=" * 40)
print(f"トピック: {result['topic']}")
print(f"本文:\n{result['content']}")
print(f"理由: {result['reasoning']}")

# 品質チェックテスト
from quality_filter import QualityFilter
qf = QualityFilter()
quality = qf.check(result['content'])
print(f"\n品質スコア: {quality['score']}/10")
print(f"合格: {quality['passed']}")