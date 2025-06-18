rag_tool = {
    "type": "function",
    "function": {
        "name": "rag_tool",
        "description": (
            "Answer user queries based on the content of uploaded PDF documents, "
            "specifically document prospectuses and fact sheets. "
            "Returns the top 3 most relevant content chunks from the document."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A natural language question related to the uploaded prospectus or fact sheet document, "
                        "such as fees, investment objectives, or risks."
                    ),
                }
            },
            "required": ["query"],
        },
    }
}

Tools_list = [rag_tool]