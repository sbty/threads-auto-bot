import requests
from config import Config


class ThreadsClient:
    def __init__(self, access_token=None, user_id=None):
        # 引数で渡されたものを優先、なければConfigから取得（後方互換）
        self.access_token = access_token
        self.user_id = user_id
        self.base_url = Config.THREADS_API_BASE
    
    def create_text_post(self, text):
        """テキスト投稿"""
        # コンテナ作成
        container_url = f"{self.base_url}/{self.user_id}/threads"
        params = {
            "media_type": "TEXT",
            "text": text,
            "access_token": self.access_token
        }
        
        response = requests.post(container_url, params=params)
        response.raise_for_status()
        container_id = response.json()["id"]
        
        # 公開
        publish_url = f"{self.base_url}/{self.user_id}/threads_publish"
        publish_params = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        
        response = requests.post(publish_url, params=publish_params)
        response.raise_for_status()
        
        return response.json()["id"]