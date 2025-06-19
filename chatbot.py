import json
import os
from groq import Groq



# Initialize the Groq client (no need to manually pass API key if set in env variable GROQ_API_KEY)
client = Groq()

MODEL_NAME = "llama-3.3-70b-versatile"


class BerryPieChatbot:
    def __init__(self, transcript: str, doc_content: str):
        self.transcript = transcript
        self.doc_content = doc_content
        self.history = []
        self._initialize_system_message()

    def _initialize_system_message(self):
        doc_content_note = (
            f"""In addition, you are equipped with a the content of a document,
            the documents are prospectuses and fact sheets.
            If the transcript does not contain the answer, and these documents are available,
            use the provided context to answer the user’s query.
            Make sure to stay helpful, clear, and professional when responding based on this document content.
            The context provided is:
            \"\"\"
            {self.doc_content}
            \"\"\"
            If the document content is not available, inform the user politely that you don't have enough information to answer."""
        ) if self.doc_content else ""

        if self.transcript:
            system_prompt = f"""
            You are a helpful and friendly virtual assistant for BerryPie, a company specializing in financial products. 
            Your role is to help users understand and ask questions about financial solutions discussed in video content.

            The video transcript provided is:
            \"\"\"
            {self.transcript}
            \"\"\"

            Always base your answers strictly on the information from the transcript.

            If the answer cannot be found in the transcript, politely inform the user that you don't have enough information to answer.

            {doc_content_note}

            Maintain a friendly, professional, and supportive tone at all times.
            """
        else:
            system_prompt = """
            You are a helpful and friendly virtual assistant for BerryPie, a company specializing in financial products. 
            At the moment, there is no financial product available for discussion because no video transcript was provided.
            Kindly inform the user of this in a friendly, professional manner.
            """

        self.history.append({"role": "system", "content": system_prompt})

    def chat(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})

        # Make the initial API call to Groq
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=self.history,
            # tools=Tools_list,  # if self.vectordb else None,
            # tool_choice="auto",  # if self.vectordb else None,
            temperature=0.2,
            max_tokens=1024,
            top_p=1,
            stream=False  # Not streaming inside the function, returning full reply at once
        )

        response_message = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": assistant_reply})

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
        
