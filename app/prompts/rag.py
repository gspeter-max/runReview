"""
Prompts for the RAG (Retrieval-Augmented Generation) components.
"""

CONTEXT_GENERATION_SYSTEM_PROMPT = """You are an expert programmer. Provide a concise, one-sentence context for the following code chunk to help with retrieval."""

RERANK_SYSTEM_PROMPT = """You are a technical judge ranking code relevance to a search query. Return only a JSON list of numbers."""

RERANK_PROMPT = """\
Given the following search query and code chunks, rate each chunk's relevance \
to the query on a scale of 0-10. Return only a JSON array of scores in the same \
order as the chunks.

Query: {query}

Chunks:
{chunks}

Return a JSON array of numeric scores, e.g. [8, 3, 7, ...]. Nothing else."""
