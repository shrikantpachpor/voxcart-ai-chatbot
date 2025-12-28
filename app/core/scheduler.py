import asyncio
import httpx
import logging
from typing import Any

async def update_attack_vectors(defender: Any = None):
    while True:
        try:
            response = httpx.get("https://raw.githubusercontent.com/rebuff-ai/rebuff/main/attack-patterns.json")
            if response.status_code == 200 and defender:
                if hasattr(defender, 'add_attack_patterns'):
                    defender.add_attack_patterns(response.json())
                    logging.info("Updated attack vectors from Rebuff feed")
        except Exception as e:
            logging.error(f"Failed to update attack vectors: {str(e)}")
        
        await asyncio.sleep(86400)

async def startup_event(defender: Any = None):
    if defender:
        asyncio.create_task(update_attack_vectors(defender))