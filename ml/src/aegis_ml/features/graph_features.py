"""Entity Graph & Graph Feature Computation Engine using NetworkX.
Computes connected component size, shortest path to known fraud, 
and PageRank propagated risk scores, cached to Redis.
"""
from __future__ import annotations
import json
from typing import List, Dict, Any, Optional
import networkx as nx

class EntityGraphEngine:
    """Builds multi-entity graph and computes per-entity graph risk features."""

    def __init__(self):
        self.graph = nx.Graph()

    def add_edge(self, src_type: str, src_id: str, dst_type: str, dst_id: str, weight: float = 1.0):
        """Add undirected edge between entities in the graph."""
        src_node = f"{src_type}:{src_id}"
        dst_node = f"{dst_type}:{dst_id}"
        self.graph.add_edge(src_node, dst_node, weight=weight)

    def build_from_edge_records(self, edges: List[Dict[str, Any]]):
        """Build NetworkX graph from edge list records."""
        for edge in edges:
            self.add_edge(
                edge["src_type"], str(edge["src_id"]),
                edge["dst_type"], str(edge["dst_id"]),
                float(edge.get("weight", 1.0))
            )

    def compute_component_size(self, entity_type: str, entity_id: str) -> int:
        """Compute connected component size for a given entity."""
        node = f"{entity_type}:{entity_id}"
        if node not in self.graph:
            return 1
        comp = nx.node_connected_component(self.graph, node)
        return len(comp)

    def compute_shortest_path_to_fraud(
        self,
        entity_type: str,
        entity_id: str,
        fraud_nodes: List[str]
    ) -> int:
        """Compute shortest path distance to nearest known fraud node (-1 if unreachable)."""
        node = f"{entity_type}:{entity_id}"
        if node not in self.graph or not fraud_nodes:
            return -1

        min_dist = float('inf')
        for f_node in fraud_nodes:
            if f_node in self.graph and nx.has_path(self.graph, node, f_node):
                length = nx.shortest_path_length(self.graph, node, f_node)
                if length < min_dist:
                    min_dist = length

        return int(min_dist) if min_dist != float('inf') else -1

    def compute_pagerank(self) -> Dict[str, float]:
        """Compute PageRank risk propagation score for all graph nodes."""
        if len(self.graph) == 0:
            return {}
        return nx.pagerank(self.graph, alpha=0.85)

    def cache_graph_features_to_redis(
        self,
        redis_client,
        fraud_entity_ids: List[str] = None
    ) -> int:
        """Cache computed graph features to Redis under gfeat:acct:{id} keys."""
        if fraud_entity_ids is None:
            fraud_entity_ids = []
        fraud_nodes = [f"account:{f_id}" for f_id in fraud_entity_ids]

        pagerank_scores = self.compute_pagerank()
        count = 0

        for node in self.graph.nodes():
            if node.startswith("account:"):
                acct_id = node.split("account:")[1]
                comp_size = self.compute_component_size("account", acct_id)
                dist_fraud = self.compute_shortest_path_to_fraud("account", acct_id, fraud_nodes)
                pr_score = round(pagerank_scores.get(node, 0.0), 6)

                payload = {
                    "component_size": comp_size,
                    "dist_to_fraud": dist_fraud,
                    "pagerank_score": pr_score
                }
                redis_key = f"gfeat:acct:{acct_id}"
                if redis_client:
                    redis_client.set(redis_key, json.dumps(payload))
                count += 1

        print(f"[+] Cached graph features to Redis for {count} accounts")
        return count
