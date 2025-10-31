"""
Event Storage - Almacenamiento Persistente de Eventos
Gestión de almacenamiento de eventos críticos en SQLite con rotación y compresión.
"""

import sqlite3
import json
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import threading

from .event_logger import Event, EventLevel, EventCategory


class EventStorage:
    """
    Almacenamiento persistente de eventos en SQLite
    
    Características:
    - Base de datos SQLite para eventos críticos
    - Rotación diaria de archivos
    - Compresión de archivos antiguos (.gz)
    - Retención configurable (30 días por default)
    - Búsqueda y filtrado eficiente
    - Thread-safe
    """
    
    def __init__(
        self,
        db_dir: Optional[Path] = None,
        retention_days: int = 30,
        auto_rotate: bool = True
    ):
        self.db_dir = db_dir or Path("logs/db")
        self.retention_days = retention_days
        self.auto_rotate = auto_rotate
        
        # Crear directorio
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivo de base de datos actual
        self.current_db_file = self._get_db_file_for_date(datetime.now())
        
        # Conexión thread-local
        self._local = threading.local()
        
        # Inicializar base de datos
        self._init_database()
        
        # Limpiar archivos antiguos si auto_rotate está activo
        if self.auto_rotate:
            self._cleanup_old_files()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtener conexión thread-local a la base de datos"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.current_db_file,
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
        
        return self._local.connection
    
    def _get_db_file_for_date(self, date: datetime) -> Path:
        """Obtener nombre de archivo de base de datos para una fecha"""
        date_str = date.strftime("%Y%m%d")
        return self.db_dir / f"events_{date_str}.db"
    
    def _init_database(self):
        """Inicializar esquema de base de datos"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabla de eventos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                timestamp_iso TEXT NOT NULL,
                level TEXT NOT NULL,
                level_value INTEGER NOT NULL,
                category TEXT NOT NULL,
                source TEXT NOT NULL,
                node_id INTEGER,
                message TEXT NOT NULL,
                context TEXT,
                stack_trace TEXT
            )
        """)
        
        # Índices para búsquedas eficientes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON events(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_level 
            ON events(level_value)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON events(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source 
            ON events(source)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_node_id 
            ON events(node_id)
        """)
        
        conn.commit()
    
    def store_event(self, event: Event):
        """
        Almacenar evento en base de datos
        
        Args:
            event: Evento a almacenar
        """
        # Verificar si necesitamos rotar a nueva base de datos
        if self.auto_rotate:
            self._check_rotation()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Serializar contexto a JSON
        context_json = json.dumps(event.context) if event.context else None
        
        cursor.execute("""
            INSERT INTO events (
                timestamp,
                timestamp_iso,
                level,
                level_value,
                category,
                source,
                node_id,
                message,
                context,
                stack_trace
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.timestamp.timestamp(),
            event.timestamp.isoformat(),
            event.level.name,
            event.level.value,
            event.category.value,
            event.source,
            event.node_id,
            event.message,
            context_json,
            event.stack_trace
        ))
        
        conn.commit()
    
    def _check_rotation(self):
        """Verificar si necesitamos rotar a nueva base de datos"""
        current_date = datetime.now().date()
        db_date = datetime.fromtimestamp(
            self.current_db_file.stat().st_mtime
        ).date()
        
        if current_date != db_date:
            # Cerrar conexión actual
            if hasattr(self._local, 'connection') and self._local.connection:
                self._local.connection.close()
                self._local.connection = None
            
            # Comprimir base de datos anterior
            self._compress_db_file(self.current_db_file)
            
            # Actualizar archivo actual
            self.current_db_file = self._get_db_file_for_date(datetime.now())
            
            # Inicializar nueva base de datos
            self._init_database()
            
            # Limpiar archivos antiguos
            self._cleanup_old_files()
    
    def _compress_db_file(self, db_file: Path):
        """Comprimir archivo de base de datos con gzip"""
        if not db_file.exists():
            return
        
        gz_file = db_file.with_suffix('.db.gz')
        
        with open(db_file, 'rb') as f_in:
            with gzip.open(gz_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Eliminar archivo original
        db_file.unlink()
    
    def _cleanup_old_files(self):
        """Eliminar archivos más antiguos que retention_days"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for file in self.db_dir.glob("events_*.db.gz"):
            # Extraer fecha del nombre de archivo
            try:
                date_str = file.stem.replace("events_", "").replace(".db", "")
                file_date = datetime.strptime(date_str, "%Y%m%d")
                
                if file_date < cutoff_date:
                    file.unlink()
            except (ValueError, IndexError):
                continue
    
    def query_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_level: Optional[EventLevel] = None,
        category: Optional[EventCategory] = None,
        source: Optional[str] = None,
        node_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Buscar eventos con filtros
        
        Args:
            start_time: Fecha/hora inicial
            end_time: Fecha/hora final
            min_level: Nivel mínimo de evento
            category: Categoría específica
            source: Fuente específica
            node_id: ID de nodo específico
            limit: Número máximo de resultados
            offset: Offset para paginación
        
        Returns:
            Lista de eventos como diccionarios
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Construir query dinámicamente
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.timestamp())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.timestamp())
        
        if min_level:
            query += " AND level_value >= ?"
            params.append(min_level.value)
        
        if category:
            query += " AND category = ?"
            params.append(category.value)
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        if node_id is not None:
            query += " AND node_id = ?"
            params.append(node_id)
        
        # Ordenar por timestamp descendente
        query += " ORDER BY timestamp DESC"
        
        # Limit y offset
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convertir a diccionarios
        events = []
        for row in rows:
            event_dict = dict(row)
            
            # Parsear contexto JSON
            if event_dict['context']:
                event_dict['context'] = json.loads(event_dict['context'])
            
            events.append(event_dict)
        
        return events
    
    def count_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_level: Optional[EventLevel] = None,
        category: Optional[EventCategory] = None,
        source: Optional[str] = None,
        node_id: Optional[int] = None
    ) -> int:
        """Contar eventos con filtros (para paginación)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM events WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.timestamp())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.timestamp())
        
        if min_level:
            query += " AND level_value >= ?"
            params.append(min_level.value)
        
        if category:
            query += " AND category = ?"
            params.append(category.value)
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        if node_id is not None:
            query += " AND node_id = ?"
            params.append(node_id)
        
        cursor.execute(query, params)
        return cursor.fetchone()[0]
    
    def get_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Obtener estadísticas de eventos almacenados
        
        Args:
            start_time: Fecha/hora inicial (opcional)
            end_time: Fecha/hora final (opcional)
        
        Returns:
            Diccionario con estadísticas
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Query base
        where_clause = "WHERE 1=1"
        params = []
        
        if start_time:
            where_clause += " AND timestamp >= ?"
            params.append(start_time.timestamp())
        
        if end_time:
            where_clause += " AND timestamp <= ?"
            params.append(end_time.timestamp())
        
        # Total de eventos
        cursor.execute(f"SELECT COUNT(*) FROM events {where_clause}", params)
        total = cursor.fetchone()[0]
        
        # Por nivel
        cursor.execute(f"""
            SELECT level, COUNT(*) as count 
            FROM events {where_clause}
            GROUP BY level
        """, params)
        by_level = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Por categoría
        cursor.execute(f"""
            SELECT category, COUNT(*) as count 
            FROM events {where_clause}
            GROUP BY category
        """, params)
        by_category = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Por fuente
        cursor.execute(f"""
            SELECT source, COUNT(*) as count 
            FROM events {where_clause}
            GROUP BY source
        """, params)
        by_source = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            "total_events": total,
            "by_level": by_level,
            "by_category": by_category,
            "by_source": by_source
        }
    
    def close(self):
        """Cerrar conexión a base de datos"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
