"""Utility for loading system prompts from files."""

from pathlib import Path
from typing import Optional


class PromptLoader:
    """Load system prompts from various sources."""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        
    def load_analyzer_prompt(self) -> Optional[str]:
        """Load analyzer system prompt from file."""
        prompt_file = self.prompts_dir / "analyzer_prompt.txt"
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Remove comment lines starting with #
                lines = [line for line in content.split('\n') if not line.strip().startswith('#')]
                return '\n'.join(lines).strip()
        return None
        
    def load_verifier_prompt(self) -> Optional[str]:
        """Load verifier system prompt from file."""
        prompt_file = self.prompts_dir / "verifier_prompt.txt"
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Remove comment lines starting with #
                lines = [line for line in content.split('\n') if not line.strip().startswith('#')]
                return '\n'.join(lines).strip()
        return None
        
    def save_analyzer_prompt(self, prompt: str) -> None:
        """Save analyzer system prompt to file."""
        self.prompts_dir.mkdir(exist_ok=True)
        prompt_file = self.prompts_dir / "analyzer_prompt.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
            
    def save_verifier_prompt(self, prompt: str) -> None:
        """Save verifier system prompt to file."""
        self.prompts_dir.mkdir(exist_ok=True)
        prompt_file = self.prompts_dir / "verifier_prompt.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)