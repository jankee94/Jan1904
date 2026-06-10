# core/models/base.py
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import json

@dataclass
class BaseModel:
    """Modelo base para todas las entidades"""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir modelo a diccionario para Firestore"""
        data = asdict(self)
        # Eliminar campos None
        data = {k: v for k, v in data.items() if v is not None}
        # Convertir datetime a string
        if 'created_at' in data and data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = data['updated_at'].isoformat()
        # Eliminar id del diccionario (Firestore usa su propio id)
        data.pop('id', None)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], doc_id: str = None):
        """Crear modelo desde diccionario de Firestore"""
        # Convertir strings a datetime
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(id=doc_id, **data)
