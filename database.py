# SQLite Database Module for Mental Health App
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import secrets

# Database Configuration
DB_DIR = "user_data"
DB_FILE = os.path.join(DB_DIR, "mental_health.db")

# Ensure database directory exists
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

class DatabaseManager:
    """Manages all database operations for the Mental Health App"""
    
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                active INTEGER DEFAULT 1
            )
        ''')
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                age INTEGER,
                gender TEXT,
                occupation TEXT,
                goals TEXT,
                preferences TEXT,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Mood history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_history (
                mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                mood_score INTEGER NOT NULL,
                mood_label TEXT,
                notes TEXT,
                activities TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Journal entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_entries (
                journal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                sentiment_score REAL,
                sentiment_label TEXT,
                word_count INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Screening results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screening_results (
                screening_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                screening_type TEXT NOT NULL,
                date TEXT NOT NULL,
                score INTEGER NOT NULL,
                severity TEXT,
                responses TEXT,
                recommendations TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Comprehensive screening results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comprehensive_screenings (
                comp_screening_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                phq9_score INTEGER,
                gad7_score INTEGER,
                stress_score INTEGER,
                overall_index REAL,
                risk_level TEXT,
                recommendations TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mood_user_date ON mood_history(user_id, date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_journal_user_date ON journal_entries(user_id, date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_screening_user_date ON screening_results(user_id, date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_comp_screening_user_date ON comprehensive_screenings(user_id, date)')
        
        conn.commit()
        conn.close()
    
    # ==================== USER MANAGEMENT ====================
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return salt + pwd_hash.hex()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        salt = hashed[:32]
        stored_hash = hashed[32:]
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return pwd_hash.hex() == stored_hash
    
    def create_user(self, username: str, password: str, full_name: str, role: str = "user") -> Tuple[bool, str]:
        """Create new user account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, full_name, role))
            conn.commit()
            user_id = cursor.lastrowid
            
            # Create default profile
            cursor.execute('''
                INSERT INTO user_profiles (user_id) VALUES (?)
            ''', (user_id,))
            conn.commit()
            
            conn.close()
            return True, "Account created successfully"
        except sqlite3.IntegrityError:
            conn.close()
            return False, "Username already exists"
        except Exception as e:
            conn.close()
            return False, f"Error creating account: {str(e)}"
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Optional[int]]:
        """Authenticate user login"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, password_hash, active FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "Username not found", None
        
        user_id, password_hash, active = result
        
        if not active:
            conn.close()
            return False, "Account is disabled", None
        
        if self.verify_password(password, password_hash):
            # Update last login
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True, "Login successful", user_id
        
        conn.close()
        return False, "Invalid password", None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user information by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user information by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    # ==================== USER PROFILE ====================
    
    def save_user_profile(self, user_id: int, profile_data: Dict) -> bool:
        """Save or update user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE user_profiles 
                SET age = ?, gender = ?, occupation = ?, goals = ?, preferences = ?, updated_date = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (
                profile_data.get('age'),
                profile_data.get('gender'),
                profile_data.get('occupation'),
                json.dumps(profile_data.get('goals', [])),
                json.dumps(profile_data.get('preferences', {})),
                user_id
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error saving profile: {e}")
            return False
    
    def get_user_profile(self, user_id: int) -> Dict:
        """Get user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            profile = dict(result)
            # Parse JSON fields
            if profile.get('goals'):
                profile['goals'] = json.loads(profile['goals'])
            if profile.get('preferences'):
                profile['preferences'] = json.loads(profile['preferences'])
            return profile
        return {}
    
    # ==================== MOOD HISTORY ====================
    
    def add_mood_entry(self, user_id: int, date: str, mood_score: int, mood_label: str, notes: str = "", activities: List[str] = None) -> bool:
        """Add mood entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO mood_history (user_id, date, mood_score, mood_label, notes, activities)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, date, mood_score, mood_label, notes, json.dumps(activities or [])))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error adding mood entry: {e}")
            return False
    
    def get_mood_history(self, user_id: int, limit: int = None) -> List[Dict]:
        """Get mood history for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM mood_history WHERE user_id = ? ORDER BY date DESC'
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        conn.close()
        
        mood_list = []
        for row in results:
            mood = dict(row)
            if mood.get('activities'):
                mood['activities'] = json.loads(mood['activities'])
            mood_list.append(mood)
        
        return mood_list
    
    # ==================== JOURNAL ENTRIES ====================
    
    def add_journal_entry(self, user_id: int, date: str, title: str, content: str, 
                         sentiment_score: float = None, sentiment_label: str = None) -> bool:
        """Add journal entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            word_count = len(content.split())
            cursor.execute('''
                INSERT INTO journal_entries (user_id, date, title, content, sentiment_score, sentiment_label, word_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, date, title, content, sentiment_score, sentiment_label, word_count))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error adding journal entry: {e}")
            return False
    
    def get_journal_entries(self, user_id: int, limit: int = None) -> List[Dict]:
        """Get journal entries for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM journal_entries WHERE user_id = ? ORDER BY date DESC'
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    # ==================== SCREENING RESULTS ====================
    
    def add_screening_result(self, user_id: int, screening_type: str, date: str, score: int, 
                            severity: str, responses: Dict = None, recommendations: str = None) -> bool:
        """Add screening result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO screening_results (user_id, screening_type, date, score, severity, responses, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, screening_type, date, score, severity, json.dumps(responses or {}), recommendations))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error adding screening result: {e}")
            return False
    
    def get_screening_results(self, user_id: int, screening_type: str = None, limit: int = None) -> List[Dict]:
        """Get screening results for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if screening_type:
            query = 'SELECT * FROM screening_results WHERE user_id = ? AND screening_type = ? ORDER BY date DESC'
            params = (user_id, screening_type)
        else:
            query = 'SELECT * FROM screening_results WHERE user_id = ? ORDER BY date DESC'
            params = (user_id,)
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        screening_list = []
        for row in results:
            screening = dict(row)
            if screening.get('responses'):
                screening['responses'] = json.loads(screening['responses'])
            screening_list.append(screening)
        
        return screening_list
    
    # ==================== COMPREHENSIVE SCREENINGS ====================
    
    def add_comprehensive_screening(self, user_id: int, date: str, phq9_score: int, gad7_score: int, 
                                   stress_score: int, overall_index: float, risk_level: str, 
                                   recommendations: str = None) -> bool:
        """Add comprehensive screening result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO comprehensive_screenings 
                (user_id, date, phq9_score, gad7_score, stress_score, overall_index, risk_level, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, date, phq9_score, gad7_score, stress_score, overall_index, risk_level, recommendations))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error adding comprehensive screening: {e}")
            return False
    
    def get_comprehensive_screenings(self, user_id: int, limit: int = None) -> List[Dict]:
        """Get comprehensive screening results for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM comprehensive_screenings WHERE user_id = ? ORDER BY date DESC'
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    # ==================== STATISTICS & ANALYTICS ====================
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """Get comprehensive statistics for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Mood entries count
        cursor.execute('SELECT COUNT(*) FROM mood_history WHERE user_id = ?', (user_id,))
        stats['mood_entries'] = cursor.fetchone()[0]
        
        # Journal entries count
        cursor.execute('SELECT COUNT(*) FROM journal_entries WHERE user_id = ?', (user_id,))
        stats['journal_entries'] = cursor.fetchone()[0]
        
        # Screening results count
        cursor.execute('SELECT COUNT(*) FROM screening_results WHERE user_id = ?', (user_id,))
        stats['screening_results'] = cursor.fetchone()[0]
        
        # Comprehensive screenings count
        cursor.execute('SELECT COUNT(*) FROM comprehensive_screenings WHERE user_id = ?', (user_id,))
        stats['comprehensive_screenings'] = cursor.fetchone()[0]
        
        # Average mood score
        cursor.execute('SELECT AVG(mood_score) FROM mood_history WHERE user_id = ?', (user_id,))
        avg_mood = cursor.fetchone()[0]
        stats['average_mood'] = round(avg_mood, 1) if avg_mood else 0
        
        # Latest screening date
        cursor.execute('SELECT MAX(date) FROM screening_results WHERE user_id = ?', (user_id,))
        stats['last_screening_date'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    # ==================== DATA MIGRATION ====================
    
    def migrate_from_json(self, username: str, json_data_dir: str) -> bool:
        """Migrate data from JSON files to SQLite"""
        user = self.get_user_by_username(username)
        if not user:
            return False
        
        user_id = user['user_id']
        
        try:
            # Migrate mood history
            mood_file = os.path.join(json_data_dir, "mood_history.json")
            if os.path.exists(mood_file):
                with open(mood_file, 'r', encoding='utf-8') as f:
                    mood_data = json.load(f)
                    for entry in mood_data:
                        self.add_mood_entry(
                            user_id, 
                            entry.get('date'), 
                            entry.get('mood'), 
                            entry.get('mood_label', ''),
                            entry.get('notes', ''),
                            entry.get('activities', [])
                        )
            
            # Migrate journal entries
            journal_file = os.path.join(json_data_dir, "journal_entries.json")
            if os.path.exists(journal_file):
                with open(journal_file, 'r', encoding='utf-8') as f:
                    journal_data = json.load(f)
                    for entry in journal_data:
                        self.add_journal_entry(
                            user_id,
                            entry.get('date'),
                            entry.get('title', ''),
                            entry.get('content', ''),
                            entry.get('sentiment_score'),
                            entry.get('sentiment')
                        )
            
            # Migrate screening results
            screening_file = os.path.join(json_data_dir, "screening_results.json")
            if os.path.exists(screening_file):
                with open(screening_file, 'r', encoding='utf-8') as f:
                    screening_data = json.load(f)
                    for screening_type, results in screening_data.items():
                        if isinstance(results, list):
                            for result in results:
                                self.add_screening_result(
                                    user_id,
                                    screening_type,
                                    result.get('date'),
                                    result.get('score', 0),
                                    result.get('severity', ''),
                                    result.get('responses'),
                                    result.get('recommendations')
                                )
            
            return True
        except Exception as e:
            print(f"Error migrating data: {e}")
            return False


    # ==================== STREAK SYSTEM ====================
    
    def calculate_streak(self, user_id, activity_type='mood'):
        """Calculate current streak and longest streak for user"""
        from datetime import datetime, timedelta
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if activity_type == 'mood':
            cursor.execute('SELECT DISTINCT date FROM mood_history WHERE user_id = ? ORDER BY date DESC', (user_id,))
        elif activity_type == 'journal':
            cursor.execute('SELECT DISTINCT date FROM journal_entries WHERE user_id = ? ORDER BY date DESC', (user_id,))
        else:
            cursor.execute('SELECT DISTINCT date FROM (SELECT date FROM mood_history WHERE user_id = ? UNION SELECT date FROM journal_entries WHERE user_id = ?) ORDER BY date DESC', (user_id, user_id))
        
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not dates:
            return {'current_streak': 0, 'longest_streak': 0, 'last_activity_date': None, 'streak_status': 'inactive', 'days_since_last': 0, 'total_days': 0}
        
        date_objects = [datetime.strptime(d, '%Y-%m-%d').date() for d in dates]
        today = datetime.now().date()
        
        current_streak = 0
        expected_date = today
        
        for date in date_objects:
            if date == expected_date:
                current_streak += 1
                expected_date = date - timedelta(days=1)
            elif date == expected_date + timedelta(days=1):
                expected_date = date - timedelta(days=1)
            else:
                break
        
        longest_streak = 0
        temp_streak = 1
        
        for i in range(len(date_objects) - 1):
            diff = (date_objects[i] - date_objects[i + 1]).days
            if diff == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
        
        longest_streak = max(longest_streak, temp_streak, current_streak)
        
        last_activity = date_objects[0]
        days_since_last = (today - last_activity).days
        
        if days_since_last == 0:
            streak_status = 'active_today'
        elif days_since_last == 1:
            streak_status = 'active_yesterday'
        elif days_since_last <= 7:
            streak_status = 'recent'
        else:
            streak_status = 'inactive'
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'last_activity_date': dates[0],
            'streak_status': streak_status,
            'days_since_last': days_since_last,
            'total_days': len(dates)
        }
    
    def get_streak_statistics(self, user_id):
        """Get comprehensive streak statistics for all activities"""
        mood_streak = self.calculate_streak(user_id, 'mood')
        journal_streak = self.calculate_streak(user_id, 'journal')
        combined_streak = self.calculate_streak(user_id, 'any')
        
        return {
            'mood_tracking': mood_streak,
            'journaling': journal_streak,
            'combined': combined_streak,
            'achievements': self._calculate_achievements(user_id, combined_streak)
        }
    
    def _calculate_achievements(self, user_id, streak_data):
        """Calculate streak-based achievements"""
        achievements = []
        current = streak_data['current_streak']
        longest = streak_data['longest_streak']
        total = streak_data['total_days']
        
        streak_milestones = [
            (3, "3-Day Streak", "Getting started!"),
            (7, "Week Warrior", "7 days strong!"),
            (14, "Two Week Champion", "Consistency is key!"),
            (30, "Monthly Master", "30 days of dedication!")
        ]
        
        for days, title, description in streak_milestones:
            if longest >= days:
                achievements.append({'title': title, 'description': description, 'unlocked': True, 'days': days})
        
        return achievements
    
    def get_weekly_summary(self, user_id):
        """Get summary of last 7 days activity"""
        from datetime import datetime, timedelta
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        cursor.execute('SELECT date, COUNT(*) as count FROM (SELECT date FROM mood_history WHERE user_id = ? AND date >= ? UNION ALL SELECT date FROM journal_entries WHERE user_id = ? AND date >= ?) GROUP BY date ORDER BY date DESC', (user_id, week_ago.strftime('%Y-%m-%d'), user_id, week_ago.strftime('%Y-%m-%d')))
        
        daily_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute('SELECT AVG(mood_score) FROM mood_history WHERE user_id = ? AND date >= ?', (user_id, week_ago.strftime('%Y-%m-%d')))
        avg_mood = cursor.fetchone()[0]
        
        conn.close()
        
        week_summary = []
        for i in range(7):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            week_summary.append({
                'date': date_str,
                'day_name': date.strftime('%A'),
                'activity_count': daily_counts.get(date_str, 0),
                'active': date_str in daily_counts
            })
        
        return {
            'week_summary': list(reversed(week_summary)),
            'active_days': len(daily_counts),
            'total_activities': sum(daily_counts.values()),
            'average_mood': round(avg_mood, 1) if avg_mood else None,
            'completion_rate': (len(daily_counts) / 7) * 100
        }


# Global database instance
db = DatabaseManager()

    