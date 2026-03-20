import tiktoken

def truncate_to_tokens(text: str, max_tokens: int = 4000, model: str = "gpt-4o") -> str:
    """Truncates text to a maximum number of tokens using head and tail truncation."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base for gpt-4o or similar models
        encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    
    half = max_tokens // 2
    head_tokens = tokens[:half]
    tail_tokens = tokens[-half:]
    
    head_text = encoding.decode(head_tokens)
    tail_text = encoding.decode(tail_tokens)
    
    omitted = len(tokens) - len(head_tokens) - len(tail_tokens)
    return f"{head_text}\n\n[...TRUNCATED: {omitted} tokens omitted...]\n\n{tail_text}"

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Counts the number of tokens in a string."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
