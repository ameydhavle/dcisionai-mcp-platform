# DcisionAI MCP Python SDK

Official Python SDK for connecting to DcisionAI Manufacturing MCP servers.

## Installation

```bash
pip install dcisionai-mcp
```

## Quick Start

```python
import asyncio
from dcisionai_mcp import DcisionAIClient

async def main():
    # Initialize client
    client = DcisionAIClient(api_key="dai_your_api_key_here")
    
    # Complete manufacturing optimization
    result = await client.complete_manufacturing_optimization(
        query="Optimize production line efficiency",
        data={
            "total_workers": 50,
            "production_lines": 3,
            "max_hours_per_week": 48
        }
    )
    
    print(f"Optimization result: {result}")

asyncio.run(main())
```

## Features

- **Easy Integration**: Simple Python client for DcisionAI MCP servers
- **Type Safety**: Full type hints and Pydantic models
- **Async Support**: Built-in async/await support
- **Error Handling**: Comprehensive error handling and retries
- **Manufacturing Tools**: Direct access to all 4 manufacturing optimization tools

## Documentation

- [Quick Start Guide](https://docs.dcisionai.com/quick-start)
- [API Reference](https://docs.dcisionai.com/api-reference)
- [Examples](https://docs.dcisionai.com/examples)

## Support

- **Email**: support@dcisionai.com
- **Documentation**: https://docs.dcisionai.com
- **GitHub**: https://github.com/dcisionai/dcisionai-mcp-python
