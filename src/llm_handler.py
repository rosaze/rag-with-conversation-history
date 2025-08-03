import json
import os
from openai import OpenAI
from config.settings import DEFAULT_MODEL, DEFAULT_TEMPERATURE, MAX_TOKENS
from config.prompts import SYSTEM_PROMPTS

class LLMHandler:
    def __init__(self, api_key, model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE):
        self.client = OpenAI(api_key=api_key)
        self.model = model  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        self.temperature = temperature
    
    def generate_response(self, messages, system_prompt=None):
        """Generate response using OpenAI GPT-4o"""
        try:
            # Prepare messages
            formatted_messages = []
            
            if system_prompt:
                formatted_messages.append({"role": "system", "content": system_prompt})
            
            # Handle different message formats
            if isinstance(messages, str):
                formatted_messages.append({"role": "user", "content": messages})
            elif isinstance(messages, list):
                formatted_messages.extend(messages)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=self.temperature,
                max_tokens=MAX_TOKENS
            )
            
            return {
                "response": response.choices[0].message.content,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    def generate_d1_response(self, question):
        """D1: LLM-only without history"""
        return self.generate_response(
            messages=question,
            system_prompt=SYSTEM_PROMPTS["d1_no_history"]
        )
    
    def generate_d2_response(self, history, question):
        """D2: LLM with conversation history"""
        messages = []
        
        # Add conversation history
        for i, msg in enumerate(history):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({"role": role, "content": msg})
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        return self.generate_response(
            messages=messages,
            system_prompt=SYSTEM_PROMPTS["d2_with_history"]
        )
    
    def generate_d3_response(self, question, search_results):
        """D3: RAG with current question only"""
        # Format search results
        search_context = self._format_search_results(search_results)
        
        # Create message with search context
        message = f"Search Results:\n{search_context}\n\nQuestion: {question}"
        
        return self.generate_response(
            messages=message,
            system_prompt=SYSTEM_PROMPTS["d3_rag_no_history"]
        )
    
    def generate_d4_response(self, history, question, search_results):
        """D4: RAG with history-enhanced query"""
        # Format search results
        search_context = self._format_search_results(search_results)
        
        messages = []
        
        # Add conversation history
        for i, msg in enumerate(history):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({"role": role, "content": msg})
        
        # Add search context as system message
        messages.append({"role": "system", "content": f"Search Results:\n{search_context}"})
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        return self.generate_response(
            messages=messages,
            system_prompt=SYSTEM_PROMPTS["d4_rag_with_history"]
        )
    
    def _format_search_results(self, search_results):
        """Format search results for context"""
        if not search_results:
            return "No search results available."
        
        formatted = []
        for i, result in enumerate(search_results[:5], 1):
            title = result.get('title', 'No title')
            content = result.get('content', result.get('snippet', 'No content'))
            url = result.get('url', '')
            
            formatted.append(f"{i}. {title}\n   {content}\n   Source: {url}\n")
        
        return "\n".join(formatted)
    
    def evaluate_response(self, question, history, response):
        """Use LLM to evaluate response quality"""
        from config.prompts import EVALUATION_PROMPT
        
        eval_prompt = EVALUATION_PROMPT.format(
            question=question,
            history="\n".join(history) if history else "No previous conversation",
            response=response
        )
        
        try:
            result = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": eval_prompt}],
                response_format={"type": "json_object"},
                temperature=0.1  # Lower temperature for more consistent evaluation
            )
            
            return json.loads(result.choices[0].message.content)
        except Exception as e:
            return {
                "error": f"Evaluation failed: {str(e)}",
                "total_score": 0
            }
