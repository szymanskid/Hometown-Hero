"""Database module for persistent storage of banner records."""

import sqlite3
from datetime import datetime
from typing import List, Optional
from models import BannerRecord


class BannerDatabase:
    """Manages persistent storage for banner records."""
    
    def __init__(self, db_path: str = "hometown_hero.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS banners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hero_name TEXT NOT NULL,
                sponsor_name TEXT NOT NULL,
                sponsor_email TEXT,
                info_complete BOOLEAN DEFAULT 0,
                payment_verified BOOLEAN DEFAULT 0,
                proof_sent BOOLEAN DEFAULT 0,
                proof_approved BOOLEAN DEFAULT 0,
                print_approved BOOLEAN DEFAULT 0,
                pole_location TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_or_create_banner(self, hero_name: str, sponsor_name: str) -> BannerRecord:
        """Get existing banner record or create new one."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM banners 
            WHERE hero_name = ? AND sponsor_name = ?
        """, (hero_name, sponsor_name))
        
        row = cursor.fetchone()
        
        if row:
            banner = self._row_to_banner(row)
        else:
            cursor.execute("""
                INSERT INTO banners (hero_name, sponsor_name)
                VALUES (?, ?)
            """, (hero_name, sponsor_name))
            conn.commit()
            banner_id = cursor.lastrowid
            banner = BannerRecord(
                id=banner_id,
                hero_name=hero_name,
                sponsor_name=sponsor_name,
                created_at=datetime.now()
            )
        
        conn.close()
        return banner
    
    def update_banner(self, banner: BannerRecord):
        """Update banner record in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE banners 
            SET hero_name = ?,
                sponsor_name = ?,
                sponsor_email = ?,
                info_complete = ?,
                payment_verified = ?,
                proof_sent = ?,
                proof_approved = ?,
                print_approved = ?,
                pole_location = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            banner.hero_name,
            banner.sponsor_name,
            banner.sponsor_email,
            banner.info_complete,
            banner.payment_verified,
            banner.proof_sent,
            banner.proof_approved,
            banner.print_approved,
            banner.pole_location,
            banner.notes,
            banner.id
        ))
        
        conn.commit()
        conn.close()
    
    def get_all_banners(self) -> List[BannerRecord]:
        """Get all banner records."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM banners ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        
        banners = [self._row_to_banner(row) for row in rows]
        
        conn.close()
        return banners
    
    def get_banners_by_status(self, status_filter: str) -> List[BannerRecord]:
        """Get banners filtered by status."""
        all_banners = self.get_all_banners()
        return [b for b in all_banners if status_filter.lower() in b.get_status().lower()]
    
    def _row_to_banner(self, row) -> BannerRecord:
        """Convert database row to BannerRecord object."""
        return BannerRecord(
            id=row[0],
            hero_name=row[1],
            sponsor_name=row[2],
            sponsor_email=row[3],
            info_complete=bool(row[4]),
            payment_verified=bool(row[5]),
            proof_sent=bool(row[6]),
            proof_approved=bool(row[7]),
            print_approved=bool(row[8]),
            pole_location=row[9],
            notes=row[10],
            created_at=datetime.fromisoformat(row[11]) if row[11] else None,
            updated_at=datetime.fromisoformat(row[12]) if row[12] else None
        )
