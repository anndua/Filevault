from datetime import datetime

from pathlib import Path
import uuid

class ObjectkeyGenerator:
    @staticmethod
    def generate(user_id:int,filename:str,)->str:
        extension=Path(filename).suffix
        now=datetime.now()

        object_id=uuid.uuid4

        return (f"users/"f"{user_id}/"f"{now.year}/"f"{now.month}/"f"{now.month:02d}/"f"{object_id}{extension}")
    
