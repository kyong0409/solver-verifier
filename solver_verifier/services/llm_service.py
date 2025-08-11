"""LLM service for interacting with OpenAI API."""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
from ..models.agent_config import SystemSettings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with OpenAI LLM API."""
    
    def __init__(self, settings: SystemSettings):
        self.settings = settings
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not provided. LLM calls will fail.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None
    ) -> str:
        """
        Call OpenAI API with the provided prompts.
        
        Args:
            system_prompt: System message to set context
            user_prompt: User message with the actual request
            temperature: Override default temperature
            max_tokens: Override default max tokens
            response_format: Expected response format ("json" or None)
            
        Returns:
            LLM response text
            
        Raises:
            ValueError: If API key is not configured
            Exception: If API call fails
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        # Use provided parameters or fall back to settings
        temp = temperature if temperature is not None else self.settings.openai_temperature
        max_tok = max_tokens if max_tokens is not None else self.settings.openai_max_tokens
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Prepare request parameters
            request_params = {
                "model": self.settings.openai_model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": max_tok,
            }
            
            # Add JSON response format if requested
            if response_format == "json":
                request_params["response_format"] = {"type": "json_object"}
            
            logger.debug(f"Calling OpenAI API with model: {self.settings.openai_model}")
            
            # Make API call with retry logic
            response = await self._call_with_retry(request_params)
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI API")
            
            logger.debug(f"Received response with {len(content)} characters")
            return content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise Exception(f"LLM service error: {str(e)}") from e
    
    async def _call_with_retry(self, request_params: Dict[str, Any], max_retries: int = 3) -> Any:
        """Call OpenAI API with exponential backoff retry."""
        
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.chat.completions.create(**request_params)
                return response
                
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                # Calculate backoff delay
                delay = (2 ** attempt) + (0.1 * attempt)  # Exponential backoff with jitter
                logger.warning(f"API call failed (attempt {attempt + 1}), retrying in {delay}s: {str(e)}")
                await asyncio.sleep(delay)
        
        raise Exception("Max retries exceeded")
    
    async def call_llm_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Call LLM and expect JSON response.
        
        Args:
            system_prompt: System message to set context
            user_prompt: User message with the actual request
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Parsed JSON response as dictionary
        """
        # Ensure system prompt mentions JSON format
        if "json" not in system_prompt.lower():
            system_prompt += "\n\nPlease respond with valid JSON format."
        
        response_text = await self.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format="json"
        )
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}") from e
    
    async def test_connection(self) -> bool:
        """Test OpenAI API connection."""
        try:
            await self.call_llm(
                system_prompt="You are a helpful assistant.",
                user_prompt="Say 'OK' if you can receive this message.",
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {str(e)}")
            return False
    
    def is_configured(self) -> bool:
        """Check if LLM service is properly configured."""
        return self.client is not None and bool(self.settings.openai_api_key)