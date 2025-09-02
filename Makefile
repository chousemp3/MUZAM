# MUZAM Makefile
# ===============

.PHONY: help install test clean dev-install lint format docs serve build

# Default target
help:
	@echo "🎵 MUZAM - Open Source Audio Recognition"
	@echo "========================================"
	@echo ""
	@echo "Available commands:"
	@echo "  install      Install MUZAM in production mode"
	@echo "  dev-install  Install MUZAM in development mode"
	@echo "  test         Run the test suite"
	@echo "  test-quick   Run quick functionality test"
	@echo "  lint         Run code linting (flake8)"
	@echo "  format       Format code with black"
	@echo "  clean        Clean build artifacts"
	@echo "  docs         Generate documentation"
	@echo "  serve        Start the web server"
	@echo "  build        Build distribution packages"
	@echo "  init-db      Initialize the database"
	@echo ""

# Installation
install:
	@echo "📦 Installing MUZAM..."
	pip install -e .

dev-install:
	@echo "🔧 Installing MUZAM in development mode..."
	pip install -e ".[dev,all]"

# Testing
test:
	@echo "🧪 Running full test suite..."
	pytest tests/ -v

test-quick:
	@echo "⚡ Running quick functionality test..."
	python test_muzam.py

# Code quality
lint:
	@echo "🔍 Running code linting..."
	flake8 muzam/ --max-line-length=100

format:
	@echo "✨ Formatting code..."
	black muzam/ --line-length=100
	isort muzam/

# Database
init-db:
	@echo "🗄️ Initializing database..."
	python -m muzam.database.init

# Development
serve:
	@echo "🚀 Starting MUZAM web server..."
	muzam serve --reload

serve-prod:
	@echo "🚀 Starting MUZAM production server..."
	muzam serve --host 0.0.0.0 --port 8000

# Build and distribution
build:
	@echo "📦 Building distribution packages..."
	python setup.py sdist bdist_wheel

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Documentation
docs:
	@echo "📚 Generating documentation..."
	@if command -v mkdocs >/dev/null 2>&1; then \
		mkdocs build; \
	else \
		echo "⚠️  mkdocs not installed. Install with: pip install mkdocs mkdocs-material"; \
	fi

docs-serve:
	@echo "📚 Serving documentation locally..."
	@if command -v mkdocs >/dev/null 2>&1; then \
		mkdocs serve; \
	else \
		echo "⚠️  mkdocs not installed. Install with: pip install mkdocs mkdocs-material"; \
	fi

# CLI shortcuts
recognize:
	@echo "🎤 Starting audio recognition..."
	muzam recognize $(FILE)

listen:
	@echo "🎧 Listening for audio..."
	muzam listen --duration $(DURATION)

search:
	@echo "🔍 Searching database..."
	muzam db search "$(QUERY)"

stats:
	@echo "📊 Database statistics..."
	muzam db stats

# Development helpers
setup-dev:
	@echo "🔧 Setting up development environment..."
	python -m venv .venv
	@echo "Activate with: source .venv/bin/activate"
	@echo "Then run: make dev-install"

check-deps:
	@echo "🔍 Checking dependencies..."
	pip check

update-deps:
	@echo "📈 Updating dependencies..."
	pip list --outdated

# Docker commands (if Dockerfile exists)
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t muzam:latest .

docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p 8000:8000 muzam:latest

# Performance testing
benchmark:
	@echo "⚡ Running performance benchmarks..."
	@if [ -f benchmarks/run_benchmarks.py ]; then \
		python benchmarks/run_benchmarks.py; \
	else \
		echo "No benchmark script found"; \
	fi

# Release helpers
check-release:
	@echo "🔍 Checking release readiness..."
	@echo "Checking version consistency..."
	@python -c "import muzam; print(f'Version: {muzam.__version__}')"
	@echo "Running tests..."
	@make test-quick
	@echo "Checking code style..."
	@make lint

release-patch:
	@echo "🚀 Creating patch release..."
	bump2version patch

release-minor:
	@echo "🚀 Creating minor release..."
	bump2version minor

release-major:
	@echo "🚀 Creating major release..."
	bump2version major

# Utility commands
list-devices:
	@echo "🎤 Listing audio devices..."
	muzam devices

example-usage:
	@echo "📖 Example usage commands:"
	@echo ""
	@echo "Basic recognition:"
	@echo "  muzam recognize song.mp3"
	@echo ""
	@echo "Microphone recognition:"
	@echo "  muzam listen --duration 10"
	@echo ""
	@echo "Add song to database:"
	@echo "  muzam db add song.mp3 --title 'Song Title' --artist 'Artist Name'"
	@echo ""
	@echo "Batch processing:"
	@echo "  muzam batch *.mp3 --recursive"
	@echo ""
	@echo "Start web server:"
	@echo "  muzam serve"
	@echo ""

# All-in-one setup
setup-all: clean setup-dev dev-install init-db test-quick
	@echo "🎉 MUZAM is ready to use!"
	@echo "Activate the environment with: source .venv/bin/activate"
