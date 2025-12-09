<<<<<<< HEAD
# TikTok SAAS - Automated Reddit Video Generator

An automated TikTok video creation system that scrapes Reddit posts, generates AI-powered scripts, creates voiceovers, and produces engaging short-form videos with synchronized subtitles.

## 🎯 Overview

This project automates the entire workflow of creating TikTok-style videos from Reddit content:

1. **Scrapes** top Reddit posts from specified subreddits
2. **Formats** content using Google Gemini AI for optimal narration
3. **Generates** voiceovers using Microsoft Edge-TTS (free, high-quality voices)
4. **Creates** videos with Minecraft background loops, title cards, and synchronized subtitles
5. **Processes** videos in the background using Celery for scalability

## ✨ Features

- 🤖 **AI-Powered Script Generation**: Uses Google Gemini 2.5 Flash to format Reddit posts into engaging narration scripts
- 🎙️ **Smart Voice Selection**: Automatically detects narrator gender and selects appropriate voice (male/female)
- 🎬 **Professional Video Production**: 
  - Custom title cards with TikTok handle
  - Synchronized subtitles using OpenAI Whisper
  - Minecraft background video loops
  - Automatic video splitting for longer content
- 📊 **Background Processing**: Celery-based task queue for scalable video generation
- 🔄 **Duplicate Prevention**: Tracks seen posts to avoid re-processing
- 🌐 **REST API**: Flask-based API for programmatic video creation
- 📈 **Monitoring**: Flower dashboard for Celery task monitoring

## 🛠️ Tech Stack

- **Python 3.12+**
- **Flask**: Web framework for API endpoints
- **Celery**: Distributed task queue
- **Redis**: Message broker and result backend
- **Google Gemini API**: AI script formatting
- **Microsoft Edge-TTS**: Free text-to-speech
- **OpenAI Whisper**: Audio transcription and subtitle timing
- **MoviePy**: Video editing and composition
- **PRAW**: Reddit API wrapper
- **Docker**: Containerization support

## 📋 Prerequisites

- Python 3.12 or higher
- FFmpeg (required for video processing)
- Redis server
- Google Gemini API key
- Reddit API credentials (client ID, secret, user agent)
- Minecraft loop video file (or any background video)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd "Tiktok SAAS"
```

### 2. Create Virtual Environment

**On Linux/WSL:**
```bash
python3 -m venv ~/tiktok_venv
source ~/tiktok_venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg -y
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH

### 5. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# Reddit API Credentials
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_app_name/1.0

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Video Settings
MINECRAFT_CLIP_PATH=minecraft_loop.mp4
TIKTOK_HANDLE=@YourTikTokHandle
```

### 6. Prepare Assets

- Place your background video (e.g., `minecraft_loop.mp4`) in the project root
- Ensure fonts are in the `fonts/` directory:
  - `Arial.TTF` (or system default)
  - `LuckiestGuy-Regular.ttf` (for stylized text)

## 🎮 Usage

### Start Redis Server

**Linux/WSL:**
```bash
sudo service redis-server start
```

**macOS:**
```bash
brew services start redis
```

**Windows:**
Download and run Redis from [redis.io](https://redis.io/download)

### Method 1: Direct Script Execution

**Terminal 1 - Start Celery Worker:**
```bash
cd /mnt/d/Tiktok\ SAAS  # or your project path
source ~/tiktok_venv/bin/activate  # or venv\Scripts\activate on Windows
celery -A celeryconfig worker --loglevel=info
```

**Terminal 2 - Trigger Video Creation:**
```bash
cd /mnt/d/Tiktok\ SAAS
source ~/tiktok_venv/bin/activate
python trigger_video_creation.py
```

### Method 2: Flask API

**Terminal 1 - Start Celery Worker:**
```bash
celery -A celeryconfig worker --loglevel=info
```

**Terminal 2 - Start Flask API:**
```bash
python -m flask --app app.main run
# Or with gunicorn:
gunicorn --bind 0.0.0.0:5000 app.main:app
```

**Terminal 3 - (Optional) Start Flower Monitor:**
```bash
celery -A celeryconfig flower
```

**API Endpoints:**

- `POST /create` - Create a video from post data
  ```json
  {
    "post_data": {
      "title": "My Reddit Story",
      "text": "This is the story content..."
    }
  }
  ```

- `GET /status/<task_id>` - Check video creation status

### Method 3: Docker Compose

```bash
docker-compose up
```

This starts:
- Redis server
- Flask web server (port 5000)
- Celery worker
- Flower dashboard (port 5555)

## 📁 Project Structure

```
Tiktok SAAS/
├── app/
│   ├── __init__.py
│   ├── main.py              # Flask API endpoints
│   ├── scraper.py            # Reddit post scraping
│   ├── scripter.py           # Gemini AI script generation
│   ├── video_maker.py        # Video creation with MoviePy
│   ├── celery_app.py         # Celery app configuration
│   └── tasks/
│       ├── __init__.py
│       └── tasks.py          # Celery task definitions
├── fonts/                    # Font files for video text
├── output_videos/            # Generated video files
├── tracking_files/           # Seen posts and generated scripts
├── celeryconfig.py           # Celery configuration
├── trigger_video_creation.py # Script to trigger video creation
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker services configuration
├── Dockerfile               # Docker image definition
└── README.md                # This file
```

## ⚙️ Configuration

### Video Settings

Edit `app/video_maker.py` to customize:

- `OUTPUT_SIZE`: Video resolution (default: 1080x1920 for TikTok)
- `TITLE_FONT_SIZE`: Title card font size
- `SUBTITLE_FONT_SIZE`: Subtitle font size
- `SUBTITLE_VERTICAL_POSITION`: Subtitle position on screen
- `WORDS_PER_MINUTE`: Narration speed (default: 150)

### Subreddit Selection

Edit `trigger_video_creation.py`:

```python
subreddits = ["TIFU", "AITA", "EntitledParents"]  # Add your subreddits
posts = get_reddit_posts(subreddits, limit=1)      # Adjust limit
```

### Video Splitting

Videos longer than 2 minutes are automatically split into parts. Each part is kept close to 1 minute in length.

## 🔧 Troubleshooting

### Permission Errors on WSL

If you encounter permission errors when installing packages, move your venv to the Linux filesystem:

```bash
deactivate
rm -rf venv
python3 -m venv ~/tiktok_venv
source ~/tiktok_venv/bin/activate
```

### FFmpeg Not Found

Ensure FFmpeg is installed and in your PATH:
```bash
ffmpeg -version
```

### Redis Connection Error

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Whisper Model Download

The first run will download the Whisper model (~150MB). Ensure you have internet connectivity.

## 📝 Notes

- **Voice Selection**: The system uses Gemini AI to detect narrator gender from the story content
- **Abbreviation Expansion**: Common Reddit abbreviations (TIFU, AITA, etc.) are automatically expanded for better narration
- **Duplicate Prevention**: Posts are tracked in `tracking_files/seen_posts.txt` to avoid re-processing
- **Video Quality**: Uses `ultrafast` encoding preset for speed. Adjust in `video_maker.py` for better quality

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Google Gemini for AI script generation
- Microsoft Edge-TTS for free, high-quality text-to-speech
- OpenAI Whisper for transcription
- MoviePy for video editing capabilities
- Reddit community for content inspiration

---

**Happy Video Creating! 🎬**

=======
# TikTok SAAS - Automated Reddit Video Generator

An automated TikTok video creation system that scrapes Reddit posts, generates AI-powered scripts, creates voiceovers, and produces engaging short-form videos with synchronized subtitles.

## 🎯 Overview

This project automates the entire workflow of creating TikTok-style videos from Reddit content:

1. **Scrapes** top Reddit posts from specified subreddits
2. **Formats** content using Google Gemini AI for optimal narration
3. **Generates** voiceovers using Microsoft Edge-TTS (free, high-quality voices)
4. **Creates** videos with Minecraft background loops, title cards, and synchronized subtitles
5. **Processes** videos in the background using Celery for scalability

## ✨ Features

- 🤖 **AI-Powered Script Generation**: Uses Google Gemini 2.5 Flash to format Reddit posts into engaging narration scripts
- 🎙️ **Smart Voice Selection**: Automatically detects narrator gender and selects appropriate voice (male/female)
- 🎬 **Professional Video Production**: 
  - Custom title cards with TikTok handle
  - Synchronized subtitles using OpenAI Whisper
  - Minecraft background video loops
  - Automatic video splitting for longer content
- 📊 **Background Processing**: Celery-based task queue for scalable video generation
- 🔄 **Duplicate Prevention**: Tracks seen posts to avoid re-processing
- 🌐 **REST API**: Flask-based API for programmatic video creation
- 📈 **Monitoring**: Flower dashboard for Celery task monitoring

## 🛠️ Tech Stack

- **Python 3.12+**
- **Flask**: Web framework for API endpoints
- **Celery**: Distributed task queue
- **Redis**: Message broker and result backend
- **Google Gemini API**: AI script formatting
- **Microsoft Edge-TTS**: Free text-to-speech
- **OpenAI Whisper**: Audio transcription and subtitle timing
- **MoviePy**: Video editing and composition
- **PRAW**: Reddit API wrapper
- **Docker**: Containerization support

## 📋 Prerequisites

- Python 3.12 or higher
- FFmpeg (required for video processing)
- Redis server
- Google Gemini API key
- Reddit API credentials (client ID, secret, user agent)
- Minecraft loop video file (or any background video)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd "Tiktok SAAS"
```

### 2. Create Virtual Environment

**On Linux/WSL:**
```bash
python3 -m venv ~/tiktok_venv
source ~/tiktok_venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg -y
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH

### 5. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# Reddit API Credentials
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_app_name/1.0

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Video Settings
MINECRAFT_CLIP_PATH=minecraft_loop.mp4
TIKTOK_HANDLE=@YourTikTokHandle
```

### 6. Prepare Assets

- Place your background video (e.g., `minecraft_loop.mp4`) in the project root
- Ensure fonts are in the `fonts/` directory:
  - `Arial.TTF` (or system default)
  - `LuckiestGuy-Regular.ttf` (for stylized text)

## 🎮 Usage

### Start Redis Server

**Linux/WSL:**
```bash
sudo service redis-server start
```

**macOS:**
```bash
brew services start redis
```

**Windows:**
Download and run Redis from [redis.io](https://redis.io/download)

### Method 1: Direct Script Execution

**Terminal 1 - Start Celery Worker:**
```bash
cd /mnt/d/Tiktok\ SAAS  # or your project path
source ~/tiktok_venv/bin/activate  # or venv\Scripts\activate on Windows
celery -A celeryconfig worker --loglevel=info
```

**Terminal 2 - Trigger Video Creation:**
```bash
cd /mnt/d/Tiktok\ SAAS
source ~/tiktok_venv/bin/activate
python trigger_video_creation.py
```

### Method 2: Flask API

**Terminal 1 - Start Celery Worker:**
```bash
celery -A celeryconfig worker --loglevel=info
```

**Terminal 2 - Start Flask API:**
```bash
python -m flask --app app.main run
# Or with gunicorn:
gunicorn --bind 0.0.0.0:5000 app.main:app
```

**Terminal 3 - (Optional) Start Flower Monitor:**
```bash
celery -A celeryconfig flower
```

**API Endpoints:**

- `POST /create` - Create a video from post data
  ```json
  {
    "post_data": {
      "title": "My Reddit Story",
      "text": "This is the story content..."
    }
  }
  ```

- `GET /status/<task_id>` - Check video creation status

### Method 3: Docker Compose

```bash
docker-compose up
```

This starts:
- Redis server
- Flask web server (port 5000)
- Celery worker
- Flower dashboard (port 5555)

## 📁 Project Structure

```
Tiktok SAAS/
├── app/
│   ├── __init__.py
│   ├── main.py              # Flask API endpoints
│   ├── scraper.py            # Reddit post scraping
│   ├── scripter.py           # Gemini AI script generation
│   ├── video_maker.py        # Video creation with MoviePy
│   ├── celery_app.py         # Celery app configuration
│   └── tasks/
│       ├── __init__.py
│       └── tasks.py          # Celery task definitions
├── fonts/                    # Font files for video text
├── output_videos/            # Generated video files
├── tracking_files/           # Seen posts and generated scripts
├── celeryconfig.py           # Celery configuration
├── trigger_video_creation.py # Script to trigger video creation
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker services configuration
├── Dockerfile               # Docker image definition
└── README.md                # This file
```

## ⚙️ Configuration

### Video Settings

Edit `app/video_maker.py` to customize:

- `OUTPUT_SIZE`: Video resolution (default: 1080x1920 for TikTok)
- `TITLE_FONT_SIZE`: Title card font size
- `SUBTITLE_FONT_SIZE`: Subtitle font size
- `SUBTITLE_VERTICAL_POSITION`: Subtitle position on screen
- `WORDS_PER_MINUTE`: Narration speed (default: 150)

### Subreddit Selection

Edit `trigger_video_creation.py`:

```python
subreddits = ["TIFU", "AITA", "EntitledParents"]  # Add your subreddits
posts = get_reddit_posts(subreddits, limit=1)      # Adjust limit
```

### Video Splitting

Videos longer than 2 minutes are automatically split into parts. Each part is kept close to 1 minute in length.

## 🔧 Troubleshooting

### Permission Errors on WSL

If you encounter permission errors when installing packages, move your venv to the Linux filesystem:

```bash
deactivate
rm -rf venv
python3 -m venv ~/tiktok_venv
source ~/tiktok_venv/bin/activate
```

### FFmpeg Not Found

Ensure FFmpeg is installed and in your PATH:
```bash
ffmpeg -version
```

### Redis Connection Error

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Whisper Model Download

The first run will download the Whisper model (~150MB). Ensure you have internet connectivity.

## 📝 Notes

- **Voice Selection**: The system uses Gemini AI to detect narrator gender from the story content
- **Abbreviation Expansion**: Common Reddit abbreviations (TIFU, AITA, etc.) are automatically expanded for better narration
- **Duplicate Prevention**: Posts are tracked in `tracking_files/seen_posts.txt` to avoid re-processing
- **Video Quality**: Uses `ultrafast` encoding preset for speed. Adjust in `video_maker.py` for better quality

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Google Gemini for AI script generation
- Microsoft Edge-TTS for free, high-quality text-to-speech
- OpenAI Whisper for transcription
- MoviePy for video editing capabilities
- Reddit community for content inspiration

---

**Happy Video Creating! 🎬**

>>>>>>> bce123b93bd8ca25fdc9330d56f90d6151a33946
