# X Engagement Tracker

A comprehensive tool for tracking and analyzing X (Twitter) engagement metrics using AI-powered vision parsing and web scraping.

## Features

- 🔍 **Post Analysis**: Extract engagement metrics from any X post
- 🤖 **AI-Powered Parsing**: Uses GPT-4o Vision to accurately read engagement data
- 📊 **Engagement Scoring**: Calculates weighted engagement scores and virality metrics
- 📈 **Trend Analysis**: Track engagement trends over time
- 🚀 **FastAPI Backend**: Modern async API with automatic documentation
- 🎭 **Playwright Scraping**: Reliable browser automation for data extraction

## Architecture

```
x-engagement-tracker/
│
├── app.py               # FastAPI application with API endpoints
├── playwright_scraper.py # Browser automation for X post scraping
├── vision_parser.py     # GPT-4o Vision OCR for metric extraction
├── calculations.py      # Engagement scoring and analysis logic
├── requirements.txt     # Python dependencies
├── env.example         # Environment variables template
└── README.md           # This file
```

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd x-engagement-tracker

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Environment Setup

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your API keys
nano .env
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4o Vision
- `API_HOST`: FastAPI host (default: 0.0.0.0)
- `API_PORT`: FastAPI port (default: 8000)

### 3. Run the Application

```bash
# Start the FastAPI server
python app.py

# Or use uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```http
GET /
GET /health
```

### Analyze Post
```http
POST /analyze-post
Content-Type: application/json

{
  "post_url": "https://x.com/username/status/1234567890",
  "username": "optional_username"
}
```

### User Statistics
```http
GET /user/{username}/stats
```

### Trending Analysis
```http
GET /trending
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Usage Examples

### Python Client Example

```python
import requests
import json

# Analyze a post
response = requests.post(
    "http://localhost:8000/analyze-post",
    json={
        "post_url": "https://x.com/username/status/1234567890",
        "username": "username"
    }
)

data = response.json()
print(f"Engagement Score: {data['engagement_metrics']['engagement_score']}")
print(f"Insights: {data['analysis']['insights']}")
```

### cURL Example

```bash
# Analyze a post
curl -X POST "http://localhost:8000/analyze-post" \
  -H "Content-Type: application/json" \
  -d '{
    "post_url": "https://x.com/username/status/1234567890",
    "username": "username"
  }'
```

## Engagement Metrics

The tool extracts and analyzes the following metrics:

- **Likes**: Number of likes (heart icon)
- **Retweets**: Number of retweets (retweet icon)
- **Replies**: Number of replies (reply icon)
- **Bookmarks**: Number of bookmarks (bookmark icon)
- **Views**: Number of views (if visible)

### Calculated Metrics

- **Engagement Score**: Weighted score (0-100) based on all interactions
- **Virality Score**: Retweets/Views ratio indicating shareability
- **Interaction Rate**: (Likes + Retweets + Replies) / Views
- **Engagement Tier**: Categorical classification (Viral, High, Medium, Low, Very Low)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o Vision | Required |
| `API_HOST` | FastAPI host address | 0.0.0.0 |
| `API_PORT` | FastAPI port | 8000 |
| `DEBUG` | Enable debug mode | True |
| `PLAYWRIGHT_HEADLESS` | Run browser in headless mode | True |
| `PLAYWRIGHT_TIMEOUT` | Browser timeout in milliseconds | 30000 |

### Engagement Thresholds

- `ENGAGEMENT_SCORE_THRESHOLD`: Minimum score for "good" engagement (default: 20.0)
- `VIRALITY_THRESHOLD`: Minimum virality score (default: 5.0)
- `INTERACTION_RATE_THRESHOLD`: Minimum interaction rate (default: 2.0)

## Development

### Project Structure

- `app.py`: FastAPI application with API endpoints
- `playwright_scraper.py`: Browser automation using Playwright
- `vision_parser.py`: GPT-4o Vision integration for OCR
- `calculations.py`: Engagement scoring and analysis algorithms

### Adding New Features

1. **New Metrics**: Add parsing logic in `vision_parser.py`
2. **New Calculations**: Extend `calculations.py` with new algorithms
3. **New Endpoints**: Add routes in `app.py`
4. **New Scraping**: Extend `playwright_scraper.py` for additional data

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.
```

## Troubleshooting

### Common Issues

1. **Playwright Installation**: Ensure browsers are installed with `playwright install chromium`
2. **OpenAI API**: Verify your API key is valid and has sufficient credits
3. **Screenshot Issues**: Check file permissions in the screenshot directory
4. **Rate Limiting**: X may block requests if too frequent

### Debug Mode

Enable debug mode by setting `DEBUG=True` in your `.env` file for detailed logging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation at `/docs`

## Roadmap

- [ ] Database integration for historical data
- [ ] Real-time engagement monitoring
- [ ] Advanced analytics dashboard
- [ ] Multi-platform support (Instagram, LinkedIn)
- [ ] Machine learning predictions
- [ ] Batch processing capabilities

