import datetime, hashlib, uuid, time
from homeassistant.components.http import HomeAssistantView

from ..const import DOMAIN, API_URL, API_NAME
from ..utils.storage import YAMLStorage

CONFIG_FILE = "bookmark.yaml"

class HttpView(HomeAssistantView):
    url = API_URL
    name = API_NAME
    cors_allowed = True
    required_admin = False

    def __init__(self, hass):
        self.hass = hass
        self._storage = YAMLStorage(hass, CONFIG_FILE)

    async def get_config(self):
        result = await self._storage.async_load()
        if not isinstance(result, list):
            result = []
        return result

    async def save_config(self, data):
        await self._storage.async_save(data)

    def datetime_now(self):
        return datetime.datetime.now().replace(microsecond=0).isoformat()

    def md5(self, text):
        return hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()

    async def get(self, request):
        # 获取全部书签
        config = await self.get_config()
        return self.json(config)

    async def delete(self, request):
        response = await request.json()
        url = response.get('url')
        config = await self.get_config()
        for index, item in enumerate(config):
            if item['url'] == url:
                del config[index]
                break
        await self.save_config(config)
        return self.json(config)

    async def post(self, request):
        response = await request.json()
        category = response.get('category')
        url = response.get('url')
        name = response.get('name')

        config = await self.get_config()
        not_exists = True
        for item in config:
            if item['url'] == url:
                item['name'] = name
                item['category'] = category
                item['time'] = int(time.time() * 1000)
                not_exists = False
                break

        if not_exists:
            config.append({
                'category': category,
                'url': url,
                'name': name,
                'time': int(time.time() * 1000)
            })

        await self.save_config(config)
        return self.json(config)

    async def put(self, request):
        response = await request.json()
        url = response.get('url')
        key = response.get('key')
        value = response.get('value')

        config = await self.get_config()
        not_exists = True
        for item in config:
            if item['url'] == url:
                item[key] = value
                not_exists = False
                break

        if not_exists == False:
            await self.save_config(config)

        return self.json(config)