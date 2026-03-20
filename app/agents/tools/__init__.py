from app.agents.tools.registry import global_registry
from app.agents.tools.retrieve import get_retrieve_schema, execute_retrieve
from app.agents.tools.read import get_read_file_schema, execute_read_file
from app.agents.tools.explorer import get_list_directory_schema, execute_list_directory

# Register tools
global_registry.register("search_codebase", get_retrieve_schema(), execute_retrieve)
global_registry.register("read_file", get_read_file_schema(), execute_read_file)
global_registry.register("list_directory", get_list_directory_schema(), execute_list_directory)
