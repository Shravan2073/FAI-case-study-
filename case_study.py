"""
NetPilot - simple single-file simulation
A packet agent finds the fastest route across a network of routers.
Two search algorithms are compared: A* and Greedy Best-First Search (GBFS).
Run: python simple_simulation.py
"""
import heapq
import math

# ---------------------------------------------------------------------
# 1. THE NETWORK (environment)
# ---------------------------------------------------------------------
# Each router has a position (used only to estimate distance to the goal)
positions = {
    "S": (0, 5), "D": (10, 5),
    "R1": (2, 8), "R2": (2, 5), "R3": (2, 2),
    "R4": (5, 8), "R5": (5, 5), "R6": (5, 2),
    "R7": (8, 8), "R8": (8, 5), "R9": (8, 2),
}

# Each link has a delay (cost). Links are two-way.
edges = [
    ("S", "R1", 4), ("S", "R2", 2), ("S", "R3", 4),
    ("R1", "R2", 3), ("R2", "R3", 3),
    ("R1", "R4", 3), ("R2", "R5", 9), ("R3", "R6", 4),
    ("R4", "R5", 3), ("R5", "R6", 3),
    ("R4", "R7", 3), ("R5", "R8", 10), ("R6", "R9", 4),
    ("R7", "R8", 3), ("R8", "R9", 3),
    ("R7", "D", 4), ("R8", "D", 2), ("R9", "D", 4),
]

graph = {r: {} for r in positions}          # graph["R1"]["R2"] = delay
for u, v, w in edges:
    graph[u][v] = w
    graph[v][u] = w


def straight_line_distance(a, b):
    """Heuristic h(n): straight-line distance to the goal. Never overestimates
    the real path cost, so it is admissible -> A* stays optimal."""
    (x1, y1), (x2, y2) = positions[a], positions[b]
    return math.hypot(x1 - x2, y1 - y2)


# ---------------------------------------------------------------------
# 2. THE SEARCH (A* and GBFS are the same algorithm with a different
#    priority rule)
# ---------------------------------------------------------------------
def search(start, goal, use_astar=True):
    """Returns (path, total_cost, list_of_expanded_routers)."""
    g_cost = {start: 0}                       # cost from start so far
    parent = {start: None}
    frontier = [(straight_line_distance(start, goal), start)]
    visited = set()
    expanded_order = []

    while frontier:
        priority, node = heapq.heappop(frontier)
        if node in visited:
            continue
        visited.add(node)
        expanded_order.append(node)

        if node == goal:                       # goal reached: rebuild path
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            return path, g_cost[goal], expanded_order

        for neighbour, delay in graph[node].items():
            if neighbour in visited:
                continue
            new_g = g_cost[node] + delay
            if use_astar:
                # A*: f(n) = cost so far + estimated cost to go
                is_better = new_g < g_cost.get(neighbour, float("inf"))
                priority = new_g + straight_line_distance(neighbour, goal)
            else:
                # GBFS: priority = estimated cost to go ONLY (ignores g)
                is_better = neighbour not in g_cost
                priority = straight_line_distance(neighbour, goal)

            if is_better:
                g_cost[neighbour] = new_g
                parent[neighbour] = node
                heapq.heappush(frontier, (priority, neighbour))

    return None, float("inf"), expanded_order   # no path exists


# ---------------------------------------------------------------------
# 3. DEMO CASES
# ---------------------------------------------------------------------
def show(label, path, cost, expanded):
    route = " -> ".join(path) if path else "NO ROUTE FOUND"
    print(f"{label}")
    print(f"  path   : {route}")
    print(f"  cost   : {cost}")
    print(f"  expanded ({len(expanded)}): {expanded}\n")


if __name__ == "__main__":
    print("=== Working case 1: normal network ===")
    path, cost, expanded = search("S", "D", use_astar=True)
    show("A*", path, cost, expanded)
    path, cost, expanded = search("S", "D", use_astar=False)
    show("GBFS", path, cost, expanded)

    print("=== Edge case: a link fails, agent must re-route ===")
    del graph["R4"]["R7"]
    del graph["R7"]["R4"]
    path, cost, expanded = search("R4", "D", use_astar=True)   # replanning from R4
    show("A* after R4-R7 fails", path, cost, expanded)

    print("=== Edge case: destination unreachable ===")
    for r in ("R7", "R8", "R9"):
        del graph[r]["D"]
        del graph["D"][r]
    path, cost, expanded = search("S", "D", use_astar=True)
    show("A* with D cut off", path, cost, expanded)