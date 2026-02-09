"""
Janani AI - Demo Mode Configuration
Feature Toggle System for Hackathon Demos

3 Modes:
- SPEED: Fast responses (3-5s) for 2-min demo
- BALANCED: Medium speed (8-10s) with some features
- FULL: All features enabled (15-20s) for Q&A
"""

import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class DemoMode(str, Enum):
    SPEED = "speed"
    BALANCED = "balanced"
    FULL = "full"


class DemoConfig(BaseModel):
    """Configuration for current demo mode"""
    mode: DemoMode = DemoMode.SPEED
    
    # Response tuning
    max_tokens: int = 300
    temperature: float = 0.3
    timeout: float = 15.0
    
    # Feature toggles
    enable_dialect_translation: bool = False
    enable_memory: bool = False
    enable_who_guard: bool = False
    enable_empathy_layer: bool = False
    enable_detailed_explanations: bool = False
    
    # System prompt optimization
    use_short_prompt: bool = True


# Pre-defined mode configurations
MODE_CONFIGS = {
    DemoMode.SPEED: DemoConfig(
        mode=DemoMode.SPEED,
        max_tokens=300,
        temperature=0.3,
        timeout=15.0,
        enable_dialect_translation=False,
        enable_memory=False,
        enable_who_guard=False,
        enable_empathy_layer=False,
        enable_detailed_explanations=False,
        use_short_prompt=True
    ),
    DemoMode.BALANCED: DemoConfig(
        mode=DemoMode.BALANCED,
        max_tokens=600,
        temperature=0.5,
        timeout=30.0,
        enable_dialect_translation=True,
        enable_memory=True,
        enable_who_guard=False,
        enable_empathy_layer=True,
        enable_detailed_explanations=False,
        use_short_prompt=False
    ),
    DemoMode.FULL: DemoConfig(
        mode=DemoMode.FULL,
        max_tokens=1000,
        temperature=0.7,
        timeout=120.0,
        enable_dialect_translation=True,
        enable_memory=True,
        enable_who_guard=True,
        enable_empathy_layer=True,
        enable_detailed_explanations=True,
        use_short_prompt=False
    )
}


# Current active configuration (loaded from env or defaults to SPEED)
def get_current_mode() -> DemoMode:
    """Get current demo mode from environment"""
    mode_str = os.getenv("JANANI_DEMO_MODE", "speed").lower()
    try:
        return DemoMode(mode_str)
    except ValueError:
        return DemoMode.SPEED


def get_demo_config() -> DemoConfig:
    """Get the configuration for current demo mode"""
    mode = get_current_mode()
    return MODE_CONFIGS[mode]


def set_demo_mode(mode: DemoMode):
    """Set the demo mode (writes to .env file)"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    
    # Read existing .env
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    
    # Update or add JANANI_DEMO_MODE
    found = False
    for i, line in enumerate(lines):
        if line.startswith("JANANI_DEMO_MODE="):
            lines[i] = f"JANANI_DEMO_MODE={mode.value}\n"
            found = True
            break
    
    if not found:
        lines.append(f"\nJANANI_DEMO_MODE={mode.value}\n")
    
    # Write back
    with open(env_path, "w") as f:
        f.writelines(lines)
    
    # Also set environment variable for current session
    os.environ["JANANI_DEMO_MODE"] = mode.value
    
    print(f"✅ Demo mode set to: {mode.value.upper()}")
    return MODE_CONFIGS[mode]


# Singleton for current config
current_config = get_demo_config()


def print_current_config():
    """Print current configuration to console"""
    config = get_demo_config()
    print("\n" + "=" * 50)
    print(f"🎯 JANANI DEMO MODE: {config.mode.value.upper()}")
    print("=" * 50)
    print(f"  Max Tokens: {config.max_tokens}")
    print(f"  Temperature: {config.temperature}")
    print(f"  Timeout: {config.timeout}s")
    print(f"  Dialect Translation: {'✅' if config.enable_dialect_translation else '❌'}")
    print(f"  Memory: {'✅' if config.enable_memory else '❌'}")
    print(f"  WHO Guard: {'✅' if config.enable_who_guard else '❌'}")
    print(f"  Empathy Layer: {'✅' if config.enable_empathy_layer else '❌'}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    print_current_config()
