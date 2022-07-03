import datetime
from typing import Any, Dict, Union
import aiohttp
from .default import date

class Osu:
    def __init__(self, *, client_id: int, client_secret: str, session: aiohttp.ClientSession):
        self.id = client_id
        self.secret = client_secret
        self.session: aiohttp.ClientSession = session
        self.API_URL = "https://osu.ppy.sh/api/v2"
        self. TOKEN_URL = "https://osu.ppy.sh/oauth/token"
    
    async def get_token(self):
        data = {
            "client_id": self.id,
            "client_secret":self.secret,
            'grant_type':'client_credentials',
            'scope':"public",
        }


        async with self.session.post(self.TOKEN_URL,data=data) as response:
            return (await response.json()).get("access_token")
    

    async def get_user(self, user: Union[str, int]) -> Dict[str, Any]:
        autorization = await self.get_token()
        headers = {
            "Content-Type": "application/json",
            "Accept":"application/json",
            "Authorization": f'Bearer {autorization}'
        }

        params = {
            "limit":5
        }
        async with self.session.get(self.API_URL+f"/users/{user}",headers=headers,params=params) as response:
            json = await response.json()

        user_time = datetime.datetime.strptime(json['join_date'], '%Y-%m-%dT%H:%M:%S+00:00').timestamp()
        relative_date = date(user_time, ago=True)
        statistics = json['statistics']
        profile_order = json['profile_order']
        acc = statistics['hit_accuracy']



        return {"username": json['username'], "avatar_url": json['avatar_url'], "is_online": json['is_online'], "join_date": relative_date, "pp":statistics['pp'], "profile_order":profile_order, "acc": acc, "global_rank":str(statistics['global_rank']), "ranks": statistics['grade_counts'], "raw": json}
    
    async def get_beatmap(self, beatmap: Union[str, int]) -> Dict[str, Any]: 
        authorization = await self.get_token()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {authorization}"
        }

        params = {

        }

        async with self.session.get(self.API_URL+f"beatmaps/{beatmap}", headers=headers, params=params) as resp:
            json = await resp.json()

        return json

