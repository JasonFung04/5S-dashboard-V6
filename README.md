# 5S Score Dashboard

A Dash-based 5S workplace organization performance monitoring dashboard with GitHub cloud storage support.

## Features

- 📊 Real-time 5S score monitoring dashboard
- 📈 Weekly trend line charts
- 🎯 Site performance gauges
- 📱 Responsive design (mobile and PC support)
- ☁️ GitHub cloud storage data persistence
- 📤 Excel file upload and download
- 🔄 Historical data viewing and management

## Local Development Setup

### 1. Clone Project
```bash
git clone <your-repo-url>
cd 5s-dashboard
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
```bash
# Linux/Mac
export GITHUB_TOKEN="your_personal_access_token"
export GITHUB_REPO_OWNER="your_github_username"
export GITHUB_REPO_NAME="5s-dashboard-data"

# Windows
set GITHUB_TOKEN=your_personal_access_token
set GITHUB_REPO_OWNER=your_github_username
set GITHUB_REPO_NAME=5s-dashboard-data
```

### 4. Run Application
```bash
python main.py
```

Access: http://localhost:8050

## GitHub Storage Setup

### 1. Create Data Repository
- Repository name: `5s-dashboard-data`
- Set as **private repository**
- Create `data/` folder

### 2. Generate Personal Access Token
- GitHub Settings → Developer settings → Personal access tokens
- Permissions: `repo` (Full control)

### 3. Test Setup
```bash
python test_github_setup.py
```

## Render Deployment

### 1. Connect GitHub Repository to Render

### 2. Configure Environment Variables
```
GITHUB_TOKEN = your_personal_access_token
GITHUB_REPO_OWNER = your_github_username
GITHUB_REPO_NAME = 5s-dashboard-data
```

### 3. Deployment Settings
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`

## Data Format

Excel file must contain the following columns:
- Site
- Monthly Performance
- Max/Month
- Completed
- Missing
- Week 1
- Week 2
- Week 3
- Week 4

## Site Categories

**Hong Kong Sites**: ELC, GGW, HSK, LFS, MAP, MTL, STLC + HK_avg  
**South China Sites**: GuangZhou, Yantian (ZhongTong), Chengdu, Pinghu + SC_avg

## Usage

1. **Upload Data**: Click settings icon (⚙️) → Select month → Upload Excel file
2. **Select Sites**: Choose which sites to display in charts and tables
3. **View Performance**: Monitor weekly trends and monthly rankings
4. **Download Template**: Get properly formatted Excel template

## Tech Stack

- **Frontend**: Dash + Plotly
- **Backend**: Python + Pandas
- **Storage**: GitHub API
- **Deployment**: Render.com

## License

MIT License
