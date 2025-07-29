"""
REST API for NeuroSim.

This module defines a simple FastAPI application exposing endpoints
that mirror the functionality of the Gradio UI. The API can be used
to integrate NeuroSim with other systems or build custom front ends.

To run the API install ``fastapi`` and ``uvicorn`` and execute
``uvicorn neurosim.api:app --reload``. Set ``NEUROSIM_API_KEY`` in
your environment to require an API key; if unset the API will accept
unauthenticated requests. For real deployments you should implement
proper authentication, rate limiting and input validation.
"""

from __future__ import annotations

from typing import Optional

import os
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel

from neurosim.core.agent_manager import AgentManager
from neurosim.core.state import SessionState


app = FastAPI(title="NeuroSim API", version="0.1.0")

# Create a global AgentManager. In a production system you might
# instantiate per user session or manage state differently.
agent_manager = AgentManager()


def get_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    """Simple API key dependency. Raises if the key does not match the configured value."""
    configured_key = os.getenv("NEUROSIM_API_KEY")
    if configured_key and x_api_key != configured_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return None


class MessageRequest(BaseModel):
    """Schema for chat messages sent to the API."""

    message: str


@app.post("/chat", dependencies=[Depends(get_api_key)])
def chat(request: MessageRequest):
    """
    Process a chat message and return the assistant's reply.

    The session state is per-request in this simple implementation.
    """
    session_state = SessionState()
    reply = agent_manager.process_message(request.message, session_state)
    return {"reply": reply, "emotion": session_state.emotion.as_dict()}


class PlanRequest(BaseModel):
    """Schema for reasoning requests."""

    task: str


@app.post("/plan", dependencies=[Depends(get_api_key)])
def plan(request: PlanRequest):
    """
    Generate a plan for a complex task using the ReasoningAgent.
    """
    reasoning_agent = agent_manager.reasoning_agent
    result = reasoning_agent.analyse(request.task)
    return {"plan": result}


@app.get("/events", dependencies=[Depends(get_api_key)])
def get_events():
    """Return the list of currently available events."""
    event_agent = agent_manager.event_agent
    if event_agent.custom_events:
        events = event_agent.custom_events
    else:
        events = event_agent.day_events + event_agent.night_events
    return {"events": events}