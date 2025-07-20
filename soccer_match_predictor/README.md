# Soccer Match Predictor

ML-powered soccer match outcome predictor for Premier League and MLS with detailed learning explanations.

## 🚀 Quick Start (Choose one)

### One-Command Setup
```bash
curl -sSL https://raw.githubusercontent.com/user/repo/main/setup.sh | bash
```

### Manual Setup (Poetry - Recommended)
```bash
git clone <repo-url>
cd soccer_match_predictor
make setup
poetry shell
make run
```

### Manual Setup (Pip)
```bash
git clone <repo-url>
cd soccer_match_predictor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python src/main.py
```

### Web Interface
```bash
make run-web
# Opens Streamlit app at http://localhost:8501
```

## 📖 Learning Context

This is part of my AI/ML learning roadmap focusing on:
- **Data collection** from APIs and web scraping
- **Feature engineering** for sports prediction
- **Supervised learning** with ensemble methods
- **Model evaluation** and explanation techniques

**Leagues:** Premier League and MLS  
**Focus:** Learning ML concepts through detailed explanations, not just prediction accuracy

## 🛠 Development

### Available Commands
```bash
make install          # Install dependencies
make setup            # Full project setup
make run              # Run CLI predictor
make run-web          # Launch Streamlit app
make test             # Run tests
make lint             # Code linting
make format           # Code formatting
make scrape-data      # Collect data from FBref
make train            # Train ML models
```

### Data Sources
- **ESPN API:** Free tier for basic match data
- **FBref.com:** Web scraping for detailed statistics
- **API-Football:** Optional premium tier for real-time data

### Project Structure
```
├── src/              # Main application code
├── data/             # Data storage (raw, processed, external)
├── models/           # Trained model files
├── notebooks/        # Jupyter exploration
├── scripts/          # Utility scripts
└── tests/            # Test suite
```

## 📊 Features

- Match outcome prediction (Win/Draw/Loss)
- Feature importance analysis with SHAP
- Historical performance analysis
- Interactive web interface
- Model explanation and learning documentation

## 🧠 Learning Goals

Each algorithm and technique includes detailed explanations covering:
- Why we chose specific approaches
- How the algorithms work conceptually
- Trade-offs and alternatives considered
- Results interpretation and insights

## 🔑 Setup Requirements

1. Copy `.env.example` to `.env`
2. Add API keys for data sources (see `.env.example`)
3. Install dependencies with Poetry or pip
4. Run data collection scripts to populate initial dataset