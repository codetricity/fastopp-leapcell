# Improve LLM Performance by Selecting a Better LLM

The demo is set to use free models, which have lower performance.
Edit `services/chat_service.py` in this project
and change the LLM model from "meta-llama/llama-3.3-70b-instruct:free"
to another model such as "meta-llama/llama-3.3-70b-instruct" without the free
for better performance and still be about 20x cheaper than premier OpenAI models.
(as of August 15, 2025)
[Browse OpenRouter cheap models](https://openrouter.ai/models?max_price=0.1).
