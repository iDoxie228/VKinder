import requests


class VK:

   def __init__(self, access_token, user_id, version='5.199'):
       self.token = access_token
       self.id = user_id
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}


   def users_info(self):
       url = 'https://api.vk.com/method/users.get'
       params = {'user_ids': self.id}
       response = requests.get(url, params={**self.params, **params})
       return response.json()

access_token = 'vk1.a.rROIArlcJYrF5FH34INZcJJULsYSWCzYH8a6TIXKlqK3jGc0urzORxF-wH4e02gVqRVIqyurwJ4i-PqgZff3uSYUDDw2gyxTFhO1GRUhcUg0ClG2HwP54QrPd4YOWk5xwGrnWQYtyz6Av1oiHK3MAiefGHcSgo6UxbytqxoE5-2HksdrUe8ZMEXg90PaQh33'
user_id = '499570989'
vk = VK(access_token, user_id)

print(vk.users_info())