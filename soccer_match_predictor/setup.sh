#!/bin/bash
echo "Setting up Soccer Match Predictor..."

# Check if Poetry is installed
if command -v poetry &> /dev/null; then
    echo "Using Poetry for setup..."
    poetry install
    cp .env.example .env
    echo ""
    echo "✅ Setup complete!"
    echo "📝 Edit the .env file with your API keys"
    echo "🚀 Run: poetry shell && make run"
else
    echo "Using pip for setup..."
    
    # Check if we're in a virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo "Creating virtual environment..."
        python -m venv venv
        echo "Activate virtual environment with:"
        echo "  source venv/bin/activate  (Linux/Mac)"
        echo "  venv\\Scripts\\activate    (Windows)"
        echo ""
        echo "Then run this script again."
        exit 1
    fi
    
    pip install -r requirements.txt
    cp .env.example .env
    echo ""
    echo "✅ Setup complete!"
    echo "📝 Edit the .env file with your API keys"
    echo "🚀 Run: python src/main.py"
fi

echo ""
echo "📚 Learning focus: This project emphasizes understanding ML concepts"
echo "🏈 Data sources: Premier League & MLS from ESPN API + FBref scraping"
echo "🔍 Next steps: Check LEARNING_LOG.md and TODO.md for guidance"