from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class SourceResult:
    status: str           
    data: Optional[dict] = None  
    reason: Optional[str] = None 


class SourceAdapter(ABC):
    name: str  

    @abstractmethod
    async def get(self, resident_id: str) -> SourceResult:
        raise NotImplementedError