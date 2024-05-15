from anytree import Node, RenderTree
import json


def convert_to_numerical_labels(data, current_level=0, label=''):
    labels = {}
    for key, value in data.items():
        current_label = label + f'{key}/'
        labels[current_label[:-1]] = current_level
        if isinstance(value, dict):
            labels.update(convert_to_numerical_labels(value, current_level + 1, current_label))
    return labels
def create_nodes(data):
    root = Node("source")
    nodes = {"source": root}
    
    for key, value in data.items():
        if "/" in key:
            parent_key, node_name = key.rsplit("/", 1)
            parent_node = nodes[parent_key]
            node = Node(node_name, parent=parent_node)
            nodes[key] = node
        else:
            node = Node(key, parent=root)
            nodes[key] = node

    
    return root
def write_tree_to_file(root, filename):
    with open(filename, "w") as file:
        for pre, _, node in RenderTree(root):
            file.write("%s%s\n" % (pre, node.name))

if __name__ == "__main__":
    with open('nested_dictionary.json', 'r') as file:
        data = json.load(file)

    # Convert to numerical labels
    numerical_labels = convert_to_numerical_labels(data)


    # Function to create nodes from hierarchical data
    data1 = dict(numerical_labels)
    # Create nodes
    root = create_nodes(data1)

    # # Render the tree
    # for pre, _, node in RenderTree(root):
    #     print("%s%s" % (pre, node.name))

    write_tree_to_file(root, "hierarchical_flow.txt")
