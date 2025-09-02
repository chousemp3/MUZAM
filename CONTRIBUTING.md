# Contributing to MUZAM

Thank you for your interest in contributing to MUZAM! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

### Ways to Contribute
- **Code**: Core algorithms, new features, bug fixes, optimizations
- **Documentation**: README updates, code comments, tutorials
- **Testing**: Unit tests, integration tests, performance testing
- **Audio Samples**: High-quality audio samples for testing
- **Translations**: Interface translations for internationalization
- **Bug Reports**: Detailed bug reports with reproduction steps
- **Feature Requests**: New feature ideas and enhancements

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 🏗️ Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Audio hardware (microphone/speakers) for testing
- Virtual environment tool (venv, conda, or similar)

### Local Development
```bash
# Clone the repository
git clone https://github.com/muzam-project/muzam.git
cd muzam

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev,all]"

# Initialize database
python -m muzam.database.init

# Run tests
pytest

# Start development server
muzam serve --reload
```

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and return values
- Write descriptive docstrings for all public functions and classes
- Use meaningful variable and function names

### Code Formatting
```bash
# Format code with black
black muzam/

# Check with flake8
flake8 muzam/

# Sort imports
isort muzam/
```

## 🧪 Testing Guidelines

### Test Structure
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Performance tests: `tests/performance/`
- Audio samples: `tests/audio_samples/`

### Writing Tests
```python
import pytest
from muzam.core.recognizer import AudioRecognizer

def test_audio_recognition():
    recognizer = AudioRecognizer()
    result = recognizer.identify_file("tests/audio_samples/test_song.mp3")
    
    assert result is not None
    assert result.confidence > 0.7
    assert "Test Song" in result.title
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=muzam

# Run performance tests
pytest tests/performance/ -v
```

## 📚 Documentation

### Code Documentation
- All public functions must have docstrings
- Use Google-style docstrings
- Include parameter types and descriptions
- Provide usage examples for complex functions

### Example Docstring
```python
def recognize_audio(self, audio_data: np.ndarray, sample_rate: int) -> Optional[RecognitionResult]:
    """
    Recognize a song from audio data.
    
    Args:
        audio_data: Raw audio signal as numpy array
        sample_rate: Sample rate of the audio in Hz
        
    Returns:
        RecognitionResult if match found, None otherwise
        
    Example:
        >>> recognizer = AudioRecognizer()
        >>> audio_data, sr = load_audio("song.mp3")
        >>> result = recognizer.recognize_audio(audio_data, sr)
        >>> print(f"Found: {result.title} by {result.artist}")
    """
```

## 🎵 Audio Algorithm Guidelines

### Fingerprinting Algorithms
- Prioritize accuracy over speed (but maintain real-time capability)
- Ensure noise robustness
- Document algorithm parameters and trade-offs
- Provide performance benchmarks

### Database Operations
- Optimize for fast lookups
- Minimize memory usage
- Support concurrent access
- Include proper error handling

### Machine Learning
- Use established libraries (scikit-learn, TensorFlow)
- Provide pre-trained models when possible
- Document training procedures
- Include model evaluation metrics

## 🐛 Bug Reports

### Bug Report Template
```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.9.5]
- MUZAM version: [e.g., 1.0.0]
- Audio hardware: [e.g., Built-in microphone]

**Audio File**
If applicable, attach a sample audio file that demonstrates the issue.

**Logs**
Include relevant log output or error messages.
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Implementation**
Ideas for how this could be implemented.

**Alternatives Considered**
Other approaches you've considered.

**Additional Context**
Screenshots, examples, or other relevant information.
```

## 🎯 Performance Guidelines

### Performance Targets
- Recognition time: < 2 seconds for 10-second audio clips
- Memory usage: < 500MB for typical operations
- Database lookup: < 100ms for fingerprint search
- Batch processing: > 100 files per minute

### Profiling
```bash
# Profile recognition performance
python -m cProfile -o profile.stats muzam/test_performance.py

# Analyze with snakeviz
snakeviz profile.stats

# Memory profiling
python -m memory_profiler muzam/test_memory.py
```

## 🔒 Security Guidelines

### Security Considerations
- Validate all user inputs
- Sanitize file uploads
- Implement rate limiting for API endpoints
- Use secure authentication methods
- Protect against injection attacks

### Privacy Guidelines
- Minimize data collection
- Provide local-only processing options
- Clear privacy documentation
- Respect user consent preferences

## 📋 Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New code has appropriate tests
- [ ] Documentation is updated
- [ ] Performance impact is considered
- [ ] Security implications are reviewed
- [ ] Breaking changes are documented

## 🌟 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Annual contributor spotlight posts

## 📞 Community

### Communication Channels
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: General questions and community chat
- Discord: Real-time community chat (link in README)
- Email: security@muzam.org for security issues

### Code of Conduct
Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inclusive environment for all contributors.

## 🚀 Release Process

### Version Numbers
- Major versions (1.0.0): Breaking changes
- Minor versions (1.1.0): New features, backward compatible
- Patch versions (1.1.1): Bug fixes

### Release Checklist
1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Update documentation
5. Create release tag
6. Build and publish packages
7. Announce release

## 💝 Thank You

Your contributions make MUZAM better for everyone. Whether you're fixing a typo, adding a feature, or reporting a bug, every contribution is valued and appreciated!

---

**Happy Contributing! 🎵**
