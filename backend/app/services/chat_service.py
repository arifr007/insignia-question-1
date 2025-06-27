import logging
from app.utils.openrouter import classify_intent, get_llm_response
from app.services.rca_service import perform_dynamic_rca
from app.services.anomaly_service import get_anomaly_analysis
from app.services.eda_service import get_eda_summary
from app.models.mongo import ChatRoom, ChatMessage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_chat_context(messages):
    """Format chat history for LLM context"""
    context = ""
    for msg in messages:
        if msg['type'] == 'user':
            context += f"User: {msg['content']}\n"
        elif msg['type'] == 'bot':
            context += f"Assistant: {msg['content']}\n"
    return context

def generate_room_title(query):
    """Generate a concise title from user's first message"""
    query = query.strip()
    if len(query) <= 50:
        return query
    query_lower = query.lower()
    if any(word in query_lower for word in ['trend', 'tren', 'kenaikan', 'increase', 'bulan', 'month']):
        return "Trend Analysis Query"
    elif any(word in query_lower for word in ['anomaly', 'anomali', 'outlier', 'unusual']):
        return "Anomaly Detection Query"
    elif any(word in query_lower for word in ['rca', 'root cause', 'penyebab', 'cause']):
        return "Root Cause Analysis"
    elif any(word in query_lower for word in ['divisi', 'division', 'directorate', 'direktorat']):
        return "Division Cost Analysis"
    elif any(word in query_lower for word in ['summary', 'ringkasan', 'overview', 'gambaran']):
        return "Data Overview Query"
    elif any(word in query_lower for word in ['compare', 'bandingkan', 'comparison', 'vs']):
        return "Comparative Analysis"
    else:
        return query[:47] + "..."

def process_single_intent(intent, query, context=""):
    """Process a single intent and return response"""
    intent_string = intent.lower() if isinstance(intent, str) else " ".join(intent).lower()
    logger.info(f"=== PROCESSING INTENT ===")
    logger.info(f"Original query: '{query}'")
    logger.info(f"Classified intent: '{intent}'")
    logger.info(f"Intent string: '{intent_string}'")
    try:
        if "anomaly_detection" in intent_string or "outlier_detection" in intent_string:
            anomaly_result = get_anomaly_analysis(method="comprehensive")
            anomaly_data = {
                "statistical_anomalies": anomaly_result.get('summary', {}).get('total_statistical_anomalies', 0),
                "ml_anomalies": anomaly_result.get('summary', {}).get('total_ml_anomalies', 0),
                "trend_anomalies": anomaly_result.get('summary', {}).get('total_trend_anomalies', 0),
                "recommendations": anomaly_result.get('summary', {}).get('recommendations', [])
            }
            anomaly_prompt = f"""Previous conversation context:
            {context}

            Current query: {query}

            Anomaly detection results: {anomaly_data}

            Provide anomaly detection analysis based on this data. Consider the conversation context when providing your response."""
            response = get_llm_response(query, anomaly_prompt)
        elif "trend_analysis" in intent_string:
            eda_data = get_eda_summary()
            temporal_data = eda_data.get('temporal_analysis', {})
            trend_data = temporal_data.get('recent_months', {})
            trend_prompt = f"""You are a financial analyst. The user asked: "{query}"
            Previous conversation context:
            {context}

            Monthly expense data: {trend_data}
            Full temporal analysis: {temporal_data}
            Complete EDA data: {eda_data}

            Analyze the expense trend data and provide insights about monthly changes, focusing on any increases."""
            response = get_llm_response(query, trend_prompt)
        elif "rca_request" in intent_string:
            rca_result = perform_dynamic_rca()
            rca_prompt = f"""Previous conversation context:
            {context}

            Current query: {query}

            Dynamic RCA results: {rca_result}

            Provide comprehensive root cause analysis based on this data. Consider the conversation context when providing your response."""
            response = get_llm_response(query, rca_prompt)
        elif "aggregation_query" in intent_string:
            eda_data = get_eda_summary()
            organizational_breakdown = eda_data.get('organizational_breakdown', {})
            summary_data = eda_data.get('summary', {})

            agg_prompt = f"""Previous conversation context:
            {context}

            Current query: {query}

            Expense summary data: {summary_data}
            Full organizational breakdown: {organizational_breakdown}

            Provide a summary of expense data based on this information. Consider the conversation context when providing your response."""
            response = get_llm_response(query, agg_prompt)
        elif "eda_request" in intent_string:
            eda_data = get_eda_summary()
            eda_prompt = f"""Previous conversation context:
            {context}

            Current query: {query}

            Exploratory data analysis results: {eda_data}

            Provide general data exploration and insights based on this financial data. Consider the conversation context when providing your response."""
            response = get_llm_response(query, eda_prompt)
        elif "comparative_analysis" in intent_string:
            eda_data = get_eda_summary()
            temporal_data = eda_data.get('temporal_analysis', {})
            trend_data = temporal_data.get('recent_months', {})
            compare_prompt = f"""Previous conversation context:
            {context}

            Current query: {query}

            Comparative analysis data: {eda_data}
            Temporal analysis: {temporal_data}
            Trend data: {trend_data}

            Provide comparative analysis insights based on this financial data. Consider the conversation context when providing your response."""
            response = get_llm_response(query, compare_prompt)
        elif "general_chat" in intent_string:
            general_prompt = f"""Previous conversation context:
            {context}

            Current query: {query}

            You are a financial data analyst. Respond to this query considering the conversation history."""
            response = get_llm_response(query, general_prompt)
        else:
            context_prompt = f"""Previous conversation context:
            {context}

            Current query: {query}

            You are a financial data analyst. Answer this query about expense data considering the conversation history."""
            response = get_llm_response(query, context_prompt)
    except Exception as e:
        logger.error(f"Error processing intent: {str(e)}")
        response = f"Error processing intent: {str(e)}"
    return response

def handle_chat_message(room_id, username, query):
    """Handle chat message processing"""
    room = ChatRoom.get_room(room_id, username)
    if not room:
        return None, {"error": "Room not found", "status": 404}

    is_first_message = room.get('message_count', 0) == 0
    ChatMessage.add_message(room_id, 'user', query)

    if is_first_message:
        title = generate_room_title(query)
        ChatRoom.update_room_title(room_id, username, title)
        logger.info(f"Updated room title to: '{title}'")

    recent_messages = ChatMessage.get_recent_context(room_id, limit=10)
    context = format_chat_context(recent_messages)
    language_instruction = f"\nIMPORTANT: Always respond in the same language as the user's query. User query: '{query}'\n"
    context = language_instruction + context

    intents = classify_intent(query)
    logger.info(f"=== CHAT PROCESSING ===")
    logger.info(f"User query: '{query}'")
    logger.info(f"Classified intents: {intents}")
    logger.info(f"Context preview: {context[:200]}...")

    if not isinstance(intents, list):
        intents = [intents] if intents else ['general_chat']

    responses = []
    for intent in intents:
        if intent and intent.strip():
            logger.info(f"Processing intent: '{intent}'")
            try:
                response = process_single_intent(intent, query, context)
                logger.info(f"Response received for '{intent}': {response[:150]}...")
                responses.append(response)
            except Exception as e:
                logger.error(f"Error processing intent '{intent}': {str(e)}")
                responses.append(f"Error processing intent '{intent}': {str(e)}")

    if not responses:
        responses.append("I'm here to help with your financial data questions. Could you please clarify what you'd like to know?")

    combined_response = "\n".join(responses)
    ChatMessage.add_message(room_id, 'bot', combined_response, 
                          intent=", ".join(intents), query=query)

    return combined_response, {"intents": intents, "individual_responses": responses, "status": 200}
