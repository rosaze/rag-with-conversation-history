from config.prompts import QUERY_ENHANCEMENT_PROMPT

class QueryEnhancer:
    def __init__(self, llm_handler):
        self.llm_handler = llm_handler
    
    def enhance_query(self, conversation_history, current_question):
        """Generate enhanced search query using conversation history"""
        try:
            # Format conversation history
            history_text = "\n".join([f"- {msg}" for msg in conversation_history])
            
            # Create enhancement prompt
            prompt = QUERY_ENHANCEMENT_PROMPT.format(
                history=history_text,
                current_question=current_question
            )
            
            # Generate enhanced query
            result = self.llm_handler.generate_response(prompt)
            enhanced_query = result["response"].strip()
            
            # Clean up the query (remove quotes, excessive punctuation)
            enhanced_query = enhanced_query.strip('"\'')
            
            return {
                "original_question": current_question,
                "enhanced_query": enhanced_query,
                "history_length": len(conversation_history)
            }
            
        except Exception as e:
            # Fallback to original question if enhancement fails
            return {
                "original_question": current_question,
                "enhanced_query": current_question,
                "history_length": len(conversation_history),
                "error": f"Query enhancement failed: {str(e)}"
            }
    
    def combine_queries(self, original_question, conversation_history, strategy="contextual"):
        """Combine original question with conversation context using different strategies"""
        
        if strategy == "simple":
            # Simple concatenation
            context = " ".join(conversation_history[-2:])  # Last 2 messages
            return f"{context} {original_question}"
        
        elif strategy == "contextual":
            # Use LLM to intelligently combine
            return self.enhance_query(conversation_history, original_question)["enhanced_query"]
        
        elif strategy == "keyword":
            # Extract keywords from history and combine
            keywords = self._extract_keywords(conversation_history)
            return f"{original_question} {' '.join(keywords)}"
        
        else:
            return original_question
    
    def _extract_keywords(self, conversation_history):
        """Simple keyword extraction from conversation history"""
        # This is a simplified version - in practice, you might use NLP libraries
        import re
        
        text = " ".join(conversation_history)
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out common words (simplified stopword removal)
        stopwords = {
            'the', 'and', 'but', 'for', 'are', 'with', 'they', 'this', 'that',
            'have', 'from', 'not', 'been', 'has', 'her', 'his', 'she', 'can',
            'all', 'any', 'may', 'had', 'was', 'were', 'will', 'you', 'your'
        }
        
        keywords = [word for word in words if word not in stopwords]
        
        # Return unique keywords (limit to 5)
        return list(set(keywords))[:5]
    
    def analyze_query_effectiveness(self, original_query, enhanced_query, search_results):
        """Analyze how query enhancement affected search results"""
        return {
            "original_query": original_query,
            "enhanced_query": enhanced_query,
            "query_length_change": len(enhanced_query) - len(original_query),
            "result_count": len(search_results.get("results", [])),
            "enhancement_used": original_query != enhanced_query
        }
