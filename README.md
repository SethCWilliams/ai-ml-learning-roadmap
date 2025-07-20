# AI/ML Learning Roadmap

10 progressive AI/ML projects designed to teach core concepts from basic prediction models to advanced autonomous systems. Each project builds on previous knowledge while introducing new techniques through hands-on implementation.

## 🎯 Learning Philosophy

**Focus:** Build things I'll actually use and enjoy  
**Style:** Progressive complexity with detailed explanations  
**Approach:** Learn by doing rather than just theory  
**Context:** Projects based on personal interests (soccer, movies, travel, games, etc.)

## 📁 Project Structure

```
ai_roadmap/
├── README.md                      # This overview
├── CLAUDE.md                      # General context for Claude
├── PROJECT_TEMPLATE.md            # Template for new projects
│
├── soccer_match_predictor/        # 🚀 ACTIVE - Phase 1: Data + Prediction
├── movie_night_optimizer/         # Phase 1: Data + Prediction  
├── trail_scout/                   # Phase 2: Interactive Systems
├── wanderlust_planner/            # Phase 2: Interactive Systems
├── game_forge/                    # Phase 3: Creative AI
├── memory_weaver/                 # Phase 3: Creative AI
├── emotion_archaeologist/         # Phase 4: Multi-modal AI
├── synesthesia_bridge/            # Phase 4: Multi-modal AI
├── research_agent/                # Phase 5: Autonomous Systems
└── habit_evolution_engine/        # Phase 5: Autonomous Systems
```

## ⚽ Phase 1: Data Science & Prediction

### [Soccer Match Predictor](./soccer_match_predictor/) 🚀 **Currently Active**
**Goal:** Predict Premier League and MLS match outcomes  
**ML Focus:** Supervised learning, feature engineering, model evaluation  
**Data:** ESPN API + FBref.com scraping  
**Key Learning:** Ensemble methods, time-series data, production ML systems  
**Status:** Project structure complete, starting data collection

**Unique Features:**
- Staged prediction system (morning → injury updates → pre-match)
- Real-world operational scheduling
- Model versioning and confidence tracking
- Detailed ML concept explanations

### Movie Night Optimizer
**Goal:** Personalized movie recommendations based on mood, group preferences  
**ML Focus:** Recommendation systems, collaborative filtering  
**Data:** TMDB API, personal viewing history  
**Key Learning:** Content-based vs collaborative filtering, cold start problems

## 🔄 Phase 2: Interactive Systems

### Trail Scout
**Goal:** AI hiking companion suggesting trails based on conditions, fitness, preferences  
**ML Focus:** Multi-criteria decision making, real-time data integration  
**Data:** Trail APIs, weather data, elevation profiles  
**Key Learning:** Reinforcement learning, contextual recommendations

### Wanderlust Planner
**Goal:** Intelligent travel itinerary generator  
**ML Focus:** Optimization algorithms, constraint satisfaction  
**Data:** Travel APIs, reviews, personal preferences  
**Key Learning:** Multi-objective optimization, user preference modeling

## 🎨 Phase 3: Creative AI

### Game Forge
**Goal:** AI-assisted board game rule generator and balancer  
**ML Focus:** Generative models, game theory  
**Data:** BoardGameGeek data, game mechanics databases  
**Key Learning:** GANs, rule-based systems, game balance algorithms

### Memory Weaver
**Goal:** AI documentary creator from photos/videos with personalized narration  
**ML Focus:** Computer vision, NLP, content generation  
**Data:** Personal media, narrative templates  
**Key Learning:** Multi-modal AI, story generation, media processing

## 🧠 Phase 4: Multi-modal AI

### Emotion Archaeologist
**Goal:** Match music to historical photos based on emotional content  
**ML Focus:** Emotion recognition, cross-modal learning  
**Data:** Photo archives, music libraries, emotion datasets  
**Key Learning:** Facial emotion detection, audio analysis, synesthetic mapping

### Synesthesia Bridge
**Goal:** Create cross-sensory experiences (sound→color, texture→music)  
**ML Focus:** Cross-modal neural networks, sensory mapping  
**Data:** Synesthesia research, sensory datasets  
**Key Learning:** Multi-modal embeddings, perceptual computing

## 🤖 Phase 5: Autonomous Systems

### Research Agent
**Goal:** Autonomous research assistant that can investigate topics and present findings  
**ML Focus:** Agent-based AI, knowledge graphs, reasoning  
**Data:** Academic papers, web sources, structured knowledge  
**Key Learning:** LLM integration, autonomous decision making, knowledge synthesis

### Habit Evolution Engine
**Goal:** Self-improving habit tracking system that adapts recommendations  
**ML Focus:** Reinforcement learning, meta-learning  
**Data:** Personal behavior data, habit research  
**Key Learning:** Online learning, adaptive systems, behavioral modeling

## 🛠 Technical Progression

### Phase 1: Foundation
- **Data Collection:** APIs, web scraping, data cleaning
- **Supervised Learning:** Classification, regression, ensemble methods
- **Tools:** Python, pandas, scikit-learn, matplotlib

### Phase 2: Integration
- **Real-time Systems:** Streaming data, live predictions
- **Optimization:** Multi-objective optimization, constraint solving
- **Tools:** Streamlit, FastAPI, Redis caching

### Phase 3: Generation
- **Generative Models:** GANs, VAEs, transformer-based generation
- **Content Creation:** Text, image, and multimedia generation
- **Tools:** PyTorch, Hugging Face, DALL-E APIs

### Phase 4: Multi-modal
- **Computer Vision:** Object detection, emotion recognition
- **Audio Processing:** Music analysis, speech recognition
- **Tools:** OpenCV, librosa, TensorFlow

### Phase 5: Autonomy
- **Agent Systems:** Planning, reasoning, decision making
- **Meta-learning:** Learning to learn, adaptive algorithms
- **Tools:** LangChain, knowledge graphs, reinforcement learning

## 📚 Learning Resources

### Documentation Approach
Each project contains:
- **CLAUDE.md** - Project-specific context and goals
- **README.md** - Public documentation and setup
- **LEARNING_LOG.md** - Personal learning notes and insights
- **TODO.md** - Current tasks and priorities

### Key Learning Principles
1. **Explain Everything:** Every algorithm choice includes conceptual explanation
2. **Progressive Complexity:** Start simple, add sophistication incrementally
3. **Real-world Focus:** Handle missing data, production constraints, user needs
4. **Domain Integration:** Combine ML with subject matter expertise

## 🚀 Getting Started

### Current Active Project
```bash
cd soccer_match_predictor
make setup
# Edit .env with API keys
make run
```

### Quick Project Overview
```bash
# See all project statuses
find . -name "CLAUDE.md" -exec echo "=== {} ===" \; -exec head -n 5 {} \;

# Check current TODOs across projects
find . -name "TODO.md" -exec echo "=== {} ===" \; -exec head -n 10 {} \;
```

## 📊 Progress Tracking

### Completed Concepts
- [x] Project structure and documentation
- [x] Feature engineering design
- [x] Data source mapping and API research
- [x] Operational system design

### Currently Learning
- [ ] Web scraping best practices
- [ ] API integration patterns
- [ ] Feature engineering for sports data
- [ ] Ensemble method implementation

### Next Concepts
- [ ] Time-series cross-validation
- [ ] Model explanation with SHAP
- [ ] Production ML deployment
- [ ] Real-time prediction systems

## 🔗 External Resources

- **APIs Used:** ESPN, FBref, TMDB, OpenWeather, various travel APIs
- **Key Libraries:** scikit-learn, pandas, streamlit, beautifulsoup4, requests
- **Learning References:** Academic papers, documentation, sports analytics research

---

**Current Focus:** Soccer Match Predictor - Building production-ready ML prediction system with detailed learning explanations.

Each project is designed to be genuinely useful while teaching fundamental AI/ML concepts through hands-on implementation. The progression moves from basic prediction to autonomous systems, with each phase building on previous knowledge.
