from dotenv import load_dotenv
import typer
from prompt_toolkit import PromptSession
from rich.console import Console

from enum import Enum
from typing import Dict, Any
import json

from deep_research_py.deep_research import deep_research, write_final_report
from deep_research_py.feedback import generate_feedback
from deep_research_py.ai.providers import get_ai_client

from whisk.kitchenai_sdk.kitchenai import KitchenAIApp

from whisk.kitchenai_sdk.schema import (ChatInput, ChatResponse)

load_dotenv()

app = typer.Typer()
console = Console()
session = PromptSession()

kitchenai_app = KitchenAIApp(
    namespace="Deep Research",
)

class ResearchState(Enum):
    AWAITING_QUERY = "awaiting_query"
    AWAITING_BREADTH = "awaiting_breadth"
    AWAITING_DEPTH = "awaiting_depth"
    ASKING_QUESTIONS = "asking_questions"
    RESEARCHING = "researching"
    COMPLETE = "complete"

# Global state storage (you might want to use a proper database in production)
conversation_states: Dict[str, Dict[str, Any]] = {}




@kitchenai_app.chat.handler("chat.completions")
async def main(input: ChatInput) -> ChatResponse:
    # Debug logging
    print("Input metadata:", input.metadata)
    print("Input messages:", [
        {
            "role": msg.role,
            "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
        } 
        for msg in input.messages
    ])
    
    # Extract conversation ID from metadata or generate from messages
    conversation_id = None
    
    # Try to get from metadata if it exists
    if input.metadata:
        conversation_id = input.metadata.get("conversation_id")
    
    # If no conversation_id in metadata, try to generate one from messages
    if not conversation_id and input.messages:
        # Use the first few messages to create a stable ID for the conversation
        conversation_text = "".join(msg.content for msg in input.messages[:1])
        conversation_id = str(hash(conversation_text))
    
    # Fallback to default if we still don't have an ID
    if not conversation_id:
        conversation_id = "default"
    
    current_message = input.messages[-1].content if input.messages else ""
    
    # Initialize or get existing state
    if conversation_id not in conversation_states:
        # Always start fresh with AWAITING_QUERY for the first interaction
        conversation_states[conversation_id] = {
            "state": ResearchState.AWAITING_QUERY,
            "query": None,
            "breadth": None,
            "depth": None,
            "questions": [],
            "answers": [],
            "current_question_idx": 0,
            "research_results": None
        }
        

        return ChatResponse(
            content="🔍 What would you like to research?"
        )
    
    state_data = conversation_states[conversation_id]
    
    # State machine for research flow
    if state_data["state"] == ResearchState.AWAITING_QUERY:
        state_data["query"] = current_message
        state_data["state"] = ResearchState.AWAITING_BREADTH
        return ChatResponse(
            content="📊 Research breadth (recommended 2-10) [4]: "
        )
        
    elif state_data["state"] == ResearchState.AWAITING_BREADTH:
        try:
            state_data["breadth"] = int(current_message or "4")
            state_data["state"] = ResearchState.AWAITING_DEPTH
            return ChatResponse(
                content="🔍 Research depth (recommended 1-5) [2]: "
            )
        except ValueError:
            return ChatResponse(
                content="Please enter a valid number for research breadth:"
            )
            
    elif state_data["state"] == ResearchState.AWAITING_DEPTH:
        try:
            state_data["depth"] = int(current_message or "2")
            
            # Generate follow-up questions
            client = get_ai_client("openai", console)  # You might want to make this configurable
            model = "o3-mini"  # Make configurable
            
            state_data["questions"] = await generate_feedback(state_data["query"], client, model)
            state_data["state"] = ResearchState.ASKING_QUESTIONS
            
            return ChatResponse(
                content=f"[Q1] {state_data['questions'][0]}"
            )
            
        except ValueError:
            return ChatResponse(
                content="Please enter a valid number for research depth:"
            )
            
    elif state_data["state"] == ResearchState.ASKING_QUESTIONS:
        # Store the answer to the current question
        state_data["answers"].append(current_message)
        
        # Move to next question or start research
        if len(state_data["answers"]) < len(state_data["questions"]):
            next_q_idx = len(state_data["answers"])
            return ChatResponse(
                content=f"[Q{next_q_idx + 1}] {state_data['questions'][next_q_idx]}"
            )
        else:
            state_data["state"] = ResearchState.RESEARCHING
            
            # Combine information for research
            combined_query = f"""
            Initial Query: {state_data['query']}
            Follow-up Questions and Answers:
            {chr(10).join(f"Q: {q} A: {a}" for q, a in zip(state_data['questions'], state_data['answers']))}
            """
            
            # Perform research
            client = get_ai_client("openai", console)
            model = "o3-mini"
            
            research_results = await deep_research(
                query=combined_query,
                breadth=state_data["breadth"],
                depth=state_data["depth"],
                concurrency=4,  # Make configurable
                client=client,
                model=model,
            )
            
            # Generate final report
            report = await write_final_report(
                prompt=combined_query,
                learnings=research_results["learnings"],
                visited_urls=research_results["visited_urls"],
                client=client,
                model=model,
            )
            
            # Format final response
            final_response = f"""Research Complete!

Final Report:
{report}

Sources:
{chr(10).join(f"• {url}" for url in research_results['visited_urls'])}
"""
            
            state_data["state"] = ResearchState.COMPLETE
            return ChatResponse(
                content=final_response
            )
    
    elif state_data["state"] == ResearchState.COMPLETE:
        # Reset state for new research
        conversation_states[conversation_id] = {
            "state": ResearchState.AWAITING_QUERY,
            "query": None,
            "breadth": None,
            "depth": None,
            "questions": [],
            "answers": [],
            "current_question_idx": 0,
            "research_results": None
        }
        return ChatResponse(
            content="Would you like to start a new research? What topic would you like to explore?"
        )
    
    # Fallback response
    return ChatResponse(
        content="I'm sorry, something went wrong. Let's start over. What would you like to research?"
    )


