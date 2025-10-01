from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

class TLClient:
    def __init__(self, api_id: int, api_hash: str):
        self.client = TelegramClient(StringSession(), api_id, api_hash)

    async def connect(self): await self.client.connect()
    async def send_code(self, phone: str):
        return await self.client.send_code_request(phone)

    async def sign_in_code(self, phone: str, code: str):
        # Will raise SessionPasswordNeededError if 2FA is enabled
        return await self.client.sign_in(phone=phone, code=code)

    async def sign_in_2fa(self, password: str):
        return await self.client.sign_in(password=password)

    def save_string(self) -> str:
        return self.client.session.save()

    async def disconnect(self): await self.client.disconnect()
      
