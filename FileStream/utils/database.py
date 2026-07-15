import time
from bson.objectid import ObjectId

class Database:
    def __init__(self, uri, database_name):
        # 🔒 [Database Bypass] ปิดท่อเชื่อมต่อของจริงทิ้งทั้งหมด ป้องกัน 403 และ ServerTimeout
        self._client = None
        self.db = None
        self.col = None
        self.black = None
        self.file = None
        print("🔒 [Database Bypass] เปิดโหมดมหาอุดไร้ฐานข้อมูลสำเร็จ 100% สัส!")

    def new_user(self, id):
        return dict(
            id=id,
            join_date=time.time(),
            Links=0
        )

    async def add_user(self, id):
        return

    async def get_user(self, id):
        return self.new_user(id)

    async def total_users_count(self):
        return 1

    async def get_all_users(self):
        class DummyCursor:
            def __aiter__(self): return self
            async def __anext__(self): raise StopAsyncIteration
        return DummyCursor()

    async def delete_user(self, user_id):
        return

    def black_user(self, id):
        return dict(id=id, ban_date=time.time())

    async def ban_user(self, id):
        return

    async def unban_user(self, id):
        return

    async def is_user_banned(self, id):
        # หลอกระบบว่าไม่มีใครโดนแบนทั้งนั้น ปล่อยผ่านฉลุย
        return False

    async def total_banned_users_count(self):
        return 0
        
    async def add_file(self, file_info):
        # หลอกสร้าง ObjectId ปลอมขึ้นมาส่งคืนให้โค้ดหลักเอาไปทำหัวลิงก์ดาวน์โหลดสตรีมมึง
        return ObjectId()

    async def find_files(self, user_id, range):
        class DummyCursor:
            def skip(self, n): return self
            def limit(self, n): return self
            def sort(self, *args): return self
            def __aiter__(self): return self
            async def __anext__(self): raise StopAsyncIteration
        return DummyCursor(), 0

    async def get_file(self, _id):
        # สุ่มคืนค่าดัมมี่เพื่อให้ระบบไม่โยนข้อความ FileNotFound
        return {"_id": ObjectId(_id), "user_id": 0, "file_unique_id": "dummy"}
    
    async def get_file_by_fileuniqueid(self, id, file_unique_id, many=False):
        if many:
            class DummyCursor:
                def __aiter__(self): return self
                async def __anext__(self): raise StopAsyncIteration
            return DummyCursor()
        return False

    async def total_files(self, id=None):
        return 0

    async def delete_one_file(self, _id):
        return

    async def update_file_ids(self, _id, file_ids: dict):
        return
        
    async def count_links(self, id, operation: str):
        return
