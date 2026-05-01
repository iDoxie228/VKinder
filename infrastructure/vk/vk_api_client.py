import vk_api

class VKApiClient:
    def __init__(self, token: str) -> None:
        self.token = token,
        self.vk_session = vk_api.VkApi(token = token)
        self.vk = self.vk_session.get_api()
    
    def get_api(self):
        return self.vk