"""
Service layer for Human Simulator plugin - connects to the main human-simulator backend.
"""
import logging
import os
import httpx
from typing import Dict, List, Any, Optional
from fastapi import HTTPException

# Configure logging
logger = logging.getLogger("api.plugins.human_simulator.services")

# Human Simulator backend configuration
HS_BACKEND_URL = os.environ.get("HS_BACKEND_URL", "http://localhost:5000/api")
HS_API_KEY = os.environ.get("HS_API_KEY", "")

class HumanSimulatorService:
    """Service for integrating with the main Human Simulator backend"""
    
    def __init__(self, base_url=None, api_key=None):
        """Initialize the service with connection parameters"""
        self.base_url = base_url or HS_BACKEND_URL
        self.api_key = api_key or HS_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
        }
        
    async def _request(self, method: str, endpoint: str, data=None, params=None) -> Dict:
        """
        Make an HTTP request to the Human Simulator backend
        """
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method, 
                    url, 
                    json=data, 
                    params=params, 
                    headers=self.headers,
                    timeout=10.0
                )
                
                # Handle HTTP errors
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {str(e)}")
            raise HTTPException(status_code=503, detail="Service Unavailable")
        except Exception as e:
            logger.error(f"Unexpected error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    async def get_scenarios(self, filter_params=None) -> List[Dict[str, Any]]:
        """Get scenarios from the Human Simulator backend"""
        return await self._request("GET", "/scenario", params=filter_params)
    
    async def get_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Get a specific scenario by ID"""
        return await self._request("GET", f"/scenario/{scenario_id}")
        
    async def create_scenario(self, scenario_data: Dict) -> Dict[str, Any]:
        """Create a new scenario"""
        return await self._request("POST", "/scenario", data=scenario_data)

    async def update_scenario(self, scenario_id: str, scenario_data: Dict) -> Dict[str, Any]:
        """Update an existing scenario"""
        return await self._request("PUT", f"/scenario/{scenario_id}", data=scenario_data)

    async def delete_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Delete a scenario"""
        return await self._request("DELETE", f"/scenario/{scenario_id}")
    
    async def get_personas(self, filter_params=None) -> List[Dict[str, Any]]:
        """Get personas from the Human Simulator backend"""
        return await self._request("GET", "/persona", params=filter_params)
    
    async def get_persona(self, persona_id: str) -> Dict[str, Any]:
        """Get a specific persona by ID"""
        return await self._request("GET", f"/persona/{persona_id}")
        
    async def create_persona(self, persona_data: Dict) -> Dict[str, Any]:
        """Create a new persona"""
        return await self._request("POST", "/persona", data=persona_data)

    async def update_persona(self, persona_id: str, persona_data: Dict) -> Dict[str, Any]:
        """Update an existing persona"""
        return await self._request("PUT", f"/persona/{persona_id}", data=persona_data)

    async def delete_persona(self, persona_id: str) -> Dict[str, Any]:
        """Delete a persona"""
        return await self._request("DELETE", f"/persona/{persona_id}")
    
    async def analyze_message(self, message_data: Dict) -> Dict[str, Any]:
        """Send a message for analysis by the human simulator"""
        return await self._request("POST", "/v2/analyze", data=message_data)
    
    # MirrorCore specific endpoints
    async def evaluate(self, user_message: Dict) -> Dict[str, Any]:
        """Evaluate user message and determine next stage transition"""
        return await self._request("POST", "/mirrorcore/evaluate", data=user_message)
    
    async def get_sessions(self, user_id: str, character_name: Optional[str] = None) -> Dict[str, Any]:
        """Get session history by user ID and character name"""
        params = {"user_id": user_id}
        if character_name:
            params["character_name"] = character_name
        return await self._request("GET", "/mirrorcore/sessions", params=params)
    
    async def save_session(self, session_data: Dict) -> Dict[str, Any]:
        """Save a session with metrics and stage information"""
        return await self._request("POST", "/mirrorcore/save-session", data=session_data)

# Create a service instance for use in routes
human_simulator_service = HumanSimulatorService()
