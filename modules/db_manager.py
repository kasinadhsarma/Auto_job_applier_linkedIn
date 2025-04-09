'''
Database manager for tracking applications and verifying companies
'''

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import csv
import os

from config.settings import file_name, failed_file_name

class ApplicationDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('applications.db')
        self.cursor = self.conn.cursor()
        self._create_tables()
        
    def _create_tables(self):
        """Create necessary database tables"""
        # Companies table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            domain TEXT,
            verified BOOLEAN,
            glassdoor_rating FLOAT,
            employee_count INTEGER,
            industry TEXT,
            last_updated DATETIME
        )
        ''')
        
        # Applications table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY,
            job_id TEXT,
            platform TEXT,
            company_id INTEGER,
            job_title TEXT,
            application_date DATETIME,
            status TEXT,
            response_received BOOLEAN,
            response_date DATETIME,
            FOREIGN KEY(company_id) REFERENCES companies(id)
        )
        ''')
        
        # Application Questions table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS application_questions (
            id INTEGER PRIMARY KEY,
            application_id INTEGER,
            question TEXT,
            answer TEXT,
            successful BOOLEAN,
            FOREIGN KEY(application_id) REFERENCES applications(id)
        )
        ''')
        
        self.conn.commit()
        
    def add_company(self, company_data: Dict) -> int:
        """Add or update company information"""
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO companies 
            (name, domain, verified, glassdoor_rating, employee_count, industry, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_data['name'],
                company_data.get('domain'),
                company_data.get('verified', False),
                company_data.get('glassdoor_rating'),
                company_data.get('employee_count'),
                company_data.get('industry'),
                datetime.now()
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error adding company: {e}")
            return None
            
    def track_application(self, application_data: Dict) -> int:
        """Track a new job application"""
        try:
            # First ensure company exists
            company_id = self.add_company({
                'name': application_data['company_name']
            })
            
            self.cursor.execute('''
            INSERT INTO applications
            (job_id, platform, company_id, job_title, application_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                application_data['job_id'],
                application_data['platform'],
                company_id,
                application_data['job_title'],
                datetime.now(),
                application_data['status']
            ))
            
            application_id = self.cursor.lastrowid
            
            # Track questions if any
            if 'questions' in application_data:
                for q in application_data['questions']:
                    self.cursor.execute('''
                    INSERT INTO application_questions
                    (application_id, question, answer, successful)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        application_id,
                        q['question'],
                        q['answer'],
                        q.get('successful', True)
                    ))
                    
            self.conn.commit()
            return application_id
            
        except Exception as e:
            print(f"Error tracking application: {e}")
            return None
            
    def is_company_verified(self, company_name: str) -> bool:
        """Check if a company is verified"""
        try:
            self.cursor.execute('''
            SELECT verified FROM companies
            WHERE name = ?
            ''', (company_name,))
            
            result = self.cursor.fetchone()
            return bool(result[0]) if result else False
            
        except Exception as e:
            print(f"Error checking company verification: {e}")
            return False
            
    def get_application_history(self, company_name: Optional[str] = None) -> pd.DataFrame:
        """Get application history, optionally filtered by company"""
        query = '''
        SELECT 
            a.job_id,
            a.platform,
            c.name as company_name,
            a.job_title,
            a.application_date,
            a.status,
            a.response_received,
            a.response_date
        FROM applications a
        JOIN companies c ON a.company_id = c.id
        '''
        
        if company_name:
            query += ' WHERE c.name = ?'
            df = pd.read_sql_query(query, self.conn, params=(company_name,))
        else:
            df = pd.read_sql_query(query, self.conn)
            
        return df
        
    def export_to_csv(self):
        """Export application history to CSV files"""
        df = self.get_application_history()
        
        # Split into successful and failed applications
        successful = df[df['status'] == 'success']
        failed = df[df['status'] == 'failed']
        
        # Ensure directories exist
        for path in [file_name, failed_file_name]:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Export
        successful.to_csv(file_name, index=False)
        failed.to_csv(failed_file_name, index=False)
        
    def close(self):
        """Close database connection"""
        self.conn.close()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()