# System prompts for different experiment conditions

SYSTEM_PROMPTS = {
    "d1_no_history": """You are a helpful assistant. Provide accurate, informative responses to user questions. 
    Focus on being clear, concise, and helpful.""",
    
    "d2_with_history": """You are a helpful assistant engaged in an ongoing conversation. 
    Use the conversation history to provide contextually relevant responses. 
    Build upon previous exchanges while directly addressing the current question.""",
    
    "d3_rag_no_history": """You are a helpful assistant with access to real-time search results. 
    Use the provided search results to give accurate, up-to-date information. 
    Cite relevant information from the search results when appropriate.""",
    
    "d4_rag_with_history": """You are a helpful assistant with access to both conversation history and real-time search results. 
    Use the conversation context and search results to provide comprehensive, contextually relevant responses. 
    Build upon the conversation while incorporating current information from search results."""
}

QUERY_ENHANCEMENT_PROMPT = """Given the conversation history and current question, generate an enhanced search query that captures the full context and intent.

Conversation History:
{history}

Current Question:
{current_question}

Generate a comprehensive search query that would retrieve the most relevant information for answering the current question in the context of this conversation. 
Focus on key concepts, domain-specific terms, and the progressive nature of the conversation.

Enhanced Search Query:"""

EVALUATION_PROMPT = """Please evaluate the following response on a scale of 0-10 based on these criteria:

1. Relevance (0-3 points): How well does the response address the specific question?
2. Accuracy (0-3 points): How factually correct is the information provided?
3. Completeness (0-2 points): How comprehensive is the answer?
4. Context Integration (0-2 points): How well does it use conversation history (if applicable)?

Question: {question}
Conversation History: {history}
Response: {response}

Please provide:
1. Score breakdown for each criteria
2. Total score (0-10)
3. Brief explanation of the scoring
4. Key strengths and weaknesses

Format your response as JSON:
{
    "relevance": score,
    "accuracy": score, 
    "completeness": score,
    "context_integration": score,
    "total_score": total,
    "explanation": "brief explanation",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"]
}"""
