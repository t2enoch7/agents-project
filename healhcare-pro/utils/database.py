import sqlite3
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "pro_system.db"):
        self.db_path = db_path

    async def initialize(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Patients table with email and date of birth
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    date_of_birth TEXT NOT NULL,
                    condition TEXT NOT NULL,
                    medical_history TEXT,
                    preferred_language TEXT DEFAULT 'en',
                    accessibility_needs TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Conversation sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    id TEXT PRIMARY KEY,
                    patient_id INTEGER NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')

            # Conversation interactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    patient_id INTEGER NOT NULL,
                    message TEXT,
                    response TEXT,
                    agent_type TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES conversation_sessions (id),
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')

            # PRO responses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pro_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    response_value TEXT,
                    response_type TEXT DEFAULT 'text',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id),
                    FOREIGN KEY (session_id) REFERENCES conversation_sessions (id)
                )
            ''')

            # Trend alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trend_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    async def create_patient(self, email: str, date_of_birth: str, condition: str, medical_history: str = "", preferred_language: str = "en", accessibility_needs: Optional[str] = None) -> int:
        """Create a new patient"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO patients (email, date_of_birth, condition, medical_history, preferred_language, accessibility_needs)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, date_of_birth, condition, medical_history, preferred_language, accessibility_needs))

            patient_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return patient_id

        except Exception as e:
            logger.error(f"Error creating patient: {e}")
            raise

    async def get_patient_by_email(self, email: str):
        """Get patient by email"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM patients WHERE email = ?', (email,))
            patient_data = cursor.fetchone()
            conn.close()

            if patient_data:
                return {
                    "id": patient_data[0],
                    "email": patient_data[1],
                    "date_of_birth": patient_data[2],
                    "condition": patient_data[3],
                    "medical_history": patient_data[4],
                    "preferred_language": patient_data[5],
                    "accessibility_needs": patient_data[6],
                    "created_at": patient_data[7]
                }
            return None

        except Exception as e:
            logger.error(f"Error getting patient: {e}")
            raise

    async def get_patient(self, patient_id: int):
        """Get patient by ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
            patient_data = cursor.fetchone()
            conn.close()

            if patient_data:
                return {
                    "id": patient_data[0],
                    "email": patient_data[1],
                    "date_of_birth": patient_data[2],
                    "condition": patient_data[3],
                    "medical_history": patient_data[4],
                    "preferred_language": patient_data[5],
                    "accessibility_needs": patient_data[6],
                    "created_at": patient_data[7]
                }
            return None

        except Exception as e:
            logger.error(f"Error getting patient: {e}")
            raise

    async def update_medical_history(self, patient_id: int, medical_history: str):
        """Update patient's medical history"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE patients
                SET medical_history = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (medical_history, patient_id))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error updating medical history: {e}")
            raise

    async def create_conversation_session(self, patient_id: int) -> str:
        """Create a new conversation session"""
        try:
            session_id = str(uuid.uuid4())
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO conversation_sessions (id, patient_id)
                VALUES (?, ?)
            ''', (session_id, patient_id))

            conn.commit()
            conn.close()
            return session_id

        except Exception as e:
            logger.error(f"Error creating conversation session: {e}")
            raise

    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT message, response, agent_type, timestamp
                FROM conversation_interactions
                WHERE session_id = ?
                ORDER BY timestamp ASC
            ''', (session_id,))

            history = []
            for row in cursor.fetchall():
                history.append({
                    "message": row[0],
                    "response": row[1],
                    "agent_type": row[2],
                    "timestamp": row[3]
                })

            conn.close()
            return history

        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            raise

    async def store_conversation_interaction(self, session_id: str, patient_id: int, message: str, response: str, agent_type: str):
        """Store a conversation interaction"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO conversation_interactions (session_id, patient_id, message, response, agent_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, patient_id, message, response, agent_type))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error storing conversation interaction: {e}")
            raise

    async def store_pro_response(self, patient_id: int, session_id: str, question_id: str, response_value: str, response_type: str = "text"):
        """Store a PRO response"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO pro_responses (patient_id, session_id, question_id, response_value, response_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (patient_id, session_id, question_id, response_value, response_type))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error storing PRO response: {e}")
            raise

    async def get_patient_pro_data(self, patient_id: int) -> List[Dict[str, Any]]:
        """Get all PRO data for a patient"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT question_id, response_value, response_type, timestamp
                FROM pro_responses
                WHERE patient_id = ?
                ORDER BY timestamp ASC
            ''', (patient_id,))

            pro_data = []
            for row in cursor.fetchall():
                pro_data.append({
                    "question_id": row[0],
                    "response_value": row[1],
                    "response_type": row[2],
                    "timestamp": row[3]
                })

            conn.close()
            return pro_data

        except Exception as e:
            logger.error(f"Error getting patient PRO data: {e}")
            raise

    async def create_trend_alert(self, patient_id: int, alert_type: str, severity: str, description: str):
        """Create a trend alert"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO trend_alerts (patient_id, alert_type, severity, description)
                VALUES (?, ?, ?, ?)
            ''', (patient_id, alert_type, severity, description))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error creating trend alert: {e}")
            raise
