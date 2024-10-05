
from datetime import datetime
import functools
from typing import Dict, List, Tuple
from dataclasses import dataclass 

@dataclass
class Call: 
    parent: int 
    child: int 
    name: str 
    args: str
    result: str | None = None

call_id = 0  # Unique ID for each function call
call_graph: Dict[int, Call] = {}  # Store the call graph

# Decorator to track calls and generate UIDs
def track_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global call_id

        # Assign a new unique ID to this function call
        wrapper.call_id += 1
        current_id = wrapper.call_id

        # Keep track of the parent ID
        parent_id = wrapper.parent_id

        # Show arguments in the call details
        # args_str = f"args={args}, kwargs={kwargs}"
        args_str = ""
        if args:
            formatted_args = [str(arg) for arg in args]
            formatted_args_str = ", ".join(formatted_args)
            args_str += formatted_args_str
        if kwargs: 
            formatted_kwargs = [f"{key}={value}" for key, value in kwargs.items()]
            formatted_kwargs_str = ", ".join(formatted_kwargs)
            args_str += f", {formatted_kwargs_str}"

        print(f"Call {current_id}: {func.__name__}({args_str}) with parent {parent_id}")

        # Store the parent-child relationship in the call graph
        # call_graph[current_id] = (func.__name__, args_str, parent_id)
        call_graph[current_id] = Call(parent=parent_id, child=current_id, name=func.__name__, args=args_str)

        # Set the parent ID for the next recursive call
        wrapper.parent_id = current_id
        try:
            # Execute the wrapped function
            result = func(*args, **kwargs)
            call_graph[current_id].result = result
        finally:
            # Restore the parent ID after returning from the recursive call
            wrapper.parent_id = parent_id

        return result

    wrapper.call_id = 0
    wrapper.parent_id = None  # Root call has no parent
    return wrapper

def get_nodes_edges_as_json() -> Tuple[List[Dict], List[Dict]]:
    nodes = []
    edges = []
    for child_id, call in call_graph.items():
        node = {
            "id": child_id,
            "label": f"{call.name}({call.args})", 
            "data": {
                "name": f"{call.name}({child_id})",
                "type": "Function",
                "status": "Active",
                "description": f"Function call {child_id} with args {call.args}",
                "result": call.result
            }
        }
        nodes.append(node)

        if call.parent is not None:
            edge = {"from": call.parent, "to": child_id}
            edges.append(edge)

    return nodes, edges

def calculate_node_positions(nodes: List[Dict]) -> None:
    """
    Calculate x, y coordinates for the nodes based on hierarchical levels.
    """

    # Constants for node placement
    horizontal_spacing = 300
    vertical_spacing = 180

    # Determine levels and parent-child relationships
    levels = {}
    for node in nodes:
        node_id = node['id']
        call = call_graph[node_id]
        if call.parent is None:
            levels[node_id] = 0  # Root node is at level 0
        else:
            levels[node_id] = levels[call.parent] + 1

    # Group nodes by levels
    nodes_by_level = {}
    for node_id, level in levels.items():
        if level not in nodes_by_level:
            nodes_by_level[level] = []
        nodes_by_level[level].append(node_id)

    # Calculate x, y positions for nodes
    positions = {}
    for level, node_ids in nodes_by_level.items():
        # Calculate x positions for nodes in the current level
        total_width = (len(node_ids) - 1) * horizontal_spacing
        start_x = -total_width // 2

        for index, node_id in enumerate(node_ids):
            x = start_x + index * horizontal_spacing
            y = level * vertical_spacing

            # Assign positions
            positions[node_id] = (x, y)

    # Update the nodes with their positions
    for node in nodes:
        node_id = node['id']
        node['x'], node['y'] = positions[node_id]

def write_to_file():

    nodes, edges = get_nodes_edges_as_json()
    calculate_node_positions(nodes)

    # read the html file and replace the nodes and edges 
    with open("index.html") as f:
        html = f.read()

    html = html.replace("{{ NODES_DATA_PLACEHOLDER }}", str(nodes))
    html = html.replace("{{ EDGES_DATA_PLACEHOLDER }}", str(edges))

    # save the html file with current timestamp 
    filename = f"call_graph_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
    with open(filename, "w") as f:
        f.write(html)

    print("Call graph saved as HTML file.")

    # open the html file in the browser 
    import webbrowser
    webbrowser.open(filename)



