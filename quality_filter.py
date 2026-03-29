import google.generativeai as genai
import json
import re
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)


class QualityFilter:

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite",
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 512,
            "response_mime_type": "application/json",
        }
    )

    model_text = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite",
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 512,
        }
    )

    @staticmethod
    def _parse_json(text):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"JSONパース失敗: {text[:200]}")

    @staticmethod
    def check(content):
        """投稿前の品質チェック"""

        prompt = f"""
以下のSNS投稿を評価してJSON形式で返してください。

チェック項目:
1. 不適切な表現がないか
2. 誤情報の可能性がないか
3. 炎上リスクがないか
4. スパムっぽくないか
5. エンゲージメントが期待できるか
6. 文字数は適切か

投稿内容:
{content}

以下のJSON形式で出力:
{{
    "passed": true または false,
    "score": 1から10の整数,
    "issues": ["問題点のリスト"],
    "suggestions": ["改善提案のリスト"]
}}
"""

        response = QualityFilter.model.generate_content(prompt)
        return QualityFilter._parse_json(response.text)

    @staticmethod
    def improve(content, issues):
        """品質チェックで問題があった場合に改善"""

        prompt = f"""
以下のSNS投稿を改善してください。
改善後の投稿本文のみを返してください。JSON不要です。

元の投稿:
{content}

問題点:
{issues}

改善後の投稿本文:
"""

        response = QualityFilter.model_text.generate_content(prompt)
        return response.text.strip()