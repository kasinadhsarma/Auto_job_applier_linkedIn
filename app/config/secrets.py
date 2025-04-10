'''
Configuration file for API keys and platform credentials.
DO NOT commit this file to version control.
'''

# AI Configuration
use_AI = True  # Set to True to enable AI-powered features
ai_provider = "ollama"  # Options: "openai", "ollama"

# OpenAI Configuration (only needed if ai_provider = "openai")
openai_api_key = ""  # Your OpenAI API key if using OpenAI

# Ollama Configuration (only needed if ai_provider = "ollama")
ollama_host = "http://localhost:11434"  # Ollama API endpoint
ollama_model = "gemma3"  # The model to use (based on 'ollama list' output)
ollama_timeout = 30  # Timeout in seconds for Ollama API calls

# Platform Credentials
# LinkedIn Credentials
username = "kasinadhsarma@gmail.com"
password = "Pavan@123"

# Indeed Credentials
indeed_username = "your-indeed-email"
indeed_password = "your-indeed-password"

# Glassdoor Credentials
glassdoor_username = "your-glassdoor-email"
glassdoor_password = "your-glassdoor-password"

# Dice Credentials
dice_username = "your-dice-email"
dice_password = "your-dice-password"

# AI LLM Settings
llm_spec = ai_provider  # Will use the value from ai_provider
llm_api_url = ollama_host if ai_provider == "ollama" else "https://api.openai.com/v1"
llm_api_key = openai_api_key if ai_provider == "openai" else ""  # OpenAI requires key, Ollama doesn't
llm_model = ollama_model if ai_provider == "ollama" else "gpt-4-turbo"

# AI Configuration for Application Optimization
stream_output = True  # Whether to stream AI responses
temperature = 0.7  # AI response creativity (0-1)

# Optional: Proxy Configuration
use_proxy = False
proxy_url = ""  # Example: "http://proxy.example.com:8080"

# Optional: Custom Headers for API Calls
custom_headers = {
    # Add any custom headers needed for your API setup
}

# Optional: Rate Limiting Settings
max_requests_per_minute = 50  # Adjust based on your API tier
max_parallel_requests = 5  # Maximum concurrent API requests