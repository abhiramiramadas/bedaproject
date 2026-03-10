# ==========================================================
# SQLite Database Storage for Accidents
# ==========================================================

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class AccidentDatabase:
    """SQLite database for persistent accident storage"""
    
    def __init__(self, db_path="data/accidents.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Accidents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                severity TEXT NOT NULL,
                impact_score REAL,
                iou REAL,
                vehicle_types TEXT,
                speeds TEXT,
                latitude REAL,
                longitude REAL,
                address TEXT,
                nearest_hospital TEXT,
                hospital_distance REAL,
                nearest_police TEXT,
                police_distance REAL,
                weather TEXT,
                temperature REAL,
                visibility REAL,
                image_path TEXT,
                video_clip_path TEXT,
                pdf_report_path TEXT,
                damage_assessment TEXT,
                alerts_sent INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                total_accidents INTEGER DEFAULT 0,
                critical_count INTEGER DEFAULT 0,
                high_count INTEGER DEFAULT 0,
                medium_count INTEGER DEFAULT 0,
                low_count INTEGER DEFAULT 0,
                alerts_sent INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_accident(self, accident_data: Dict) -> int:
        """
        Save accident to database
        
        Args:
            accident_data: Dictionary with accident information
            
        Returns:
            ID of inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO accidents (
                timestamp, severity, impact_score, iou, vehicle_types, speeds,
                latitude, longitude, address, nearest_hospital, hospital_distance,
                nearest_police, police_distance, weather, temperature, visibility,
                image_path, video_clip_path, pdf_report_path, damage_assessment, alerts_sent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            accident_data.get('timestamp', datetime.now().isoformat()),
            accident_data.get('severity', 'UNKNOWN'),
            accident_data.get('impact_score', 0),
            accident_data.get('iou', 0),
            json.dumps(accident_data.get('vehicle_types', [])),
            json.dumps(accident_data.get('speeds', [])),
            accident_data.get('latitude', 0),
            accident_data.get('longitude', 0),
            accident_data.get('address', ''),
            accident_data.get('nearest_hospital', ''),
            accident_data.get('hospital_distance', 0),
            accident_data.get('nearest_police', ''),
            accident_data.get('police_distance', 0),
            accident_data.get('weather', ''),
            accident_data.get('temperature', 0),
            accident_data.get('visibility', 0),
            accident_data.get('image_path', ''),
            accident_data.get('video_clip_path', ''),
            accident_data.get('pdf_report', ''),
            json.dumps(accident_data.get('damage_assessment', {})),
            1 if accident_data.get('alerts_sent', False) else 0
        ))
        
        accident_id = cursor.lastrowid
        
        # Update daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        severity = accident_data.get('severity', 'LOW')
        
        cursor.execute('''
            INSERT INTO daily_stats (date, total_accidents, critical_count, high_count, medium_count, low_count, alerts_sent)
            VALUES (?, 1, ?, ?, ?, ?, 1)
            ON CONFLICT(date) DO UPDATE SET
                total_accidents = total_accidents + 1,
                critical_count = critical_count + ?,
                high_count = high_count + ?,
                medium_count = medium_count + ?,
                low_count = low_count + ?,
                alerts_sent = alerts_sent + 1
        ''', (
            today,
            1 if severity == 'CRITICAL' else 0,
            1 if severity == 'HIGH' else 0,
            1 if severity == 'MEDIUM' else 0,
            1 if severity == 'LOW' else 0,
            1 if severity == 'CRITICAL' else 0,
            1 if severity == 'HIGH' else 0,
            1 if severity == 'MEDIUM' else 0,
            1 if severity == 'LOW' else 0
        ))
        
        conn.commit()
        conn.close()
        
        return accident_id
    
    def get_all_accidents(self, limit: int = 100) -> List[Dict]:
        """Get all accidents from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM accidents ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        accidents = []
        for row in rows:
            accident = dict(row)
            accident['vehicle_types'] = json.loads(accident['vehicle_types'] or '[]')
            accident['speeds'] = json.loads(accident['speeds'] or '[]')
            accident['damage_assessment'] = json.loads(accident['damage_assessment'] or '{}')
            accidents.append(accident)
        
        return accidents
    
    def get_accidents_by_date(self, start_date: str, end_date: str) -> List[Dict]:
        """Get accidents within date range"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM accidents 
            WHERE date(timestamp) BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', (start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self, days: int = 30) -> Dict:
        """Get accident statistics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                SUM(total_accidents) as total,
                SUM(critical_count) as critical,
                SUM(high_count) as high,
                SUM(medium_count) as medium,
                SUM(low_count) as low,
                SUM(alerts_sent) as alerts
            FROM daily_stats
            WHERE date >= date('now', ?)
        ''', (f'-{days} days',))
        
        row = cursor.fetchone()
        
        # Get daily breakdown
        cursor.execute('''
            SELECT date, total_accidents, critical_count, high_count, medium_count, low_count
            FROM daily_stats
            WHERE date >= date('now', ?)
            ORDER BY date ASC
        ''', (f'-{days} days',))
        
        daily_data = [dict(r) for r in cursor.fetchall()]
        conn.close()
        
        return {
            'summary': {
                'total': row['total'] or 0,
                'critical': row['critical'] or 0,
                'high': row['high'] or 0,
                'medium': row['medium'] or 0,
                'low': row['low'] or 0,
                'alerts': row['alerts'] or 0
            },
            'daily': daily_data
        }
    
    def get_accident_by_id(self, accident_id: int) -> Optional[Dict]:
        """Get single accident by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM accidents WHERE id = ?', (accident_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            accident = dict(row)
            accident['vehicle_types'] = json.loads(accident['vehicle_types'] or '[]')
            accident['speeds'] = json.loads(accident['speeds'] or '[]')
            accident['damage_assessment'] = json.loads(accident['damage_assessment'] or '{}')
            return accident
        return None


# Global instance
accident_db = AccidentDatabase()


def save_to_database(accident_data: Dict) -> int:
    """Save accident to database"""
    return accident_db.save_accident(accident_data)


def get_accidents_from_db(limit: int = 100) -> List[Dict]:
    """Get accidents from database"""
    return accident_db.get_all_accidents(limit)


def get_stats(days: int = 30) -> Dict:
    """Get statistics from database"""
    return accident_db.get_statistics(days)
