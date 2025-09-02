import datetime
import hashlib
import time
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.network import get_url
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.util.json import load_json
from homeassistant.helpers.json import save_json
from ..const import DOMAIN, API_WEBSITE

CONFIG_FILE = f'{STORAGE_DIR}/bookmark.json'

class HttpView(HomeAssistantView):
    
    url = API_WEBSITE
    name = API_WEBSITE
    cors_allowed = True
    requires_auth = False

    async def async_get_config(self, hass):
        """异步获取配置数据"""
        # 使用hass.async_add_executor_job在线程池中运行同步IO操作
        return await hass.async_add_executor_job(
            self._sync_get_config, 
            hass
        )

    def _sync_get_config(self, hass):
        """同步获取配置数据（在 executor 中运行）"""
        try:
            result = load_json(hass.config.path(CONFIG_FILE))
            # 确保返回列表格式
            return result if isinstance(result, list) else []
        except FileNotFoundError:
            # 如果文件不存在，返回空列表
            return []
        except Exception as e:
            hass.logger.error(f"Error loading config: {e}")
            return []

    async def async_save_config(self, hass, data):
        """异步保存配置数据"""
        # 使用hass.async_add_executor_job在线程池中运行同步IO操作
        await hass.async_add_executor_job(
            self._sync_save_config, 
            hass, 
            data
        )

    def _sync_save_config(self, hass, data):
        """同步保存配置数据（在 executor 中运行）"""
        try:
            save_json(hass.config.path(CONFIG_FILE), data)
        except Exception as e:
            hass.logger.error(f"Error saving config: {e}")

    def datetime_now(self):
        return datetime.datetime.now().replace(microsecond=0).isoformat()

    def md5(self, text):
        return hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()

    async def get(self, request):
        hass = request.app["hass"]
        # 获取全部书签（使用异步方法）
        config = await self.async_get_config(hass)

        # 验证访问令牌
        auth_result = await self.async_validate_access_token(request)
        if auth_result is not None:  # 如果验证失败，返回错误响应
            # 过滤非管理员可见的项目
            config = list(filter(lambda item: item.get('admin', False) is False, config))
        
        return self.json(config)

    async def delete(self, request):
        auth_result = await self.async_validate_access_token(request)
        if auth_result is not None:
            return auth_result

        hass = request.app["hass"]
        response = await request.json()
        url = response.get('url')
        
        # 获取当前配置
        config = await self.async_get_config(hass)
        
        # 查找并删除项目
        for index, item in enumerate(config):
            if item['url'] == url:
                del config[index]
                break
        
        # 保存更新后的配置
        await self.async_save_config(hass, config)
        return self.json(config)

    async def post(self, request):

        auth_result = await self.async_validate_access_token(request)
        if auth_result is not None:
            return auth_result
        
        hass = request.app["hass"]
        response = await request.json()
        category = response.get('category')
        url = response.get('url')
        name = response.get('name')
        admin = response.get('admin', False)

        # 获取当前配置
        config = await self.async_get_config(hass)
        not_exists = True
        
        # 检查是否已存在并更新
        for item in config:
            if item['url'] == url:
                item['name'] = name
                item['category'] = category
                item['admin'] = admin
                item['time'] = int(time.time() * 1000)
                not_exists = False
                break
        
        # 如果不存在则添加新项
        if not_exists:
            config.append({
                'category': category,
                'url': url,
                'name': name,
                'admin': admin,
                'time': int(time.time() * 1000)
            })

        # 保存更新后的配置
        await self.async_save_config(hass, config)
        return self.json(config)

    async def put(self, request):
        auth_result = await self.async_validate_access_token(request)
        if auth_result is not None:
            return auth_result
        
        hass = request.app["hass"]
        response = await request.json()
        url = response.get('url')
        key = response.get('key')
        value = response.get('value')

        # 获取当前配置
        config = await self.async_get_config(hass)
        updated = False
        
        # 更新指定项
        for item in config:
            if item['url'] == url:
                item[key] = value
                updated = True
                break

        # 如果有更新则保存
        if updated:
            await self.async_save_config(hass, config)

        return self.json(config)

    def get_access_token(self, request):
        authorization = request.headers.get('Authorization')
        return str(authorization).replace('Bearer', '').strip() if authorization else None

    async def async_validate_access_token(self, request):
        ''' 授权验证 '''
        hass = request.app["hass"]
        hass_access_token = self.get_access_token(request)
        
        if not hass_access_token:
            return self.json_message("未提供授权令牌", status_code=401)
            
        # 使用异步方法验证令牌
        token = hass.auth.async_validate_access_token(hass_access_token)
        if token is None:
            return self.json_message("未授权", status_code=401)
        
        # 验证成功返回None
        return None
