from beanie import Document 
from typing import List


class SignatureInDB(Document):
    signatures: List[str]
    name: str
    class Collection:
        name = "signatures"
