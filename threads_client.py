import requests
import time
from config import Config

class ThreadsClient:

    def __init__(self):
        self.base_url = Config.THREADS_API_BASE
        self.access_token = Config.THREADS_ACCESS_TOKEN
        self.user_id = Config.THREADS_USER_ID

    def create_text_post(self, text):
        """テキスト投稿"""
        # Step 1: コンテナ作成
        container = requests.post(
            f"{self.base_url}/{self.user_id}/threads",
            params={
                "media_type": "TEXT",
                "text": text,
                "access_token": self.access_token
            }
        )
        container_data = container.json()

        if "id" not in container_data:
            print(f"Error creating container: {container_data}")
            return None

        creation_id = container_data["id"]

        # Step 2: 公開
        time.sleep(3)

        publish = requests.post(
            f"{self.base_url}/{self.user_id}/threads_publish",
            params={
                "creation_id": creation_id,
                "access_token": self.access_token
            }
        )
        publish_data = publish.json()

        if "id" in publish_data:
            print(f"✅ Posted successfully! ID: {publish_data['id']}")
            return publish_data["id"]
        else:
            print(f"❌ Error publishing: {publish_data}")
            return None

    def create_image_post(self, text, image_url):
        """画像付き投稿"""
        container = requests.post(
            f"{self.base_url}/{self.user_id}/threads",
            params={
                "media_type": "IMAGE",
                "image_url": image_url,
                "text": text,
                "access_token": self.access_token
            }
        )
        creation_id = container.json()["id"]
        time.sleep(5)

        publish = requests.post(
            f"{self.base_url}/{self.user_id}/threads_publish",
            params={
                "creation_id": creation_id,
                "access_token": self.access_token
            }
        )
        return publish.json().get("id")

    def get_post_insights(self, thread_id):
        """投稿のインサイト取得"""
        response = requests.get(
            f"{self.base_url}/{thread_id}/insights",
            params={
                "metric": "views,likes,replies,reposts,quotes",
                "access_token": self.access_token
            }
        )
        return response.json()

    def get_replies(self, thread_id):
        """リプライ一覧取得"""
        response = requests.get(
            f"{self.base_url}/{thread_id}/replies",
            params={
                "fields": "id,text,username,timestamp",
                "access_token": self.access_token
            }
        )
        return response.json()

    def reply_to_thread(self, reply_to_id, text):
        """リプライに返信"""
        container = requests.post(
            f"{self.base_url}/{self.user_id}/threads",
            params={
                "media_type": "TEXT",
                "text": text,
                "reply_to_id": reply_to_id,
                "access_token": self.access_token
            }
        )
        creation_id = container.json()["id"]
        time.sleep(3)

        publish = requests.post(
            f"{self.base_url}/{self.user_id}/threads_publish",
            params={
                "creation_id": creation_id,
                "access_token": self.access_token
            }
        )
        return publish.json().get("id")

    def get_user_insights(self):
        """アカウント全体のインサイト"""
        response = requests.get(
            f"{self.base_url}/{self.user_id}/threads_insights",
            params={
                "metric": "views,likes,replies,reposts,quotes,followers_count",
                "access_token": self.access_token
            }
        )
        return response.json()