"""
FastAPI Article Generation Web Application
Provides a clean web interface for keyword-based article generation and deployment.
Uses existing articleGen system without modification.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import json
import subprocess
import asyncio
import logging
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import sqlite3
from pathlib import Path
import shutil
from dotenv import load_dotenv
import csv
import re
import glob

# Load environment variables from .env file
load_dotenv()

# Add the project directory to Python path
import sys
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Validate environment setup
def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = {
        "GEM_API_KEY": "Gemini API key for article generation",
        "FTP_HOST": "FTP server hostname", 
        "FTP_USER": "FTP username",
        "FTP_PASS": "FTP password"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.warning("Missing required environment variables:")
        for var in missing_vars:
            logger.warning(f"   • {var}")
        return False
    
    logger.info("✅ Environment validation passed")
    return True

# Initialize FastAPI app
app = FastAPI(
    title="SEO Article Generator",
    description="High-performance article generation and deployment system",
    version="1.0.0"
)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Setup directories
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "webapp_static"
TEMPLATES_DIR = BASE_DIR / "webapp_templates"
DATABASE_PATH = BASE_DIR / "webapp_users.db"

# Create directories if they don't exist
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Global job tracking
active_jobs: Dict[str, Dict] = {}

# Trend refresh / manual pipeline job tracking
trend_refresh_jobs: Dict[str, Dict] = {}

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# Data Models
# ============================================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class WebsiteConfig(BaseModel):
    website_url: str = Field(default="https://countrysnews.com")
    website_name: str = Field(default="Country's News")
    author_name: str = Field(default="News Team")
    author_email: str = Field(default="contact@countrysnews.com")
    social_twitter: Optional[str] = None
    social_facebook: Optional[str] = None

class FTPConfig(BaseModel):
    ftp_host: str = Field(default=os.getenv("FTP_HOST", "212.1.209.3"))
    ftp_username: str
    ftp_password: str
    remote_directory: str = Field(default=os.getenv("REMOTE_DIRECTORY", "/public_html"))
    max_workers: int = Field(default=int(os.getenv("MAX_WORKERS", "20")), ge=1, le=50)

class ContentConfig(BaseModel):
    articles_per_keyword: int = Field(default=3, ge=1, le=10)
    target_regions: List[str] = Field(default=["US", "IN", "GB"])
    generate_images: bool = Field(default=True)
    article_min_length: int = Field(default=800, ge=400, le=3000)
    seo_focus: bool = Field(default=True)

class ArticleGenerationRequest(BaseModel):
    keywords: List[str] = Field(..., min_items=1, max_items=20)
    website_config: WebsiteConfig
    ftp_config: FTPConfig
    content_config: ContentConfig
    deploy_immediately: bool = Field(default=False)

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: int  # 0-100
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict] = None

# ============================================================
# Database Setup
# ============================================================

def init_database():
    """Initialize SQLite database for users and configurations"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # User configurations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            config_name TEXT NOT NULL,
            config_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Generation history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            job_id TEXT UNIQUE NOT NULL,
            keywords TEXT NOT NULL,
            status TEXT NOT NULL,
            articles_generated INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_default_admin():
    """Create default admin user if no users exist"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if any users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # Create default admin user
        default_username = "admin"
        default_email = "admin@articlegen.local"
        default_password = "admin123"
        
        hashed_password = pwd_context.hash(default_password)
        
        try:
            cursor.execute(
                "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
                (default_username, default_email, hashed_password)
            )
            conn.commit()
            logger.info("✅ Default admin user created")
            logger.info(f"📧 Username: {default_username}")
            logger.info(f"🔑 Password: {default_password}")
            logger.info("⚠️  Please change these credentials after first login!")
        except sqlite3.IntegrityError:
            logger.warning("Default admin user already exists")
    
    conn.close()

# ============================================================
# Authentication Functions
# ============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        logger.info(f"Validating token: {credentials.credentials[:20]}...")
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token payload missing 'sub' field")
            raise HTTPException(status_code=401, detail="Invalid authentication")
        logger.info(f"Token validated successfully for user: {username}")
        return username
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError as e:
        logger.warning(f"JWT validation error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication")

# ============================================================
# Database Helper Functions
# ============================================================

def create_user(user: UserCreate) -> bool:
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        hashed_password = get_password_hash(user.password)
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
            (user.username, user.email, hashed_password)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username: str, password: str) -> Optional[dict]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, hashed_password FROM users WHERE username = ? AND is_active = TRUE",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user[3]):
        return {"id": user[0], "username": user[1], "email": user[2]}
    return None

def save_user_config(username: str, config_name: str, config_data: dict) -> bool:
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return False
        
        user_id = user[0]
        config_json = json.dumps(config_data)
        
        # Insert or update configuration
        cursor.execute(
            "INSERT OR REPLACE INTO user_configs (user_id, config_name, config_data) VALUES (?, ?, ?)",
            (user_id, config_name, config_json)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

# ============================================================
# Article Generation Functions (Using Existing System)
# ============================================================

async def generate_articles_background(job_id: str, request: ArticleGenerationRequest, username: str):
    """Background task to generate articles using existing system"""
    
    try:
        # Validate environment first
        if not os.getenv("GEM_API_KEY"):
            active_jobs[job_id]["status"] = "failed"
            active_jobs[job_id]["message"] = "❌ GEMINI_API_KEY not configured"
            return

        # Update job status
        active_jobs[job_id]["status"] = "running"
        active_jobs[job_id]["progress"] = 10
        active_jobs[job_id]["message"] = "Preparing article generation environment..."
        
        # Ensure we're in the correct directory
        original_dir = os.getcwd()
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        try:
            # Import and run generation directly (avoid subprocess issues)
            from super_article_manager import SuperArticleManager, generate_articles_from_keywords
            
            active_jobs[job_id]["progress"] = 20
            active_jobs[job_id]["message"] = "Initializing article manager..."
            
            # Initialize manager
            manager = SuperArticleManager()
            manager.load_articles()
            
            active_jobs[job_id]["progress"] = 30
            active_jobs[job_id]["message"] = "Generating SEO-optimized articles..."
            
            # Set environment variables for the generation process
            env_backup = {}
            env_vars = {
                "FTP_HOST": request.ftp_config.ftp_host,
                "FTP_USER": request.ftp_config.ftp_username,
                "FTP_PASS": request.ftp_config.ftp_password,
                "REMOTE_DIRECTORY": request.ftp_config.remote_directory,
                "LOCAL_DIRECTORY": os.getenv("LOCAL_DIRECTORY", os.path.join(project_dir, "output")),
                "WEBSITE_URL": request.website_config.website_url,
                "WEBSITE_NAME": request.website_config.website_name,
                "AUTHOR_NAME": request.website_config.author_name,
                "AUTHOR_EMAIL": request.website_config.author_email
            }
            
            # Backup and set environment variables
            for key, value in env_vars.items():
                env_backup[key] = os.environ.get(key)
                os.environ[key] = str(value)
            
            try:
                # Generate articles using the standalone function
                total_keywords = len(request.keywords)
                articles_generated = 0
                
                # Get target region
                region = request.content_config.target_regions[0] if request.content_config.target_regions else "India"
                
                active_jobs[job_id]["progress"] = 40
                active_jobs[job_id]["message"] = f"Generating articles for keywords in {region}..."
                
                # For each keyword, generate the requested number of articles
                for i, keyword in enumerate(request.keywords):
                    progress = 40 + (40 * i // total_keywords)
                    active_jobs[job_id]["progress"] = progress
                    active_jobs[job_id]["message"] = f"Processing keyword: '{keyword}' ({i+1}/{total_keywords})"
                    
                    # Generate multiple articles for each keyword if requested
                    articles_per_keyword = request.content_config.articles_per_keyword
                    keyword_list = [keyword] * articles_per_keyword  # Repeat keyword for multiple articles
                    
                    # Use the generate_articles_from_keywords function
                    await generate_articles_from_keywords(
                        manager=manager,
                        keywords=keyword_list,
                        region=region,
                        custom_prompt="",
                        skip_existing=False  # Don't skip existing for webapp requests
                    )
                    
                    articles_generated += articles_per_keyword
                
                active_jobs[job_id]["progress"] = 80
                active_jobs[job_id]["message"] = "Saving generated articles..."
                
                # Save the generated articles
                manager.save_articles()
                
                active_jobs[job_id]["progress"] = 85
                active_jobs[job_id]["message"] = "Generating images and finalizing..."
                
                # Generate images if requested
                if request.content_config.generate_images:
                    active_jobs[job_id]["message"] = "Generating article images..."
                    # Import the function from the module
                    from super_article_manager import generate_images_for_articles
                    await generate_images_for_articles(manager)
                
                # Deploy if requested
                if request.deploy_immediately:
                    active_jobs[job_id]["progress"] = 90
                    active_jobs[job_id]["message"] = "Deploying to website..."
                    
                    # Run deployment using existing scripts
                    deploy_cmd = ["python3", "ultraFastSync.py"]
                    env = os.environ.copy()
                    
                    process = subprocess.run(
                        deploy_cmd,
                        capture_output=True,
                        text=True,
                        cwd=project_dir,
                        env=env
                    )
                    
                    if process.returncode != 0:
                        logger.warning(f"Deployment warning: {process.stderr}")
                
                active_jobs[job_id]["progress"] = 100
                active_jobs[job_id]["status"] = "completed"
                active_jobs[job_id]["message"] = f"✅ Successfully generated {articles_generated} articles!"
                active_jobs[job_id]["completed_at"] = datetime.now().isoformat()
                active_jobs[job_id]["results"] = {
                    "articles_generated": articles_generated,
                    "keywords_processed": request.keywords,
                    "deployed": request.deploy_immediately
                }
                
                # Log successful completion
                logger.info(f"Successfully generated {articles_generated} articles for user {username}")
                
            finally:
                # Restore environment variables
                for key, value in env_backup.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value
                        
        except ImportError as e:
            logger.error(f"Import error in generation: {e}")
            active_jobs[job_id]["status"] = "failed"
            active_jobs[job_id]["message"] = f"❌ System configuration error: {str(e)}"
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            active_jobs[job_id]["status"] = "failed"
            active_jobs[job_id]["message"] = f"❌ Generation failed: {str(e)}"
            
        finally:
            # Always restore original directory
            os.chdir(original_dir)
            
    except Exception as e:
        logger.error(f"Background task error: {e}")
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["message"] = f"❌ Task failed: {str(e)}"
        
        # Update database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE generation_history SET status = ?, articles_generated = ?, completed_at = CURRENT_TIMESTAMP WHERE job_id = ?",
            ("completed", len(request.keywords) * request.content_config.articles_per_keyword, job_id)
        )
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Article generation failed for job {job_id}: {e}")
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["message"] = f"Generation failed: {str(e)}"
        active_jobs[job_id]["completed_at"] = datetime.now()
        
        # Update database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE generation_history SET status = ?, completed_at = CURRENT_TIMESTAMP WHERE job_id = ?",
            ("failed", job_id)
        )
        conn.commit()
        conn.close()

# ============================================================
# API Routes
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("🚀 Starting SEO Article Generator WebApp...")

    # Validate environment
    if not validate_environment():
        logger.warning("⚠️  Warning: Some environment variables are missing. Some features may not work.")

    # Initialize database
    init_database()
    create_default_admin()

    # Security check: warn if default credentials are still in use
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT hashed_password FROM users WHERE username = 'admin' LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row and pwd_context.verify("admin123", row[0]):
            logger.warning("=" * 60)
            logger.warning("🔐 SECURITY WARNING: The admin account is still using")
            logger.warning("   the default password 'admin123'.")
            logger.warning("   Change it immediately via the webapp settings or")
            logger.warning("   by re-creating the user in the database.")
            logger.warning("=" * 60)
    except Exception:
        pass  # Non-blocking; don't prevent startup

    logger.info("✅ SEO Article Generator API started successfully")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/auth/register", response_model=dict)
async def register(user: UserCreate):
    """Register new user"""
    if create_user(user):
        return {"message": "User created successfully"}
    else:
        raise HTTPException(status_code=400, detail="Username or email already exists")

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    """User login"""
    authenticated_user = authenticate_user(user.username, user.password)
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": authenticated_user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/generate", response_model=dict)
async def generate_articles(
    request: ArticleGenerationRequest,
    background_tasks: BackgroundTasks,
    username: str = Depends(get_user_from_token)
):
    """Start article generation process"""
    
    logger.info(f"Article generation request from user: {username}")
    logger.info(f"Keywords: {request.keywords}")
    
    # Create unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job tracking
    active_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "message": "Job queued for processing...",
        "created_at": datetime.now(),
        "completed_at": None,
        "results": None,
        "username": username
    }
    
    # Save to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user:
        cursor.execute(
            "INSERT INTO generation_history (user_id, job_id, keywords, status) VALUES (?, ?, ?, ?)",
            (user[0], job_id, json.dumps(request.keywords), "pending")
        )
        conn.commit()
    conn.close()
    
    # Start background task
    background_tasks.add_task(generate_articles_background, job_id, request, username)
    
    return {"job_id": job_id, "message": "Article generation started", "status": "pending"}

@app.get("/api/job/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str, username: str = Depends(get_user_from_token)):
    """Get job status and progress"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    if job["username"] != username:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return JobStatus(**job)

@app.get("/api/history", response_model=List[dict])
async def get_generation_history(username: str = Depends(get_user_from_token)):
    """Get user's generation history"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT h.job_id, h.keywords, h.status, h.articles_generated, h.created_at, h.completed_at
           FROM generation_history h
           JOIN users u ON h.user_id = u.id
           WHERE u.username = ?
           ORDER BY h.created_at DESC
           LIMIT 50""",
        (username,)
    )
    history = cursor.fetchall()
    conn.close()
    
    return [
        {
            "job_id": row[0],
            "keywords": json.loads(row[1]),
            "status": row[2],
            "articles_generated": row[3],
            "created_at": row[4],
            "completed_at": row[5]
        }
        for row in history
    ]

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len(active_jobs),
        "system": "SEO Article Generator"
    }

# ============================================================
# Trends & Scheduler API Routes
# ============================================================

@app.get("/api/trends")
async def get_current_trends(username: str = Depends(get_user_from_token)):
    """Get current cached trending keywords from output CSVs"""
    try:
        output_dir = BASE_DIR / "output"
        if not output_dir.exists():
            return {"trends": [], "total": 0, "last_updated": None, "source_files": []}

        # Priority: all_seo_filtered_trends.csv > master_seo_keywords.csv > *_filtered.csv > any csv
        csv_files = []
        for preferred in [output_dir / "all_seo_filtered_trends.csv",
                          output_dir / "master_seo_keywords.csv"]:
            if preferred.exists():
                csv_files = [preferred]
                break
        if not csv_files:
            csv_files = list(output_dir.glob("*_daily_trends_filtered.csv"))
        if not csv_files:
            csv_files = list(output_dir.glob("*.csv"))

        seen: dict = {}
        for csv_file in csv_files:
            try:
                with open(csv_file, newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    if not header:
                        continue
                    if 'formatted' in header or (len(header) >= 3 and header[0].lower() in ('country', 'region')):
                        for row in reader:
                            if len(row) >= 3:
                                try:
                                    region = row[0].strip()
                                    keyword = row[1].strip()
                                    searches = int(row[2])
                                    key = (region, keyword)
                                    if key not in seen or seen[key] < searches:
                                        seen[key] = searches
                                except (ValueError, IndexError):
                                    continue
                    else:
                        f.seek(0)
                        next(reader, None)  # skip header
                        for row in reader:
                            if not row:
                                continue
                            line = row[0]
                            m = re.match(r'\[([A-Z]{2})\]\s*(.*?):\s*([\d,]+)\s*searches', line)
                            if m:
                                region = m.group(1)
                                keyword = m.group(2).strip()
                                searches = int(m.group(3).replace(',', ''))
                                key = (region, keyword)
                                if key not in seen or seen[key] < searches:
                                    seen[key] = searches
            except Exception as e:
                logger.warning(f"Error reading {csv_file.name}: {e}")
                continue

        trends = [
            {"region": k[0], "keyword": k[1], "searches": v}
            for k, v in sorted(seen.items(), key=lambda x: x[1], reverse=True)
        ]

        last_updated = None
        for f in csv_files:
            mt = f.stat().st_mtime if f.exists() else None
            if mt and (last_updated is None or mt > last_updated):
                last_updated = mt

        return {
            "trends": trends[:50],
            "total": len(trends),
            "last_updated": datetime.fromtimestamp(last_updated).isoformat() if last_updated else None,
            "source_files": [f.name for f in csv_files]
        }
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        return {"trends": [], "total": 0, "last_updated": None, "source_files": [], "error": str(e)}


async def _run_background_command(job_id: str, label: str, *cmd: str):
    """Generic helper to run a subprocess and track it in trend_refresh_jobs."""
    trend_refresh_jobs[job_id]["status"] = "running"
    trend_refresh_jobs[job_id]["message"] = f"{label} running..."
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(BASE_DIR),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        stdout, _ = await proc.communicate()
        output = stdout.decode(errors="replace") if stdout else ""
        status = "completed" if proc.returncode == 0 else "failed"
        trend_refresh_jobs[job_id].update({
            "status": status,
            "completed_at": datetime.now().isoformat(),
            "message": f"{label} {'completed successfully' if status == 'completed' else f'failed (exit {proc.returncode})'}",
            "output": output[-2000:]
        })
    except Exception as e:
        trend_refresh_jobs[job_id].update({
            "status": "failed",
            "completed_at": datetime.now().isoformat(),
            "message": f"{label} error: {e}",
            "output": ""
        })


@app.post("/api/trends/refresh")
async def refresh_trends(background_tasks: BackgroundTasks,
                         username: str = Depends(get_user_from_token)):
    """Fetch fresh trending data from Google Trends in the background."""
    job_id = str(uuid.uuid4())
    trend_refresh_jobs[job_id] = {
        "job_id": job_id,
        "type": "trends_refresh",
        "status": "pending",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "message": "Queued – connecting to Google Trends...",
        "output": ""
    }
    background_tasks.add_task(
        _run_background_command, job_id, "Trends refresh",
        "python3", str(BASE_DIR / "fetch_fresh_trends.py")
    )
    return {"job_id": job_id, "message": "Trends refresh started"}


@app.get("/api/trends/refresh-status/{job_id}")
async def get_trends_refresh_status(job_id: str,
                                    username: str = Depends(get_user_from_token)):
    """Poll the status of a trends refresh (or pipeline) job."""
    if job_id not in trend_refresh_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return trend_refresh_jobs[job_id]


@app.get("/api/scheduler/status")
async def get_scheduler_status(username: str = Depends(get_user_from_token)):
    """Return cron schedule, next run time, last run outcome, and recent log lines."""
    now = datetime.now()
    today_6pm = now.replace(hour=18, minute=0, second=0, microsecond=0)
    next_run = today_6pm if now < today_6pm else today_6pm + timedelta(days=1)

    status = {
        "cron_expression": "0 18 * * *",
        "schedule_description": "Daily at 6:00 PM IST",
        "next_run": next_run.strftime("%Y-%m-%dT%H:%M:%S"),
        "last_run": None,
        "exit_code": None,
        "last_status": "unknown",
        "recent_log": []
    }

    # Prefer the machine-readable status file written by cron_wrapper.sh
    status_file = BASE_DIR / "logs" / "scheduler_status.json"
    if status_file.exists():
        try:
            with open(status_file) as f:
                saved = json.load(f)
            status["last_run"] = saved.get("last_run")
            status["exit_code"] = saved.get("exit_code")
            status["last_status"] = saved.get("status", "unknown")
        except Exception as e:
            logger.warning(f"Could not read scheduler_status.json: {e}")

    # Append the last 30 lines of the most recent daily log
    try:
        log_dir = BASE_DIR / "logs"
        log_files = sorted(log_dir.glob("auto_publish_*.log"), reverse=True)
        if log_files:
            lines = log_files[0].read_text(errors="replace").splitlines()
            status["recent_log"] = lines[-30:]
            # Fall back for last_run if status file missing
            if not status["last_run"] and lines:
                status["last_run"] = lines[0][:19]  # first 19 chars = timestamp
    except Exception as e:
        logger.warning(f"Could not read auto_publish log: {e}")

    return status


@app.post("/api/scheduler/run-now")
async def run_pipeline_now(background_tasks: BackgroundTasks,
                           username: str = Depends(get_user_from_token)):
    """Manually trigger the full auto_publish.sh pipeline."""
    job_id = str(uuid.uuid4())
    trend_refresh_jobs[job_id] = {
        "job_id": job_id,
        "type": "pipeline",
        "status": "pending",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "message": "Pipeline queued – this may take several minutes...",
        "output": ""
    }
    background_tasks.add_task(
        _run_background_command, job_id, "Pipeline",
        "/bin/bash", str(BASE_DIR / "auto_publish.sh")
    )
    return {"job_id": job_id, "message": "Pipeline started"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
