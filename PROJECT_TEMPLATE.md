# Project Setup Template

## Hybrid Approach for AI Learning Projects

Use this template when setting up each new project in the ai_roadmap. The goal is clean development environment + easy user onboarding for eventual public deployment.

## Directory Structure Template
```
project_name/
├── CLAUDE.md                 # Project-specific context for Claude
├── README.md                 # Public-facing description and setup
├── pyproject.toml            # Poetry configuration
├── requirements.txt          # Fallback for pip users
├── Dockerfile               # Container for deployment
├── docker-compose.yml       # Local development with services
├── setup.sh                 # One-command setup script
├── Makefile                 # Developer commands
├── .env.example             # Environment variables template
├── .gitignore               # Standard Python gitignore
├── LEARNING_LOG.md          # Personal learning notes
├── TODO.md                  # Current tasks and ideas
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── data/
│   ├── models/
│   └── utils/
├── tests/
├── notebooks/               # Jupyter exploration
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── models/                  # Saved model files
├── scripts/                 # Utility scripts
└── streamlit_app.py         # Web interface for demos
```

## Development Environment Setup

### 1. Poetry (Primary)
```toml
# pyproject.toml
[tool.poetry]
name = "project-name"
version = "0.1.0"
description = "Brief project description"

[tool.poetry.dependencies]
python = "^3.9"
# Add project-specific dependencies

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
jupyter = "^1.0.0"
black = "^23.0.0"
```

Commands:
- `poetry install` - Install dependencies
- `poetry shell` - Activate virtual environment
- `poetry run python src/main.py` - Run application

### 2. Requirements.txt (Fallback)
Generate from Poetry: `poetry export -f requirements.txt --output requirements.txt`

### 3. Setup Script (setup.sh)
```bash
#!/bin/bash
echo "Setting up [PROJECT_NAME]..."

# Check if Poetry is installed
if command -v poetry &> /dev/null; then
    echo "Using Poetry for setup..."
    poetry install
    echo "Setup complete! Run: poetry run python src/main.py"
else
    echo "Using pip for setup..."
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    echo "Setup complete! Activate venv and run: python src/main.py"
fi
```

### 4. Makefile
```makefile
.PHONY: install setup run test clean

install:
	poetry install

install-pip:
	pip install -r requirements.txt

setup: install
	python scripts/setup_data.py

run:
	poetry run python src/main.py

run-web:
	poetry run streamlit run streamlit_app.py

test:
	poetry run pytest tests/

clean:
	find . -type d -name "__pycache__" -delete
	find . -name "*.pyc" -delete

docker-build:
	docker build -t project-name .

docker-run:
	docker-compose up
```

## User Onboarding Options

### Option 1: Web Demo (Easiest)
- Streamlit app deployed to Streamlit Cloud
- Users just visit URL, no setup required
- Include link in README

### Option 2: One-Command Setup
```bash
curl -sSL https://raw.githubusercontent.com/user/repo/main/setup.sh | bash
```

### Option 3: Manual Setup
Clear instructions in README for different experience levels:
- Poetry users
- Pip users  
- Docker users

### Option 4: Docker (Production)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY . .
EXPOSE 8501

CMD ["poetry", "run", "streamlit", "run", "streamlit_app.py"]
```

## README Template Structure

```markdown
# Project Name

Brief description and demo GIF/screenshot

## 🚀 Quick Start (Choose one)

### Try Online
[Live Demo](https://your-app.streamlit.app) - No setup required!

### One-Command Setup
```bash
curl -sSL https://raw.githubusercontent.com/user/repo/main/setup.sh | bash
```

### Manual Setup
[Detailed instructions for different environments]

## 📖 Learning Context
This is part of my AI/ML learning roadmap. [Link to specific learning goals]

## 🛠 Development
[Instructions for contributing, running tests, etc.]
```

## Environment Variables Template (.env.example)
```bash
# API Keys (get from respective services)
WEATHER_API_KEY=your_key_here
SPORTS_API_KEY=your_key_here

# Database (if needed)
DATABASE_URL=sqlite:///data/app.db

# Model Settings
MODEL_PATH=models/trained_model.pkl
DEBUG=False
```

## Key Principles
1. **Poetry for development** - Clean dependency management
2. **Multiple setup options** - Accommodate different user preferences  
3. **Web demos** - Lowest barrier to entry
4. **Docker for deployment** - Consistent production environment
5. **Clear documentation** - Multiple difficulty levels
6. **Learning focus** - Document the educational goals

## Project-Specific Structure Variations

### Standard Structure (Use for):
- soccer_match_predictor
- movie_night_optimizer  
- trail_scout
- wanderlust_planner
- game_forge
- research_agent
- habit_evolution_engine

### Media-Heavy Projects

#### memory_weaver (Documentary + Travel Journal Creator)
Add these directories to the standard structure:
```
├── media/
│   ├── input/              # User uploaded photos/videos
│   ├── processed/          # Resized, formatted media
│   ├── output/             # Generated documentaries/journals
│   └── temp/               # Temporary processing files
├── templates/
│   ├── narration/          # Documentary narration templates
│   ├── journal/            # Travel journal templates
│   └── styles/             # Different content styles
├── assets/
│   ├── audio/              # Background music, sound effects
│   ├── fonts/              # Typography for generated content
│   └── graphics/           # Logos, overlays, graphics
└── cache/                  # Processed feature caches
```

#### emotion_archaeologist (Music + Photo Emotion Matching)
Add these directories to the standard structure:
```
├── media/
│   ├── photos/             # Historical photos for analysis
│   ├── music/              # Music library/samples for matching
│   ├── analysis/           # Emotion analysis results
│   └── playlists/          # Generated emotional playlists
├── datasets/
│   ├── emotion_research/   # Psychology/emotion datasets
│   ├── music_features/     # Pre-computed music features
│   └── facial_models/      # Emotion detection model data
├── cache/
│   ├── face_embeddings/    # Cached facial analysis
│   └── music_embeddings/   # Cached music analysis
```

#### synesthesia_bridge (Cross-Sensory Experiences)
Add these directories to the standard structure:
```
├── sensory_data/
│   ├── audio/              # Sound files for conversion
│   ├── visual/             # Images, videos, visual patterns
│   ├── mappings/           # Cross-sensory mapping data
│   └── experiments/        # User testing results
├── research/
│   ├── synesthesia_studies/ # Academic research data
│   ├── color_sound_maps/   # Research-based mappings
│   └── neural_networks/    # Pre-trained sensory models
├── generated/
│   ├── visualizations/     # Generated visual from audio
│   ├── sonifications/      # Generated audio from visual
│   └── experiences/        # Complete sensory experiences
├── calibration/            # User-specific sensory preferences
```

### Additional Considerations

#### For Interactive Projects (trail_scout, wanderlust_planner)
Consider adding:
```
├── cache/
│   ├── api_responses/      # Cached API data
│   └── user_sessions/      # Session state management
├── config/
│   ├── api_configs/        # API endpoint configurations
│   └── user_profiles/      # User preference profiles
```

#### For Agent Projects (research_agent, habit_evolution_engine)
Consider adding:
```
├── agents/
│   ├── knowledge_base/     # Agent's accumulated knowledge
│   ├── decision_logs/      # Agent decision history
│   └── learning_data/      # Meta-learning datasets
├── workflows/              # Agent workflow definitions
└── state/                  # Persistent agent state
```

## Project-Specific CLAUDE.md Template

Each project should have a focused CLAUDE.md file with this structure:

```markdown
# [Project Name] - Claude Assistant Context

## Project Goal
[1-2 sentences: What does this project do and why?]

## Learning Objectives
- [Specific ML/AI concept 1]
- [Specific ML/AI concept 2] 
- [Specific technical skill]

## Technical Approach
**Primary Method:** [Main algorithm/technique being used]
**Data Sources:** [Where data comes from]
**Key Libraries:** [Main dependencies]
**Deployment:** [How users will interact with it]

## Success Criteria
- **Functional:** [What needs to work]
- **Learning:** [What I need to understand]
- **Usable:** [How I'll know it's user-ready]

## Current Status
[Quick note on where you are: "Just started", "Data collection phase", "Model training", "Ready for deployment", etc.]

## Key Decisions & Notes
- [Important architectural choices]
- [Data/model decisions made]
- [Lessons learned so far]

## Connection to Roadmap
**Builds on:** [Previous projects that this uses concepts from]
**Leads to:** [How this prepares for future projects]
```

### Example: soccer_match_predictor/CLAUDE.md
```markdown
# Soccer Match Predictor - Claude Assistant Context

## Project Goal
Predict soccer match outcomes using team statistics, player data, weather, and historical matchups to learn fundamental ML prediction concepts.

## Learning Objectives
- Data collection and web scraping
- Feature engineering for sports data
- Supervised learning (classification/regression)
- Model evaluation and validation
- Handling time-series sports data

## Technical Approach
**Primary Method:** Ensemble of Random Forest + XGBoost for match outcome prediction
**Data Sources:** Sports APIs (ESPN, Football-Data), weather APIs, web scraping
**Key Libraries:** scikit-learn, pandas, requests, beautifulsoup
**Deployment:** Streamlit web app for match predictions

## Success Criteria
- **Functional:** Predict match outcomes with >60% accuracy
- **Learning:** Understand feature importance in sports prediction
- **Usable:** Simple web interface where users can get predictions

## Current Status
Just started - researching data sources

## Key Decisions & Notes
- Focus on Premier League initially (good data availability)
- Include weather as feature (affects gameplay)
- Start simple with basic team stats, add complexity later

## Connection to Roadmap
**Builds on:** None (first project)
**Leads to:** movie_night_optimizer (recommendation systems), trail_scout (real-time data)
```

## Notes for Claude
- Keep CLAUDE.md files under 200 words
- Focus on what's unique about THIS project
- Update the "Current Status" section as you progress
- Use the template but adapt based on project complexity
- For media projects, note file size/storage considerations
- For agent projects, emphasize decision-making and state management