from google import genai
import json
import random
import re
from config import Config
from database import Database

# Gemini初期化
client = genai.Client(api_key=Config.GEMINI_API_KEY)
db = Database()


class AIEngine:

    MODEL_MAIN = "gemini-2.5-flash"
    MODEL_LIGHT = "gemini-2.5-flash"

    @staticmethod
    def _generate(model_name, prompt, json_output=True):
        from google.genai import types
        config = types.GenerateContentConfig(
            temperature=0.9,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
        if json_output:
            config.response_mime_type = "application/json"
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config
        )
        return response.text

    @staticmethod
    def _parse_json(text):
        """Geminiの出力からJSONを安全にパース"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r'```json?\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"JSONパース失敗: {text[:200]}")

    @staticmethod
    def generate_post(custom_topic=None, rss_context=None):
        """メイン投稿生成"""

        recent_posts = db.get_recent_posts(20)
        recent_texts = [p[0] for p in recent_posts]

        top_topics = db.get_top_performing_topics()
        top_topic_str = ", ".join([t[0] for t in top_topics]) if top_topics else "no data yet"

        styles = [
            # "question style - ask followers a question",
            "knowledge sharing - useful tips",
            "opinion style - unique take on a trend",
            "story style - personal episode",
            "list style - 3 reasons why...",
            "one-liner impact - short punchy phrase",
            "debate style - controversial opinion",
        ]
        selected_style = random.choice(styles)

        niche = custom_topic if custom_topic else Config.ACCOUNT_NICHE
        recent_str = "\n".join(recent_texts[-10:]) if recent_texts else "none"
        rss_str = "\n".join(rss_context) if rss_context else "no headlines available"

        prompt = (
            "You are a pro SNS marketer running a popular Threads account.\n"
            "\n"
            "## Account Settings\n"
            f"- Today's topic: {niche}\n"
            f"- Tone: {Config.ACCOUNT_TONE}\n"
            "- Goal: maximize engagement, gain followers\n"
            "\n"
            "## Rules\n"
            "- Under 500 chars (ideal 100-300)\n"
            "- Max 3 hashtags\n"
            "- Use 1-3 emojis naturally\n"
            "- Write in natural Japanese, not robotic\n"
            "- No promotions\n"
            "- Do not repeat past posts\n"
            "- Reference current news/trends when relevant\n"
            "\n"
            "## IMPORTANT: Persona Rules\n"
            "- You are a NEWS COMMENTER, not a participant\n"
            "- NEVER pretend you attended events, matches, or concerts\n"
            "- NEVER say 「生で見た」「行ってきた」「実際に使った」 unless it's clearly general advice\n"
            "- OK: 「ハイライト見たけど」「ニュース見て思った」「気になる」「注目」\n"
            "- OK: 「みんなはどう思う？」「これはアツい」「今後が楽しみ」\n"
            "- NG: 「スタジアムで見た」「ライブ最高だった」「現地行った」\n"
            "- Your role: ニュースや話題を見て感想・意見を発信する人\n"
            "\n"
            "## Latest news headlines (use as inspiration)\n"
            f"{rss_str}\n"
            "\n"
            "## Recent posts (avoid duplicates)\n"
            f"{recent_str}\n"
            "\n"
            "## High-performing topics\n"
            f"{top_topic_str}\n"
            "\n"
            f"## Post style: {selected_style}\n"
            "\n"
            "Generate 1 post in this JSON format:\n"
            '{\n'
            f'    "content": "post text in Japanese about {niche}",\n'
            '    "topic": "topic category (1-2 words)",\n'
            '    "reasoning": "why this post will get engagement"\n'
            '}\n'
        )

        raw = AIEngine._generate(AIEngine.MODEL_MAIN, prompt, json_output=True)
        return AIEngine._parse_json(raw)

    @staticmethod
    def generate_reply(original_post, user_comment):
        """自動リプライ生成"""

        prompt = f"""
あなたはThreadsアカウントの運営者です。
フォロワーのコメントに対して、親しみやすく知的な返信をしてください。
トーン: {Config.ACCOUNT_TONE}

ルール:
- 100文字以内
- 相手の感情を肯定する
- 会話を発展させる質問を含める
- 自然で人間らしい返信

元の投稿: {original_post}
コメント: {user_comment}

返信文のみを出力してください（JSON不要）：
"""

        raw = AIEngine._generate(AIEngine.MODEL_LIGHT, prompt, json_output=False)
        return raw.strip()

    @staticmethod
    def generate_weekly_content_plan():
        """1週間分のコンテンツプラン生成"""

        top_topics = db.get_top_performing_topics()

        prompt = f"""
{Config.ACCOUNT_NICHE}ジャンルのThreadsアカウント用に
1週間分（7日間、1日2投稿 = 14投稿）のコンテンツプランを作成してください。

パフォーマンスが良いトピック: {top_topics}

以下のJSON形式で出力してください:
{{
    "plan": [
        {{
            "day": 1,
            "time_slot": "morning または evening",
            "topic": "トピック",
            "style": "投稿スタイル",
            "hook": "書き出しのフック"
        }}
    ]
}}
"""

        raw = AIEngine._generate(AIEngine.MODEL_MAIN, prompt, json_output=True)
        return AIEngine._parse_json(raw)