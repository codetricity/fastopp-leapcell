# Contributing to FastOpp PostgreSQL Edition

Thank you for your interest in contributing to FastOpp PostgreSQL Edition! This project is designed for educational purposes and student learning.

## About This Project

This is a modified version of the original [FastOpp](https://github.com/Oppkey/FastOpp) project, specifically optimized for:
- **PostgreSQL** database instead of SQLite
- **Synchronous database operations** for better serverless compatibility
- **LeapCell deployment** with free tier support
- **Educational use** and student tutorials

## How to Contribute

### 1. Fork and Clone
```bash
git clone https://github.com/YOUR_USERNAME/fastopp-postgresql-edition.git
cd fastopp-postgresql-edition
```

### 2. Set Up Development Environment
```bash
# Install dependencies
uv sync

# Set up environment
cp env.example .env
# Edit .env with your database settings

# Initialize database
uv run python oppdemo.py init
```

### 3. Make Changes
- Create a new branch: `git checkout -b feature/your-feature-name`
- Make your changes
- Test thoroughly
- Update documentation if needed

### 4. Submit Pull Request
- Push your branch: `git push origin feature/your-feature-name`
- Create a pull request on GitHub
- Provide clear description of changes

## Development Guidelines

### Code Style
- Follow existing code patterns
- Use type hints where appropriate
- Keep functions focused and small
- Add docstrings for new functions

### Testing
- Test your changes locally
- Ensure database operations work correctly
- Test both sync and async patterns where applicable

### Documentation
- Update README.md for significant changes
- Add comments for complex logic
- Update deployment guides if needed

## Areas for Contribution

### High Priority
- **LeapCell Integration**: Improve deployment experience
- **Database Optimization**: Better connection pooling
- **Error Handling**: More robust error messages
- **Documentation**: Tutorial improvements

### Medium Priority
- **Testing**: Add more comprehensive tests
- **Performance**: Optimize database queries
- **UI/UX**: Improve template designs
- **Examples**: Add more demo scenarios

### Low Priority
- **Features**: New demo pages
- **Integrations**: Additional AI providers
- **Deployment**: Support for other platforms

## Educational Focus

This project is designed for students learning:
- **FastAPI** web development
- **PostgreSQL** database management
- **Serverless deployment** concepts
- **AI integration** patterns
- **Modern web development** practices

## Questions?

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Original FastOpp**: Check the [original repository](https://github.com/Oppkey/FastOpp) for base functionality

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original [FastOpp](https://github.com/Oppkey/FastOpp) project by Oppkey
- [LeapCell](https://leapcell.io/) for free serverless hosting
- FastAPI, SQLAlchemy, and PostgreSQL communities
