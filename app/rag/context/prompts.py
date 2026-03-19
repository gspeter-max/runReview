"""Prompt templates for contextual retrieval."""

from __future__ import annotations

# The core prompt from Anthropic's Contextual Retrieval approach
CONTEXTUAL_RETRIEVAL_PROMPT = """\
<document>
{document_content}
</document>

Here is the chunk we want to situate within the whole document:

<chunk>
{chunk_content}
</chunk>

Please give a short succinct context to situate this chunk within the overall document \
for the purposes of improving search retrieval of the chunk. The context should:
1. Explain what file/module this is from and its purpose
2. Describe how this chunk relates to the broader codebase
3. Note any key classes, functions, or variables defined or used
4. Mention dependencies or relationships with other parts of the code

Answer only with the succinct context and nothing else."""


CONTEXTUAL_RETRIEVAL_PROMPT_WITH_REPO = """\
<project_mission>
{project_mission}
</project_mission>

<repository_structure>
{repo_structure}
</repository_structure>

<file path="{file_path}">
{document_content}
</file>

Here is a chunk from the above file that we want to situate within the repository context:

<chunk>
{chunk_content}
</chunk>

Please give a short succinct context to situate this chunk within the overall repository \
and file for the purposes of improving search retrieval of the chunk. The context should:
1. State the file path and the purpose of this file in the repository
2. Describe what this specific chunk does (function/class/config purpose)
3. Note relationships to other files or modules if apparent from the repository structure
4. Mention key identifiers (class names, function names, config keys)

Answer only with the succinct context and nothing else."""
