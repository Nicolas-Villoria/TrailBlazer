"""
Graph service - handles graph creation and manipulation
Port of skeleton/graphmaker.py to web backend
"""
import networkx as nx
from math import acos, degrees
from typing import List, Tuple
import haversine

from models import PointModel
from core.utils import get_logger

logger = get_logger("graph_service")


class GraphService:
    """Service for graph operations"""
    
    @staticmethod
    def make_graph(segments: List[Tuple[PointModel, PointModel]]) -> nx.Graph:
        """
        Create a graph from segments.
        
        Args:
            segments: List of tuples (start_point, end_point)
            
        Returns:
            NetworkX graph with points as nodes and segments as weighted edges
        """
        graph = nx.Graph()
        
        for start_point, end_point in segments:
            # Create hashable tuples for graph nodes
            start_node = (start_point.lat, start_point.lon)
            end_node = (end_point.lat, end_point.lon)
            
            # Calculate edge weight using haversine distance
            weight = haversine.haversine(
                (start_point.lat, start_point.lon),
                (end_point.lat, end_point.lon)
            )
            
            graph.add_edge(start_node, end_node, weight=weight)
        
        logger.info(f"Created graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        return graph
    
    @staticmethod
    def simplify_graph(graph: nx.Graph, epsilon: float = 5.0) -> nx.Graph:
        """
        Simplify the graph by removing collinear nodes.
        
        Eliminates nodes with degree 2 that are nearly collinear with their neighbors.
        This reduces graph complexity while maintaining path accuracy.
        
        Args:
            graph: NetworkX graph to simplify
            epsilon: Maximum angle deviation from 180° to consider collinear (degrees)
            
        Returns:
            Simplified graph
        """
        # Find all nodes with exactly 2 connections
        nodes_degree_2 = [node for node in graph.nodes if graph.degree(node) == 2]
        removed_count = 0
        
        for node in nodes_degree_2:
            # Get the two neighbors
            neighbors = list(graph.adj[node])
            if len(neighbors) != 2:
                continue
                
            g1, g3 = neighbors
            
            # Calculate angle between the three points
            try:
                angle = GraphService._angle_of(g1, node, g3)
                
                # If angle is close to 180° (nearly straight line), remove the middle node
                if abs(180 - angle) < epsilon:
                    graph.remove_edge(g1, node)
                    graph.remove_edge(node, g3)
                    graph.remove_node(node)
                    
                    # Connect the two neighbors directly
                    weight = haversine.haversine(g1, g3)
                    graph.add_edge(g1, g3, weight=weight)
                    removed_count += 1
                    
            except (ValueError, ZeroDivisionError):
                # Skip nodes that cause calculation errors
                continue
        
        logger.info(f"Simplified graph: removed {removed_count} collinear nodes")
        logger.info(f"Final graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        return graph
    
    @staticmethod
    def _angle_of(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
        """
        Calculate the angle at p2 formed by p1-p2-p3 using haversine distances.
        
        Args:
            p1, p2, p3: Points as (lat, lon) tuples
            
        Returns:
            Angle in degrees
        """
        # Calculate distances between points
        d1 = haversine.haversine(p1, p2)
        d2 = haversine.haversine(p2, p3)
        d3 = haversine.haversine(p1, p3)
        
        # Avoid division by zero
        if d1 == 0 or d2 == 0:
            return 180.0
        
        # Use law of cosines to find angle
        # cos(angle) = (d1² + d2² - d3²) / (2 * d1 * d2)
        cos_angle = (d1**2 + d2**2 - d3**2) / (2 * d1 * d2)
        
        # Clamp to [-1, 1] to avoid numerical errors in acos
        cos_angle = max(-1.0, min(1.0, cos_angle))
        
        return degrees(acos(cos_angle))
    
    @staticmethod
    def find_closest_node(graph: nx.Graph, point: PointModel) -> PointModel | None:
        """
        Find the closest graph node to a given point.
        
        Args:
            graph: NetworkX graph
            point: Target point
            
        Returns:
            Closest node as (lat, lon) tuple or None if graph is empty
        """
        min_dist = float("inf")
        closest_node = None
        
        target = (point.lat, point.lon)
        
        for node in graph.nodes:
            dist = haversine.haversine(target, node)
            if dist < min_dist:
                min_dist = dist
                closest_node = node
        
        logger.debug(f"Found closest node at distance {min_dist:.3f} km")
        return closest_node
    
    @staticmethod
    def shortest_path(
        graph: nx.Graph, 
        start: PointModel, 
        end: PointModel,
    ) -> Tuple[float, List[PointModel]]:
        """
        Find shortest path between two nodes using Dijkstra's algorithm.
        
        Args:
            graph: NetworkX graph
            start: Start node (lat, lon)
            end: End node (lat, lon)
            
        Returns:
            Tuple of (total_distance, path_nodes)
            
        Raises:
            nx.NetworkXNoPath: If no path exists between start and end
        """
        distance, path = nx.single_source_dijkstra(graph, start, end, weight="weight")
        logger.debug(f"Found path of length {distance:.3f} km with {len(path)} nodes")
        return distance, path
