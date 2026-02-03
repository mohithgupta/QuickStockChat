# Market Insight

An AI-powered stock market analysis platform that provides comprehensive financial data and intelligent insights through a conversational interface.

## Overview

Market Insight leverages advanced AI agents to deliver real-time stock market information, financial analysis, and investment insights. The platform combines the power of LangChain and OpenAI's language models with Yahoo Finance data to create an intelligent assistant for stock market research.

## Technology Stack

**Backend:**
- FastAPI for high-performance API endpoints
- LangChain & LangGraph for AI agent orchestration
- OpenAI GPT models for intelligent responses
- YFinance for financial data retrieval
- Langfuse for observability and tracing

**Frontend:**
- Modern React-based interface
- Real-time streaming responses
- Responsive design for all devices

## Getting Started

### Prerequisites
- Python 3.x
- Node.js (for frontend)
- OpenAI API key

### Installation

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env` file
4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
5. Run the backend server:
   ```bash
   python main.py
   ```
6. Run the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```
7. Access the API at `http://localhost:8000` and frontend at `http://localhost:5173`

## Project Structure

```
MarketInsight/
├── components/     # AI agent configuration
├── utils/          # Tools and utilities
├── config/         # Configuration files
├── frontend/       # React frontend application
└── main.py         # FastAPI server entry point
```

## API Endpoints

### Health Check

**GET** `/health`

Health check endpoint for service monitoring and keep-alive pings.

**Response (200 OK):**
```json
{
  "status": "ok",
  "message": "Service is running"
}
```

### Chat Endpoint

**POST** `/api/chat`

Chat endpoint for processing user queries with agent-based responses. Returns streaming responses using Server-Sent Events (SSE).

**Authentication:**
- Optional API key via `X-API-Key` header or `api_key` query parameter
- Controlled by `REQUIRE_API_KEY` environment variable

**Rate Limiting:**
- 100 requests per minute per IP address
- Returns 429 status when limit exceeded

**Request Headers:**
```
Content-Type: application/json
X-API-Key: <your-api-key> (optional, if auth enabled)
```

**Request Body:**
```json
{
  "prompt": {
    "role": "user",
    "content": "What's the current stock price of AAPL?"
  },
  "threadId": "unique-session-identifier"
}
```

**Request Validation:**
- `prompt.content` is required and cannot be empty
- Maximum content length: 5000 characters
- Content is sanitized for security

**Response (200 OK):**
```
Content-Type: text/event-stream
Cache-Control: no-cache, no-transform
Connection: keep-alive

streaming response chunks...
```

**Error Responses:**

#### 400 Bad Request - Validation Error
```json
{
  "error": "Prompt content is required and cannot be empty",
  "error_type": "ValidationError",
  "field": "prompt.content"
}
```

#### 401 Unauthorized - Missing API Key
```json
{
  "detail": "API key is required. Provide it via X-API-Key header or api_key query parameter."
}
```

#### 403 Forbidden - Invalid API Key
```json
{
  "detail": "Invalid API key"
}
```

#### 429 Too Many Requests - Rate Limit Exceeded
```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "error": "rate_limit_exceeded"
}
```
Headers:
```
Retry-After: 60
```

#### 500 Internal Server Error - Server/Configuration Error
```json
{
  "error": "Error message describing what went wrong",
  "error_type": "ErrorType",
  "details": {}
}
```

## API Capabilities

The platform provides 16 specialized tools for comprehensive stock analysis:
- Stock price tracking
- Historical data analysis
- Financial statements (Balance Sheet, Income Statement, Cash Flow)
- Company information and ratios
- Dividend and split history
- Ownership and holder data
- Insider transactions
- Analyst recommendations
- Company ticker lookup

## Error Response Format

All error responses follow a consistent structure:

```json
{
  "error": "Human-readable error message",
  "error_type": "SpecificErrorType",
  "field": "field_name",  // Present for validation errors
  "details": {}           // Additional context (optional)
}
```

**Common Error Types:**
- `ValidationError` - Input validation failures (400)
- `TickerValidationError` - Invalid ticker symbol (400)
- `APIError` - Internal API operation failures (500)
- `ExternalServiceError` - External API failures (500)
- `ConfigurationError` - Server configuration issues (500)

## HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success - Request processed successfully |
| 400 | Bad Request - Invalid input or validation failure |
| 401 | Unauthorized - API key required but not provided |
| 403 | Forbidden - Invalid or expired API key |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server-side error occurred |
| 503 | Service Unavailable - External service temporarily unavailable |