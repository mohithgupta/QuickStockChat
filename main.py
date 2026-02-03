import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from langfuse import Langfuse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import SystemMessage, HumanMessage
from config.config import RequestObject
from MarketInsight.components.agent import agent
from MarketInsight.utils.logger import get_logger
from middleware.rate_limiter import limiter
from middleware.security_headers import SecurityHeadersMiddleware
from middleware.auth import get_api_key
from slowapi.errors import RateLimitExceeded

logger = get_logger(__name__)
app = FastAPI()
app.state.limiter = limiter

# Add rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors with a clear message"""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "error": "rate_limit_exceeded"
        },
        headers={"Retry-After": "60"}
    )

# Configure CORS with environment-based whitelist
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)


@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring and keep-alive pings"""
    return {"status": "ok", "message": "Service is running"}


@app.post("/api/chat")
@limiter.limit("100/minute")
async def chat(request: Request, body: RequestObject, api_key: str = Depends(get_api_key)):
    config = {'configurable': {'thread_id': body.threadId}}
    async def generate():
        try:
            # Create a span for the entire request
            with langfuse.start_as_current_observation(
                as_type="span",
                name="chat-request",
                input=body.prompt.content
            ) as span:
                # Set user_id as metadata
                span.update(metadata={"user_id": body.threadId})

                # Create a nested generation for the LLM/agent call
                with langfuse.start_as_current_observation(
                    as_type="generation",
                    name="agent-stream",
                    model="agentic-workflow",
                    input=body.prompt.content
                ) as generation:

                    full_response = ""
                    for token, _ in agent.stream(
                        {
                            'messages': [
                                SystemMessage(content="You are a professional stock market analyst. For every user query, first determine whether a relevant tool can provide accurate or real-time data. If an appropriate tool exists, you must use it before answering. If the user does not provide an exact stock ticker, use the available tool to identify or resolve the correct ticker when required. Only when no suitable tool applies should you respond using your own reasoning and general market knowledge. Never guess, assume, or fabricate any financial data."),
                                HumanMessage(content=body.prompt.content)
                            ]
                        },
                        stream_mode='messages',
                        config=config
                    ):
                        full_response += token.content
                        yield token.content

                    # Update generation with the complete output
                    generation.update(output=full_response)

                # Update span with completion status
                span.update(output="Request completed successfully")

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise
    
    return StreamingResponse(generate(), media_type='text/event-stream',
        headers={
            'cache-control': 'no-cache, no-transform', 
            'connection': 'keep-alive'
        })

if __name__ == '__main__':
    logger.info("App Initiated Successfully")
    uvicorn.run(app, host='0.0.0.0', port=8000)