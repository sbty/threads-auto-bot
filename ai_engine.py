from google import genai
import json
import random
import re
from config import Config
from database import Database

# Gemini初期化
client = genai.Client(api_key=Config.GEMINI_API_KEY)


class AIEngine:

    MODEL_MAIN = "gemini-2.5-flash"
    MODEL_LIGHT = "gemini-2.5-flash"

    @staticmethod
    def _generate(model_name, prompt, json_output=True, use_grounding=False):
        from google.genai import types
        
        tools = []
        if use_grounding:
            # Google検索グラウンディングを有効化
            tools.append(types.Tool(google_search=types.GoogleSearch()))

        config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            tools=tools
        )
        
        if json_output and not use_grounding:
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
    def generate_post(custom_topic=None, rss_context=None,
                      account_niche=None, account_tone=None, account_db=None):
        """メイン投稿生成"""

        db = account_db if account_db else Database()

        recent_posts = db.get_recent_posts(20)
        recent_texts = [p[0] for p in recent_posts]

        top_topics = db.get_top_performing_topics()
        top_topic_str = ", ".join([t[0] for t in top_topics]) if top_topics else "no data yet"

        styles = [
            "knowledge sharing - useful tips",
            "opinion style - unique take on a trend",
            "story style - personal episode",
            "list style - 3 reasons why...",
            "one-liner impact - short punchy phrase",
            "debate style - controversial opinion",
        ]
        selected_style = random.choice(styles)

        niche = custom_topic if custom_topic else (account_niche or Config.ACCOUNT1.niche)
        tone = account_tone or Config.ACCOUNT1.tone

        recent_str = "\n".join(recent_texts[-10:]) if recent_texts else "none"
        rss_str = "\n".join(rss_context) if rss_context else "no headlines available"

        prompt = (
            "You are a highly influential SNS marketer running a popular Threads account.\n"
            "\n"
            "## Account Persona & Context\n"
            f"- Today's specific topic/news context: {niche}\n"
            f"- Persona Tone: {tone}\n"
            "- Ultimate Goal: Maximize engagement (Saves, Likes, Quotes)\n"
            "\n"
            "## Content Rules\n"
            "- Under 400 chars (ideal 150-300). Keep it concise, punchy, and highly readable using line breaks.\n"
            "- Max 2 hashtags (if necessary).\n"
            "- Use 1-3 emojis effectively.\n"
            "- Write in extremely natural, conversational Japanese. Avoid robotic, rigid phrasing.\n"
            "- Do not repeat past posts.\n"
            "\n"
            "## IMPORTANT: Factual Accuracy & Hallucination Prevention\n"
            "- **FACT CHECK**: Before stating any facts (especially about sports results, technical specs, or recent events), ensure they are accurate. If you are not 100% sure, use the search tool or avoid making a definitive statement.\n"
            "- Do not invent facts. If the information is not in your current context or search results, speak in general terms or ask the audience.\n"
            "\n"
            "## IMPORTANT: Persona & Engagement Strategy\n"
            "- FULLY ADOPT THE PERSONA implied by the Tone and Topic. If the topic is 'Engineer Life', speak as an actual engineer experiencing it. If it's 'AI Tips', speak as someone who uses them daily to save time.\n"
            "- DO NOT act like a detached 'news commenter'. Speak from a first-person, authentic perspective.\n"
            "- Share highly actionable tips, relatable struggles ('あるある'), or strong opinions based on facts.\n"
            "- **CRITICAL**: DO NOT ask any questions to the audience at the end of the post. NEVER end the post with a question mark (？) or sentences like 'どう思いますか？', 'コメント欄で教えてください', or '皆さんは？'. This sounds like cheap engagement bait and is extremely robotic. To get engagement, rely on deep resonance or strong opinions, NOT questions. Just declare your thoughts and end the post cleanly with a natural observation, exclamation, or period.\n"
            "\n"
            "## Latest news headlines (If your niche/topic is news-centric, focus on distilling the key points and providing professional insights. Otherwise, use them as inspiration for persona-driven storytelling.)\n"
            f"{rss_str}\n"
            "\n"
            "## Recent posts (avoid duplicates)\n"
            f"{recent_str}\n"
            "\n"
            "## High-performing topics\n"
            f"{top_topic_str}\n"
            "\n"
            "## Format Instruction\n"
            f"Generate 1 post based on the style: [{selected_style}]. Output in this JSON format:\n"
            '{\n'
            '    "content": "post text in Japanese",\n'
            '    "topic": "topic category (1-2 words)",\n'
            '    "reasoning": "why this post will be heavily saved and quoted by users"\n'
            '}\n'
        )

        raw = AIEngine._generate(AIEngine.MODEL_MAIN, prompt, json_output=True, use_grounding=True)
        return AIEngine._parse_json(raw)

    @staticmethod
    def generate_reply(original_post, user_comment,
                       account_tone=None):
        """自動リプライ生成"""
        tone = account_tone or Config.ACCOUNT1.tone

        prompt = f"""
あなたはThreadsアカウントの運営者です。
フォロワーのコメントに対して、親しみやすく知的な返信をしてください。
トーン: {tone}

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
    def generate_weekly_content_plan(account_niche=None, account_db=None):
        """1週間分のコンテンツプラン生成"""

        db = account_db if account_db else Database()
        niche = account_niche or Config.ACCOUNT1.niche

        top_topics = db.get_top_performing_topics()

        prompt = f"""
{niche}ジャンルのThreadsアカウント用に
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

        raw = AIEngine._generate(AIEngine.MODEL_MAIN, prompt, json_output=True, use_grounding=False)
        return AIEngine._parse_json(raw)