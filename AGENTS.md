# Dripage - AGENTS.md

Project-specific guidelines for agentic coding.

## Build & Test Commands

### Running the Project
This project uses **uv** as the package manager. Always use `uv run` for executing Python scripts.

```bash
# Run main CLI
uv run dripage

# Run MCP server (HTTP mode for testing)
PYTHONPATH="G:\code\agent-use\dripage" uv run mcp_server.py http

# Run MCP server (STDIO mode for production)
PYTHONPATH="G:\code\agent-use\dripage" uv run mcp_server.py
```

### Running Tests

Tests are located in the `test/` directory. Run tests directly:

```bash
# Run a single test file
PYTHONPATH="G:\code\agent-use\dripage" uv run test/test_mcp_server.py

# Run a specific test (if using pytest)
uv run pytest test/test_mcp_server.py::test_function_name
```

Tests use `asyncio` for async operations. No test configuration file exists - tests run directly with Python.

### Entry Points
- `cli` - Main CLI entry point (`dripage` command)
- `mcp_server:main` - MCP server (`dripage-mcp` command)
- Other entry points in `pyproject.toml` [project.scripts]

## Code Style Guidelines

### Imports
- Generally grouped but not strictly separated (stdlib, third-party, local mixed)
- Add project directory to path when needed:
  ```python
  project_dir = Path(__file__).resolve().parent
  if str(project_dir) not in sys.path:
      sys.path.insert(0, str(project_dir))
  ```

### Type Annotations
- Use `typing` module: `Optional`, `List`, `Union`, `Dict`, `Any`, `TypedDict`
- Extensive use of type hints for function parameters and return values
- Example: `def func(x: Optional[str] = None) -> str:`

### Naming Conventions
- **Functions**: `snake_case` (e.g., `browser_navigate`, `get_config`)
- **Classes**: `PascalCase` (e.g., `BrowserToolConfig`, `CoordinateConverter`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `LOG_LEVEL`, `LOG_DIR`)
- **Variables**: `snake_case`

### Docstrings
- Triple-quoted docstrings (both English and Chinese used)
- Mixed Google/NumPy style
- Include Args, Returns, Example sections where appropriate

### Error Handling
- Use try/except blocks with logging
- Return error information as JSON dicts:
  ```python
  try:
      # code
  except Exception as e:
      logger.error(f"Operation failed: {e}")
      return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)
  ```

### Logging
- Uses **loguru** for logging
- Custom `get_logger()` function in `utils/logu.py`:
  ```python
  from utils.logu import get_logger
  logger = get_logger('module_name')
  logger.info("Message")
  ```
- Named loggers for each module (`get_logger('browser_tools')`)

### Configuration
- YAML-based configuration in `config/` directory
- Config loaded with `yaml.safe_load()`
- Example config files: `config/mcp_config.yaml`, `config/tools_runtime.yaml`
- Runtime configuration patterns with global config instances (singleton pattern)

### Async/Await
- Extensive use of `asyncio` for async operations
- Functions marked with `async def` where appropriate
- Use `await asyncio.to_thread()` for blocking operations in async context

### JSON Handling
- Use `json.dumps()` with `ensure_ascii=False, indent=2` for output
- Use `json.loads()` for parsing

### Tool Decorators
- LangChain tools use `@tool` decorator from `langchain.tools`
- FastMCP tools use `@mcp.tool` decorator
- Tools have `.func` attribute for direct function access

### Path Handling
- Use `pathlib.Path` for path operations
- Project root resolution: `Path(__file__).resolve().parent`

## Project Structure

```
dripage/
├── cli.py              # Main CLI entry point (Click-based)
├── mcp_server.py       # FastMCP server
├── tools/              # Browser and agent tools
├── utils/              # Utilities (logging, browser management)
├── test/               # Test files
├── config/             # YAML configuration files
├── example/            # Example scripts
├── services/           # Chrome RPC/HTTP services
└── pyproject.toml      # Project configuration and dependencies
```

## Dependencies

Key external libraries:
- **click** - CLI framework
- **fastmcp** - MCP server
- **drissionpage** - Browser automation
- **langchain** - LLM framework
- **langgraph** - Graph-based workflows
- **loguru** - Logging

Python version: >= 3.13

## Notes for Agents

1. Always use `uv run` instead of `python` directly
2. Set `PYTHONPATH` when running scripts outside project root
3. Check for YAML config files in `config/` directory
4. Use loguru for logging, not standard logging module
5. Browser operations use DrissionPage library
6. Return JSON-formatted responses with proper error handling
