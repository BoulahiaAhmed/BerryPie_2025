from groq import Groq

# Initialize the Groq client (no need to manually pass API key if set in env variable GROQ_API_KEY)
client = Groq()

MODEL_NAME = "llama-3.3-70b-versatile"


class BerryPieChatbot:
    def __init__(self, transcript: str):
        self.transcript = transcript
        self.history = []
        self._initialize_system_message()

    def _initialize_system_message(self):
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

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=self.history,
            temperature=0.2,
            max_tokens=1024,
            top_p=1,
            stream=False  # Not streaming inside the function, returning full reply at once
        )

        assistant_reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply
