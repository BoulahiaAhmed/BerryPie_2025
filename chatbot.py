import json
import os
from groq import Groq
import logging


#set logger
logging.basicConfig(level=logging.INFO)

# Initialize the Groq client (no need to manually pass API key if set in env variable GROQ_API_KEY)
client = Groq()

MODEL_NAME = "llama-3.3-70b-versatile"


class BerryPieChatbot:

    def __init__(self, transcript: str, doc_content: str):
        self.transcript = transcript.strip() if transcript else ""
        self.doc_content = doc_content.strip() if doc_content else ""
        self.history = []
        self._initialize_system_message()

    def _initialize_system_message(self):
        """Initialize the system message with transcript and document context."""
        base_prompt = """
            ROLE: Financial assistant for BerryPie (investment products expert)
            TONE: Professional yet approachable (clear, precise, compliant)

            INSTRUCTIONS:
            1. Prioritize answers from the transcript
            2. Only use document context when transcript is insufficient
            3. For unavailable information: "Based on my resources, I can't provide a definitive answer."
            4. Never speculate - admit uncertainty when needed

            RESPONSE FORMAT:
            - Start with clear answer
            - Add supporting details when relevant
            - End with "Does this help?" or similar
            """.strip()

        transcript_section = f"""
            PRIMARY SOURCE: Video transcript:
            \"\"\"
            {self.transcript}
            \"\"\"
            """.strip() if self.transcript else ""

        doc_section = f"""
            ADDITIONAL CONTEXT:
            You also have access to financial documents (prospectuses and fact sheets).
            If the transcript doesn't contain the answer but these documents do, use them to respond.
            Document content:
            \"\"\"
            {self.doc_content[:7000]}
            \"\"\"
            If the document content is unavailable or irrelevant, say: "I don't have sufficient documentation to answer that."
            """.strip() if self.doc_content else ""

        if not self.transcript and not self.doc_content:
            system_prompt = """
                You're BerryPie's financial assistant, but no product information is currently available.
                Respond professionally: "I don't have any active financial product details to reference at this time.
                Would you like general information about our services?"
                """.strip()
        else:
            system_prompt = "\n".join(
                part for part in [base_prompt, transcript_section, doc_section] 
                if part
            )

        logging.info(f"System prompt initialized: {system_prompt}")

        # Append the system prompt to the history
        # Clean up whitespace and newlines
        system_prompt = "\n".join(line.strip() for line in system_prompt.split("\n"))
        self.history.append({"role": "system", "content": system_prompt.strip()})

    def chat(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})

        # Make the initial API call to Groq
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=self.history,
            temperature=0.2,
            max_tokens=1024,
            top_p=1,
            stream=False  # Not streaming inside the function, returning full reply at once
        )

        response_message = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": response_message})

        return response_message






        # tool_calls = response_message.tool_calls

        # if tool_calls:
        #     # Define the available tools that can be called by the LLM
        #     available_functions = {
        #         "rag_tool": rag_tool,
        #     }
        #     # Add the LLM's response to the conversation
        #     self.history.append(response_message)

        #     # Process each tool call
        #     for tool_call in tool_calls:
        #         function_name = tool_call.function.name
        #         function_to_call = available_functions[function_name]
        #         function_args = json.loads(tool_call.function.arguments)
        #         # Call the tool and get the response
        #         function_response = function_to_call(
        #             query=function_args.get("query"), vectordb=self.vectordb
        #         )
        #         # Add the tool response to the conversation
        #         self.history.append(
        #             {
        #                 "tool_call_id": tool_call.id,
        #                 "role": "tool",  # Indicates this message is from tool use
        #                 "name": function_name,
        #                 "content": json.dumps(function_response, default=str),
        #             }
        #         )
        #     # Make a second API call with the updated conversation
        #     second_response = client.chat.completions.create(
        #         model=MODEL_NAME,
        #         messages=self.history
        #     )
        #     # Return the final response
        #     return second_response.choices[0].message.content
        
