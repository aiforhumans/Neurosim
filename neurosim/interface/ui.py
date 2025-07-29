"""
Top-level user interface for NeuroSim using Gradio.

This module defines a function that assembles the entire UI into a
single Gradio Blocks object. It wires up callbacks to the underlying
agent manager and keeps session state isolated per user. Messages are
timestamped to give users a sense of temporal flow in the chat.
"""

from __future__ import annotations

import gradio as gr
from datetime import datetime

from neurosim.core.agent_manager import AgentManager  # type: ignore
from neurosim.core.state import SessionState  # type: ignore
from neurosim.interface.character_editor import build_character_editor  # type: ignore
from neurosim.interface.visualization import build_visualisation, create_emotion_plot  # type: ignore


def create_app(agent_manager: AgentManager) -> gr.Blocks:
    """Return a fully assembled Gradio Blocks application."""

    # Each user session gets its own SessionState instance
    session_state = SessionState()

    def respond(user_message: str, chat_history: list) -> tuple:
        """Handle a chat turn and update UI components.

        Args:
            user_message: The message typed by the user.
            chat_history: A list of message dictionaries with 'role' and 'content' keys
                for Gradio's Chatbot component with type='messages'.

        Returns:
            A tuple of (new_user_message, updated_chat_history, new_plot)
        """
        # Convert chat_history (list of message dicts) to session history format
        session_state.conversation_history = chat_history.copy()

        # Process the latest message
        reply = agent_manager.process_message(user_message, session_state)

        # Append new messages to chat history for display, with timestamps
        timestamp_user = datetime.now().strftime("%H:%M")
        timestamp_assistant = datetime.now().strftime("%H:%M")
        chat_history.append({"role": "user", "content": f"[{timestamp_user}] {user_message}"})
        chat_history.append({"role": "assistant", "content": f"[{timestamp_assistant}] {reply}"})

        # Build a fresh plot for the emotion state
        plot_fig = create_emotion_plot(session_state.emotion)
        # Clear the input box after submission
        return "", chat_history, plot_fig

    with gr.Blocks(title="NeuroSim") as demo:
        gr.Markdown("# NeuroSim \nA local AI companion with memory and emotion management")
        with gr.Tabs():
            with gr.TabItem("Chat"):
                chatbot = gr.Chatbot([], label="Conversation", type='messages')
                user_input = gr.Textbox(
                    label="Your message", placeholder="Say something...", lines=3
                )
                send_btn = gr.Button("Send")
                emotion_plot = gr.Plot(value=create_emotion_plot(session_state.emotion))

                # When the send button is clicked, call the respond function
                send_btn.click(
                    respond,
                    inputs=[user_input, chatbot],
                    outputs=[user_input, chatbot, emotion_plot],
                )
            with gr.TabItem("Character Editor"):
                # Provide an independent character editor UI
                build_character_editor(session_state)
            with gr.TabItem("Visualisation"):
                build_visualisation(session_state)
        return demo