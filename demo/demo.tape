Output demo/demo.gif
Set FontSize 14
Set Width 120
Set Height 36

# Start server in background
Type "uvicorn memkit.server:app --host 127.0.0.1 --port 8000 &"
Enter
Sleep 3s

# Add three memories
Type "memkit add 'The Eiffel Tower is in Paris, France.'"
Enter
Sleep 1s
Type "memkit add 'Python was created by Guido van Rossum in 1991.'"
Enter
Sleep 1s
Type "memkit add 'ChromaDB stores vectors on the local filesystem.'"
Enter
Sleep 1s

# List all
Type "memkit list"
Enter
Sleep 1s

# Semantic search
Type "memkit search 'where is the Eiffel Tower'"
Enter
Sleep 2s

# Chatbot example (one turn, then Ctrl-C)
Type "ANTHROPIC_API_KEY=sk-... python examples/chatbot.py"
Enter
Sleep 2s
Type "What do you know about Paris?"
Enter
Sleep 4s
Ctrl+C
