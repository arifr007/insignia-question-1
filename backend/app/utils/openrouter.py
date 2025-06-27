import requests
from app.config import Config
import json
import logging

def classify_intent(query):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                # "model": "qwen/qwen3-32b-04-28",
                # "model": "qwen/qwen3-235b-a22b",
                # "model": "google/gemini-2.0-flash-001",
                "messages": [
                    {"role": "system", "content": "Classify the query into one or more of these intents: general_chat, trend_analysis, rca_request, aggregation_query, eda_request, comparative_analysis, anomaly_detection, outlier_detection. Return ONLY a JSON array format like [\"intent1\", \"intent2\"] or [\"intent1\"]. No explanations, no other text."},
                    {"role": "user", "content": query}
                ]
            }
        )
        
        if response.status_code != 200:
            print(f"OpenRouter API error: {response.status_code} - {response.text}")
            return ["eda_request"]  # Default fallback as array
            
        response_data = response.json()
        if 'choices' not in response_data or len(response_data['choices']) == 0:
            print(f"Unexpected response format: {response_data}")
            return ["eda_request"]  # Default fallback as array
            
        content = response_data['choices'][0]['message']['content'].strip()
        # Try to parse as JSON array
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return parsed
            else:
                return [parsed]
        except:
            # If parsing fails, return as single item array
            return [content.lower()]
    except Exception as e:
        print(f"Error in classify_intent: {str(e)}")
        return ["eda_request"]  # Default fallback as array

def get_llm_response(userPrompt, asistantPrompt=None):
    try:
        system_message = "You are a financial analysis assistant. Answer in the same language as the user's query. If the user asks in Indonesian, respond in Indonesian. If in English, respond in English. Be clear and professional."
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": userPrompt},
        ]
        if asistantPrompt is not None:
            messages.append({"role": "assistant", "content": asistantPrompt})

        request_body = {
            "model": "openai/gpt-4o-mini",
            # "model": "qwen/qwen3-32b-04-28",
            # "model": "qwen/qwen3-235b-a22b",
            # "model": "google/gemini-2.0-flash-001",
            "messages": messages
        }

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info(f"OpenRouter request body: {request_body}")

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
            "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
            },
            json=request_body
        )

        if response.status_code != 200:
            print(f"OpenRouter API error: {response.status_code} - {response.text}")
            return "Unable to generate response due to API error."
            
        response_data = response.json()
        if 'choices' not in response_data or len(response_data['choices']) == 0:
            print(f"Unexpected response format: {response_data}")
            return "Unable to generate response due to unexpected API response format."
            
        return response_data['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in get_llm_response: {str(e)}")
        return f"Unable to generate response: {str(e)}"