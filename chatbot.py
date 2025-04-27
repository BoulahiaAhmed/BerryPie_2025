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
        system_prompt = f"""You are BerryPie, a helpful and friendly virtual assistant. 
You specialize in answering questions about video content provided by the user.
The video transcript is as follows:
\"\"\"
{self.transcript}
\"\"\"
Always base your answers on the transcript above. If the answer is not in the transcript, politely say you don't know."""
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
