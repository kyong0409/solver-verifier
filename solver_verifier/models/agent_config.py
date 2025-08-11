"""Configuration models for Analyzer and Verifier agents."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from pathlib import Path


class AgentPromptConfig(BaseModel):
    """Configuration for agent system prompts."""
    role: str = Field(..., description="Agent role (analyzer or verifier)")
    system_prompt: str = Field(..., description="System prompt for the agent")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for LLM generation")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens for generation")
    model_name: str = Field(default="gpt-4o", description="LLM model name")
    additional_instructions: Optional[str] = Field(None, description="Additional instructions")


class PipelineConfig(BaseModel):
    """Configuration for the 6-stage pipeline."""
    max_iterations: int = Field(default=5, ge=1, le=10, description="Maximum iterations for stages 3-5")
    acceptance_threshold: int = Field(default=3, ge=1, le=5, description="Consecutive passes needed for acceptance")
    enable_stage_4_review: bool = Field(default=False, description="Enable optional human/AI review in stage 4")
    stage_timeouts: Dict[int, int] = Field(
        default_factory=lambda: {1: 300, 2: 240, 3: 180, 4: 120, 5: 240, 6: 60},
        description="Timeout in seconds for each stage"
    )


class SystemSettings(BaseSettings):
    """Application-wide settings."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key"
    )
    
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use"
    )
    
    openai_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM generation"
    )
    
    openai_max_tokens: int = Field(
        default=4000,
        ge=1,
        le=16000,
        description="Maximum tokens for LLM response"
    )
    
    # Agent configurations
    analyzer_system_prompt: str = Field(
        default="",
        description="System prompt for the Analyzer agent"
    )
    
    verifier_system_prompt: str = Field(
        default="",
        description="System prompt for the Verifier agent"
    )
    
    def model_post_init(self, __context):
        """Auto-load prompts from files if not set via environment."""
        if not self.analyzer_system_prompt:
            self.analyzer_system_prompt = self._load_prompt_file("prompts/analyzer_prompt.txt")
        
        if not self.verifier_system_prompt:
            self.verifier_system_prompt = self._load_prompt_file("prompts/verifier_prompt.txt")
    
    def _load_prompt_file(self, file_path: str) -> str:
        """Load prompt from file, removing comment lines."""
        try:
            prompt_file = Path(file_path)
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # Remove comment lines starting with #
                    lines = [line for line in content.split('\n') 
                            if not line.strip().startswith('#')]
                    return '\n'.join(lines).strip()
        except Exception as e:
            print(f"Warning: Could not load prompt from {file_path}: {e}")
        return ""
    
    # Pipeline settings
    pipeline_config: PipelineConfig = Field(default_factory=PipelineConfig)
    
    # Storage settings
    output_directory: str = Field(default="./output", description="Directory for output files")
    enable_logging: bool = Field(default=True, description="Enable detailed logging")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Performance settings
    concurrent_processing: bool = Field(default=False, description="Enable concurrent processing where possible")
    batch_size: int = Field(default=10, ge=1, le=100, description="Batch size for processing")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"