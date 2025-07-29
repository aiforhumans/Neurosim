# NeuroSim AI Coding Agent Instructions

## Architecture Overview

NeuroSim is a **local AI companion** with memory and emotion management built on a **modular agent architecture**. The system uses dependency injection patterns and centralized orchestration through `AgentManager`.

### Core Components
- **AgentManager** (`core/agent_manager.py`) - Central orchestrator that wires up all agents
- **SessionState** (`core/state.py`) - Per-user conversation state (mutable across interactions)  
- **Settings** (`core/config.py`) - Environment-based configuration with `NEUROSIM_` prefix
- **Gradio UI** (`interface/ui.py`) - Three-tab interface (Chat, Character Editor, Visualization)
- **DependencyAnalyzer** (`check_dependencies.py`) - Package compatibility checker and installer
- **Logging System** (`core/logging_config.py`) - Structured, colored logging with agent-specific formatting
- **Error Handling** (`core/error_handling.py`) - Comprehensive exception management and recovery
- **Input Validation** (`core/validation.py`) - Robust validation for all user inputs and configuration

### Agent Architecture Pattern
All agents follow this **consistent dependency injection pattern**:
```python
class SomeAgent:
    def __init__(self, config: Optional[Settings] = None):
        self.settings = config or settings  # Dependency injection
        self.logger = get_agent_logger("AgentName", "TYPE")  # Structured logging
```
This pattern enables easy testing, configuration override, modular composition, and comprehensive observability.

**Key Agents:**
- `ChatAgent` - LLM orchestration + memory injection + emotion updates
- `MemoryAgent` - Dual persistence (JSON log + vector embeddings)
- `EmotionAgent` - Sentiment-based mood/trust/energy adjustments (0-1 range)
- `ReasoningAgent` - Separate RunnableSequence for complex tasks (unused in main flow)
- `EventAgent` - Random event generation (extensible via `.events` list)

## Data Flow & State Management

### Message Processing Flow
```
user_message → AgentManager.process_message() → ChatAgent.generate_response()
├── MemoryAgent.search_memory() (semantic search for context)
├── LLM invocation with memory context as SystemMessage  
├── SessionState.conversation_history update (direct mutation)
├── MemoryAgent.store_memory() (both user + assistant messages)
└── EmotionAgent.update_on_message() (sentiment analysis)
```

### State Mutation Pattern
- `SessionState` is **mutable** - agents directly modify it
- Emotional state updates: `session_state.emotion = agent.update_on_message()`
- Conversation history: Direct `.append()` to `session_state.conversation_history`
- Memory context: Retrieved via semantic search and injected as SystemMessage
- **Critical**: State changes persist across agent calls within a session

### Dual Memory Architecture
The system implements a sophisticated dual-persistence memory pattern:
1. **JSON log** (`data/memories/memory.json`) - Structured, append-only conversation log
2. **Vector embeddings** (`data/embeddings/chroma.sqlite3`) - Semantic search via Chroma
3. **Search flow**: Query → embedding → similarity search → Document objects → context injection

## Configuration & Environment

**Environment Variables:** All prefixed with `NEUROSIM_` (e.g., `NEUROSIM_BASE_URL`, `NEUROSIM_MODEL`)

**Default LLM Setup:** Expects local LM Studio at `http://localhost:1234/v1`

**Data Persistence:**
- Characters: `data/characters/*.json` (JSON with traits, baselines)
- Memory: `data/memories/memory.json` (append-only log)  
- Embeddings: `data/embeddings/chroma.sqlite3` (Chroma vector store with SQLite backend)
- Generated files: Auto-created PowerShell scripts, dependency analysis reports

## Key Patterns & Conventions

### Modern LangChain Import Structure
The codebase uses the newer modular LangChain structure:
```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma  # Updated from langchain_community
```
**Critical:** Always use these modular imports, not legacy `langchain.*` imports.

### Structured Logging Pattern
All agents implement comprehensive logging with agent-specific formatting:
```python
from neurosim.core.logging_config import get_agent_logger

class SomeAgent:
    def __init__(self, config: Optional[Settings] = None):
        self.logger = get_agent_logger("SomeAgent", "TYPE")
        self.logger.info("Agent initialized")
        
    def some_method(self):
        self.logger.debug(f"Processing input: {input_data}")
        # Color-coded console output: INFO=green, WARNING=yellow, ERROR=red
```

### Error Handling & Recovery
Use the centralized error handling system for consistent exception management:
```python
from neurosim.core.error_handling import handle_exceptions, safe_call, ValidationError

@handle_exceptions(default_return="fallback response")
def risky_operation():
    # Operation that might fail
    pass

# Safe function calls with defaults
result = safe_call(potentially_failing_func, arg1, arg2, default="safe_value")
```

### Input Validation Pattern
Always validate user inputs using the validation system:
```python
from neurosim.core.validation import validate_user_message, validate_emotion_values

def process_user_input(message: str):
    clean_message = validate_user_message(message)  # Sanitizes and validates
    # Process validated input
```

### Optional Dependency Handling
```python
try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    Chroma = None  # type: ignore
```
Used throughout for `tiktoken`, `vaderSentiment`, vector stores. This pattern ensures graceful degradation when optional packages are missing.

### Settings Resolution
```python
def _resolve_data_path(sub_path: str) -> Path:
    return Path(__file__).resolve().parents[2] / "data" / sub_path
```
All data paths computed relative to project root via file traversal.

### Gradio Callback Pattern
UI callbacks return tuples for multiple output updates:
```python
def respond(user_message: str, chat_history: list) -> tuple:
    # Process message
    return "", chat_history, plot_fig  # Clear input, update chat, refresh plot
```

### Error Handling
Agents use comprehensive error handling with structured logging:
```python
try:
    response_message = self.llm.invoke(messages)
    assistant_reply: str = response_message.content
    self.logger.debug(f"Generated response with {len(assistant_reply)} characters")
except Exception as e:
    self.logger.error(f"LLM invocation failed: {e}")
    assistant_reply = "Sorry, something went wrong while generating a response."
```

## Development Workflows

**Check Dependencies:** `python check_dependencies.py` (always run before development)

**Run Application:** `python run.py` (from project root)

**Test Core Systems:** `python test_core.py` (tests without Chroma SQLite issues)

**Run Full Test Suite:** `python -m pytest tests/ -v` (comprehensive testing)

**Dependency Management:**
- Use `DependencyAnalyzer` class for compatibility checking
- Install packages in suggested order to avoid conflicts
- Generated PowerShell scripts automate safe installation
- Run `check_dependencies.py` before any development work

**Add New Agent:**
1. Create in `agents/` following the constructor pattern
2. Add to `agents/__init__.py` imports
3. Wire up in `AgentManager.__init__()`
4. Follow dependency injection pattern for Settings

**Extend Character System:** 
- Modify `data/characters/default.json` structure
- Update `Character.from_json()` classmethod
- Adjust character editor UI in `interface/character_editor.py`

**Vector Store Switching:**
Set `NEUROSIM_VECTOR_STORE_TYPE=qdrant` and configure `NEUROSIM_QDRANT_URL`

## Integration Points

**LangChain Integration:** Uses `ChatOpenAI`, `HuggingFaceEmbeddings`, vector stores
**Memory System:** Dual persistence - structured JSON + semantic vector search  
**UI Framework:** Gradio Blocks with tab-based layout
**Emotion Visualization:** matplotlib plots updated on each interaction
**Dependency Management:** Automated compatibility checking and installation ordering

## Advanced Dependency Management

### DependencyAnalyzer System
The `check_dependencies.py` script provides sophisticated package compatibility analysis:

```python
class DependencyAnalyzer:
    def check_compatibility(self) -> Dict[str, List[str]]:
        # Identifies missing packages, version conflicts, and warnings
        
    def suggest_installation_order(self) -> List[str]:
        # Returns optimal installation sequence to prevent conflicts
        
    def generate_install_script(self) -> str:
        # Creates PowerShell automation scripts
```

**Key Features:**
- **Compatibility Analysis**: Detects version conflicts and missing packages
- **Installation Ordering**: Prevents dependency hell by installing in optimal sequence
- **Script Generation**: Creates PowerShell automation for safe installation
- **Requirements Management**: Supports both `.in` and `.txt` requirements files

**Critical Installation Order:**
1. Core packages (`pydantic`, `typing-extensions`) 
2. LangChain ecosystem (`langchain-core` → `langchain-community` → `langchain-openai` → `langchain-huggingface`)
3. ML/AI packages (`sentence-transformers`, HuggingFace models)
4. Vector stores (`chromadb`, `qdrant-client`)
5. UI and visualization (`gradio`, `matplotlib`)
6. Optional tools (`tiktoken`, `vaderSentiment`, `pip-tools`)

### Dependency Workflow
```bash
# 1. Always check compatibility first
python check_dependencies.py

# 2. Use generated script for installation
powershell -ExecutionPolicy Bypass -File install_dependencies.ps1

# 3. Verify installation
python -c "from neurosim.core.agent_manager import AgentManager; print('✓ Success')"
```

## Testing Local Setup

**Prerequisites:** Ensure LM Studio is running locally at `http://localhost:1234/v1`

**Setup Verification:**
1. `python check_dependencies.py` - verify all dependencies compatible
2. `python run.py` starts without import errors
3. Gradio interface loads at localhost  
4. Chat tab processes messages
5. Emotion plot updates after interactions
6. Character editor loads `data/characters/default.json`

**Troubleshooting:**
- Import errors: Run dependency checker and follow installation order
- LangChain issues: Verify modular imports (`langchain_openai`, not `langchain.chat_models`)
- Missing embeddings: Install `langchain-huggingface` and `sentence-transformers`
- Gradio launch errors: Check if all agents initialize without import errors
- Vector store issues: Verify `chromadb` installation and SQLite backend availability

## Recent System Enhancements

### Production-Ready Infrastructure (2025)
The codebase now includes enterprise-grade reliability features:

**Comprehensive Logging System:**
- Color-coded console output with agent type identifiers ([CHAT], [MEMORY], [EMOTION])
- File logging with rotation and detailed context (function names, timestamps)
- Agent-specific loggers for precise debugging and monitoring

**Robust Error Handling:**
- Custom exception hierarchy (NeuroSimError, AgentError, ConfigurationError, etc.)
- Decorator-based exception handling with fallbacks (`@handle_exceptions`)
- Safe function calling with default returns (`safe_call`)
- User-friendly error message formatting

**Input Validation System:**
- Message validation (length limits, character encoding, security checks)
- Configuration validation (URLs, API keys, model names, file paths)
- Emotion state bounds enforcement (0.0-1.0 range validation)
- JSON schema validation for character files

**Testing Infrastructure:**
- Comprehensive test suite (`tests/`) with pytest framework
- Core functionality tests (`test_core.py`) avoiding Windows SQLite issues
- Agent-specific test modules with proper mocking and fixtures
- Chroma resource cleanup handling for Windows environments

## Key Insights for AI Agents

### Immediate Productivity Tips
1. **Always run `python check_dependencies.py` first** - This identifies missing packages and version conflicts before they cause import errors
2. **Follow the modular LangChain imports** - Use `langchain_openai`, `langchain_chroma`, `langchain_huggingface` instead of legacy imports
3. **Understand the agent wiring** - `AgentManager` coordinates everything; agents use dependency injection for testability
4. **Respect state mutation** - `SessionState` is mutable; agents directly modify conversation history and emotion state
5. **Use structured logging** - All agents have `self.logger` for debugging and monitoring
6. **Memory is dual-layered** - JSON log for structured data, vector embeddings for semantic search

### Common Pitfalls to Avoid
- Don't use `langchain.*` imports - they're deprecated
- Don't forget to call `persist()` on Chroma vector stores
- Don't modify agent constructor patterns - they use consistent dependency injection
- Don't ignore the dependency installation order - it prevents conflicts
- Don't assume packages are installed - use try/except blocks for optional dependencies

### Architecture Understanding
- **AgentManager** is the central orchestrator that wires up all dependencies
- **SessionState** holds mutable per-user state across interactions
- **Memory flows**: JSON log (structured) + Chroma embeddings (semantic search)
- **UI architecture**: Three-tab Gradio interface with tuple-based callbacks
- **Configuration**: Environment-based with `NEUROSIM_` prefix convention
- **Logging flows**: Agent operations → structured logs → console (colored) + file (detailed)
- **Error flows**: Exceptions → custom handlers → user-friendly messages + detailed logs
