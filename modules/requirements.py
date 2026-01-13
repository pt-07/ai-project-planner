import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class RequirementsGatherer:
    """Handles interactive requirements gathering using Claude API"""

    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"
        self.conversation_history = []

    def start_session(self, project_name, project_description):
        """Start a requirements gathering session"""
        self.conversation_history = []
        self.project_name = project_name
        self.project_description = project_description

        # Store system prompt for reuse
        self.system_prompt = f"""You are an expert software requirements analyst. Your task is to gather comprehensive requirements for a software project through an interactive conversation.

Project: {project_name}
Description: {project_description}

Your goal is to ask exactly 8 focused, insightful questions to understand:
- Key functional requirements (what the system should do)
- Non-functional requirements (performance, security, usability, etc.)
- Technical constraints (platforms, technologies, limitations)
- User needs and use cases

Ask one question at a time. Make each question clear, specific, and relevant to the project context. Build upon previous answers to ask progressively deeper questions.

After all 8 questions are answered, you will extract and categorize the requirements."""

        return self.system_prompt

    def ask_next_question(self, user_response=None):
        """Ask the next question in the requirements gathering process"""

        # Add user response to conversation history if provided
        if user_response:
            self.conversation_history.append({
                "role": "user",
                "content": user_response
            })

        # Determine which question number we're on
        question_number = len([msg for msg in self.conversation_history if msg["role"] == "assistant"]) + 1

        if question_number > 8:
            return None  # All questions asked

        # Build the prompt for the next question
        if question_number == 1:
            prompt = f"""This is a requirements gathering session for: {self.project_name}

Description: {self.project_description}

Ask your first question (1 of 8) to gather important requirements. Be specific and relevant to this project."""
        else:
            prompt = f"Based on the previous answer, ask your next question ({question_number} of 8). Build upon what you've learned so far."

        # Call Claude API
        messages = self.conversation_history.copy()
        messages.append({
            "role": "user",
            "content": prompt
        })

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=[
                {
                    "type": "text",
                    "text": self.system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=messages
        )

        assistant_message = response.content[0].text

        # Add assistant's question to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def extract_requirements(self):
        """Extract structured requirements from the conversation"""

        extraction_prompt = """Based on the entire conversation above, extract all requirements and categorize them.

Return your response as a JSON object with this exact structure:
{
    "functional": [
        "requirement description 1",
        "requirement description 2"
    ],
    "non_functional": [
        "requirement description 1",
        "requirement description 2"
    ],
    "constraints": [
        "constraint description 1",
        "constraint description 2"
    ]
}

Ensure each requirement is:
- Clear and specific
- Actionable
- Derived from the conversation
- Properly categorized

Return ONLY the JSON object, no additional text."""

        messages = self.conversation_history.copy()
        messages.append({
            "role": "user",
            "content": extraction_prompt
        })

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=[
                {
                    "type": "text",
                    "text": self.system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=messages
        )

        requirements_json = response.content[0].text.strip()

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if requirements_json.startswith('```'):
                requirements_json = requirements_json.split('```')[1]
                if requirements_json.startswith('json'):
                    requirements_json = requirements_json[4:]
                requirements_json = requirements_json.strip()

            requirements = json.loads(requirements_json)
            return requirements
        except json.JSONDecodeError as e:
            print(f"Error parsing requirements JSON: {e}")
            print(f"Raw response: {requirements_json}")
            # Return empty structure if parsing fails
            return {
                "functional": [],
                "non_functional": [],
                "constraints": []
            }

    def get_conversation_summary(self):
        """Get a summary of the conversation for export"""
        summary = []
        question_num = 1

        # The conversation history alternates: user prompt, assistant question, user answer, assistant question, etc.
        # We want to extract only the Q&A pairs, skipping the internal prompts

        i = 0
        while i < len(self.conversation_history):
            msg = self.conversation_history[i]

            # Skip internal prompts (they start with "This is a requirements" or "Based on the previous")
            if msg["role"] == "user" and (
                msg['content'].startswith("This is a requirements gathering") or
                msg['content'].startswith("Based on the previous answer")
            ):
                i += 1
                continue

            # Assistant messages are questions
            if msg["role"] == "assistant":
                summary.append(f"Q{question_num}: {msg['content']}")
                question_num += 1

            # User messages (that aren't prompts) are answers
            elif msg["role"] == "user":
                summary.append(f"A: {msg['content']}\n")

            i += 1

        return "\n".join(summary)
