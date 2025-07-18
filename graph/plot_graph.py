import networkx as nx

import matplotlib.pyplot as plt

from graph.generate_graph import generate_graph


def plot_graph(db_uri, output_file="graph.png", *, graph=None):
	if graph is None:
		graph = generate_graph(db_uri)

	# Draw the graph
	pos = nx.spring_layout(
		graph,
		scale=2,
		k=0.4
	)  # Position the nodes
	colors = [
		data['color']
		for _, data in graph.nodes(data=True)
	]  # Extract node colors
	labels = nx.get_node_attributes(graph, 'label')  # Extract labels

	# Draw nodes, edges, and labels
	nx.draw(
		graph,
		pos,
		node_color=colors,
		with_labels=True,
		labels=labels,
		node_size=5000,
		font_size=8,
		font_color="white",
	)
	nx.draw_networkx_edge_labels(
		graph,
		pos,
		edge_labels={
			(u, v): "" for u, v in graph.edges
		},
		font_size=8,
	)

	plt.title("Database Graph")
	plt.savefig(output_file)
	plt.show()
