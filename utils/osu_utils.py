from __future__ import annotations
import datetime
from typing import Any, Dict, List, Union
import typing
import aiohttp
from .default import date
from .osu_errors import NoUserFound

class Osu:
    def __init__(self, *, client_id: int, client_secret: str, session: aiohttp.ClientSession):
        self.id = client_id
        self.secret = client_secret
        self.session: aiohttp.ClientSession = session
        self.API_URL = "https://osu.ppy.sh/api/v2"
        self.TOKEN_URL = "https://osu.ppy.sh/oauth/token"
        self.beatmap_types = ['favourite', 'graveyard', 'loved', 'most_played', 'pending', 'ranked']
    
    async def get_token(self):
        data = {
            "client_id": self.id,
            "client_secret":self.secret,
            'grant_type':'client_credentials',
            'scope':"public",
        }


        async with self.session.post(self.TOKEN_URL,data=data) as response:
            return (await response.json()).get("access_token")
    

    async def fetch_user(self, user: Union[str, int]) -> User:
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


        return User(json)

    async def fetch_user_recent(self, user: Union[str, int]):
        autorization = await self.get_token()
        headers = {
            "Content-Type": "application/json",
            "Accept":"application/json",
            "Authorization": f'Bearer {autorization}'
        }

        params = {
            "limit":5
        }
        async with self.session.get(self.API_URL+f"/users/{user}/scores/recent",headers=headers,params=params) as response:
            json = await response.json()

    

        return json

    async def fetch_user_beatmaps(self, user: str, type: str, limit: int) -> Beatmap:
        autorization = await self.get_token()
        headers = {
            "Content-Type": "application/json",
            "Accept":"application/json",
            "Authorization": f'Bearer {autorization}'
        }

        params = {
            "limit":limit
        }
        if type not in self.beatmap_types:
            types = ', '.join(self.beatmap_types)
            return f"Beatmap type must be in {types}"

        async with self.session.get(self.API_URL+f"/users/{user}/beatmapsets/{type}",headers=headers,params=params) as response:
            json = await response.json()
        

        return json
    
    async def get_beatmap(self, beatmap: Union[str, int]): 
        authorization = await self.get_token()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {authorization}"
        }

        params = {

        }

        async with self.session.get(self.API_URL+f"/beatmaps/{beatmap}", headers=headers, params=params) as resp:
            json = await resp.json()

        return Beatmap(json)

class User:
    def __init__(self, data):
        try:
            self.data = data
            self.username = data.get('username')
            self._global_rank = str(data.get('statistics').get("global_rank")) if data.get('statistics').get("global_rank") is not None else 0
            self.pp = data.get("statistics").get("pp")  if data.get('statistics') else "None"
            self._rank = data.get("statistics").get("grade_counts") if data.get('statistics') else "None"
            self.accuracy = f"{int(data.get('statistics').get('hit_accuracy')):.2f}"  if data.get('statistics') else "None"
            self._country_rank = str(data.get('statistics').get("country_rank"))  if data.get('statistics').get("country_rank") is not None else 0
            self._profile_order = data['profile_order'] if data['profile_order'] != KeyError else "Cant Get Profile Order!"
            self.country_emoji = f":flag_{data.get('country_code').lower()}:" if data.get("country_code") else "None"
            self.country_code = data.get("country_code") if data.get("country_code") else "None"
            self._country = data.get("country")
            self.avatar_url = data.get("avatar_url")
            self.id = data.get("id")
            self.playstyle = data.get("playstyle") 
            self.playmode = data.get("playmode")
            self.max_combo = data.get("statistics").get("maximum_combo")
            self.level = data.get("statistics").get("level")
            self.follower_count = data.get("follower_count")
            self._total_hits = str(data.get("statistics").get("total_hits"))
            self.total_score = data.get("statistics").get("total_score")
            self.play_count = data.get("statistics").get("play_count")
        except: # These return None if not available so bare except works fine here.
            raise NoUserFound("No user was found by that name!")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} username: {self.username!r}, id: {self.id}>"

    def __str__(self) -> str:
        return self.username

    @property
    def global_rank(self) -> Any:
        rank = self._global_rank[:3] + ',' + self._global_rank[3:] if int(self._global_rank) >  10000 else self._global_rank if int(self._global_rank) < 1000 else  self._global_rank[:1] + ',' + self._global_rank[1:] if self._global_rank != 0 else 0
        return rank
    
    @property
    def country_rank(self):
        rank = self._country_rank[:2] + ',' + self._country_rank[2:] if int(self._country_rank) > 10000 else self._country_rank if int(self._country_rank) < 1000 else  self._country_rank[:1] + ',' + self._country_rank[1:] if self._country_rank != 0 else 0
        return rank

    @property
    def total_hits(self):
        rank = self._total_hits[:3] + ',' + self._total_hits[3:] if int(self._total_hits) > 10000 else self._total_hits if int(self._total_hits) < 1000 else  self._total_hits[:2] + ',' + self._total_hits[2:] if self._total_hits != 0 else 0
        return rank


    @property
    def profile_order(self) -> str:
        profile_order ='\n ​ ​ ​ ​ ​ ​ ​ ​  - '.join(x for x in self._profile_order)
        return profile_order.replace("_", " ")

    @property
    def ranks(self) -> str:
        ss_text = self._rank['ss']
        ssh_text = self._rank['ssh']
        s_text = self._rank['s']
        sh_text = self._rank['sh']
        a_text = self._rank['a']
        return f"``SS {ss_text}`` | ``SSH {ssh_text}`` | ``S {s_text}`` | ``SH {sh_text}`` | ``A {a_text}``"

    @property
    def joined_at(self) -> str:
        if self.data.get("join_date"):
           return date(datetime.datetime.strptime(self.data.get('join_date'), '%Y-%m-%dT%H:%M:%S+00:00').timestamp(), ago=True)

    @property
    def country(self):
        return [self._country['code'], self._country['name']]

    @property
    def raw(self) -> Dict[str, any]:
        return self.data

class Beatmap:
    def __init__(self, data):
        self.data = data
        self.artist = data.get("artist")
        self.title = data.get("title")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} title: {self.title!r}, artist: {self.artist!r}>"

    def covers(self, cover: str) -> str:
        if cover not in self.data.get("cover"):
            return "Cover not in covers"

        cover_data = self.data.get("cover").get(cover)
        return cover_data



