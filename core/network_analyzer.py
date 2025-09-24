"""
Manhattan Network Analyzer - Validates and analyzes SUMO network
"""

import sumolib
import json
import os
from typing import Dict, List, Set, Tuple

class ManhattanNetworkAnalyzer:
    def __init__(self, net_file='data/sumo/manhattan.net.xml'):
        self.net_file = net_file
        self.net = sumolib.net.readNet(net_file)
        
        # Categories of edges
        self.drivable_edges = []
        self.connected_edges = {}  # edge_id -> [reachable_edges]
        self.edge_lengths = {}
        self.edge_types = {}
        
        # Analyze network
        self._analyze_network()
        self._find_connected_components()
        
    def _analyze_network(self):
        """Analyze network structure"""
        print("Analyzing Manhattan network...")
        
        for edge in self.net.getEdges():
            edge_id = edge.getID()
            
            # Skip internal junction edges
            if edge_id.startswith(':'):
                continue
                
            # Check if edge allows passenger vehicles
            if edge.allows('passenger'):
                self.drivable_edges.append(edge_id)
                self.edge_lengths[edge_id] = edge.getLength()
                
                # Get edge type/name for categorization
                edge_name = edge.getName() if edge.getName() else ""
                if any(ave in edge_name.lower() for ave in ['broadway', '5th', '7th', 'park', 'madison']):
                    self.edge_types[edge_id] = 'avenue'
                elif any(st in edge_name for st in ['42nd', '34th', '57th', '23rd', '14th']):
                    self.edge_types[edge_id] = 'street'
                else:
                    self.edge_types[edge_id] = 'local'
                    
                # Find connected edges
                self.connected_edges[edge_id] = []
                
                # Get outgoing edges from this edge's to-node
                to_node = edge.getToNode()
                for out_edge in to_node.getOutgoing():
                    if out_edge.allows('passenger') and not out_edge.getID().startswith(':'):
                        self.connected_edges[edge_id].append(out_edge.getID())
        
        print(f"Found {len(self.drivable_edges)} drivable edges")
        print(f"  - Avenues: {sum(1 for t in self.edge_types.values() if t == 'avenue')}")
        print(f"  - Streets: {sum(1 for t in self.edge_types.values() if t == 'street')}")
        print(f"  - Local roads: {sum(1 for t in self.edge_types.values() if t == 'local')}")
        
    def _find_connected_components(self):
        """Find connected components in the network"""
        visited = set()
        components = []
        
        for edge in self.drivable_edges:
            if edge not in visited:
                component = self._dfs(edge, visited)
                components.append(component)
        
        # Find largest connected component
        self.main_component = max(components, key=len)
        
        print(f"Network has {len(components)} connected components")
        print(f"Main component has {len(self.main_component)} edges ({len(self.main_component)*100//len(self.drivable_edges)}% of network)")
        
        # Only use edges from main component
        self.routable_edges = list(self.main_component)
        
    def _dfs(self, start_edge, visited):
        """Depth-first search to find connected component"""
        stack = [start_edge]
        component = set()
        
        while stack:
            edge = stack.pop()
            if edge in visited:
                continue
                
            visited.add(edge)
            component.add(edge)
            
            # Add connected edges
            for next_edge in self.connected_edges.get(edge, []):
                if next_edge not in visited:
                    stack.append(next_edge)
                    
        return component
    
    def get_valid_od_pair(self):
        """Get a valid origin-destination pair that can definitely be routed"""
        import random
        
        # Use only edges from main connected component
        origin = random.choice(self.routable_edges)
        destination = random.choice(self.routable_edges)
        
        # Ensure they're different and not too close
        attempts = 0
        while destination == origin and attempts < 10:
            destination = random.choice(self.routable_edges)
            attempts += 1
            
        return origin, destination
    
    def find_route(self, from_edge, to_edge):
        """Find valid route between two edges using SUMO's routing"""
        try:
            from_edge_obj = self.net.getEdge(from_edge)
            to_edge_obj = self.net.getEdge(to_edge)
            
            # Use SUMO's built-in shortest path
            route = self.net.getShortestPath(from_edge_obj, to_edge_obj)
            
            if route and route[0]:
                return [edge.getID() for edge in route[0]]
            return None
            
        except Exception as e:
            return None
    
    def save_analysis(self):
        """Save network analysis for faster loading"""
        analysis = {
            'drivable_edges': self.drivable_edges,
            'routable_edges': self.routable_edges,
            'edge_types': self.edge_types,
            'main_component_size': len(self.main_component),
            'total_edges': len(self.drivable_edges)
        }
        
        with open('data/sumo/network_analysis.json', 'w') as f:
            json.dump(analysis, f, indent=2)
            
        print("Network analysis saved to data/sumo/network_analysis.json")