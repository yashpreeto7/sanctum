"""
Mega Volume Expansion Module: Distributed Systems Theorems, Browser Internals, Full-Stack Security, and 10 Advanced LeetCode Algorithms.
"""

DISTRIBUTED_THEOREMS = [
    ("14.1 Vector Clocks & Lamport Timestamps — Mathematical Causality",
     "In distributed systems lacking a synchronized physical global clock, we determine causal ordering using logical timestamps.<br/>"
     "• <b>Lamport Timestamps:</b> Every process $P_i$ maintains an integer counter $L_i$. On local event: $L_i = L_i + 1$. On message send: attaches $L_i$. On message receive with timestamp $t$: $L_j = \\max(L_j, t) + 1$. Establishes strict partial ordering ($a \\rightarrow b \\implies L(a) < L(b)$), but $L(a) < L(b)$ does NOT imply $a \\rightarrow b$ (cannot distinguish concurrent events).<br/>"
     "• <b>Vector Clocks:</b> Each node maintains vector $V_i \\in \\mathbb{Z}^N$. On event: $V_i[i] = V_i[i] + 1$. On receive vector $W$: $V_j[k] = \\max(V_j[k], W[k])$ for all $k$, and $V_j[j] = V_j[j] + 1$. <b>Key Theorem:</b> $a \\rightarrow b \\iff V(a) < V(b)$. Enables exact detection of concurrent conflicting writes (used in Amazon Dynamo & Riak)."),

    ("14.2 CAP Theorem vs PACELC Theorem — Real-World Classification",
     "• <b>CAP Theorem (Eric Brewer):</b> A distributed data store can guarantee at most two of: <b>C</b>onsistency (linearizability), <b>A</b>vailability (every non-failing node returns response), <b>P</b>artition Tolerance (survives network drops). Since network partitions are inevitable in real networks, the choice is always between **CP** (e.g. HBase, Spanner) and **AP** (e.g. Cassandra, CouchDB).<br/>"
     "• <b>PACELC Theorem (Daniel Abadi):</b> Extends CAP by analyzing normal non-partitioned operation: If there is a <b>P</b>artition, trade <b>A</b>vailability vs <b>C</b>onsistency; <b>E</b>lse, trade <b>L</b>atency vs <b>C</b>onsistency.<br/>"
     "  - <i>PA/EL (Cassandra, DynamoDB):</i> Prioritizes Availability during partitions and Low Latency during normal operations.<br/>"
     "  - <i>PC/EC (Google Spanner, CockroachDB):</i> Prioritizes Consistency during partitions and Consistency during normal operations.")
]

BROWSER_AND_SECURITY = [
    ("15.1 Browser Critical Rendering Path & 60 FPS Layout Triggers",
     "The browser transforms HTML/CSS/JS into pixels on screen in 5 sequential stages:<br/>"
     "1. <b>DOM Tree Construction:</b> Incremental tokenization of HTML byte stream into Node tree hierarchy.<br/>"
     "2. <b>CSSOM Tree Construction:</b> Parses CSS rules into cascading object model.<br/>"
     "3. <b>Render Tree:</b> Merges visible DOM nodes with CSSOM (elements with `display: none` are omitted).<br/>"
     "4. <b>Layout (Reflow):</b> Calculates exact geometry and pixel coordinates (x, y, width, height) of each box. <i>Triggered by:</i> modifying `width`, `height`, `margin`, `padding`, or querying `offsetHeight`/`getBoundingClientRect()`. Expensive CPU operation.<br/>"
     "5. <b>Paint:</b> Converts render tree boxes into bitmap drawing commands (colors, borders, shadows).<br/>"
     "6. <b>Composite:</b> GPU uploads layers and composites textures. Modifying `transform` and `opacity` bypasses Layout and Paint entirely, executing on GPU for buttery 60 FPS animations."),

    ("15.2 Node.js Event Loop Phases & Microtask Priority",
     "Node.js runs on `libuv` single-threaded event loop traversing 6 distinct phases in order:<br/>"
     "1. <b>Timers Phase:</b> Executes expired `setTimeout()` and `setInterval()` callbacks.<br/>"
     "2. <b>Pending I/O Callbacks Phase:</b> Executes system-level error callbacks (e.g. TCP connection errors).<br/>"
     "3. <b>Idle, Prepare Phase:</b> Internal libuv housekeeping.<br/>"
     "4. <b>Poll Phase:</b> Retrieves new I/O events, executes I/O callbacks (file reads, network requests). Blocks here if queue is empty.<br/>"
     "5. <b>Check Phase:</b> Executes `setImmediate()` callbacks specifically.<br/>"
     "6. <b>Close Callbacks Phase:</b> Executes socket close handlers (`socket.on('close')`).<br/>"
     "• <b>Microtask Queues (Highest Priority):</b> `process.nextTick()` queue followed by `Promise.then()` microtask queue. Microtasks drain immediately after every single synchronous JavaScript operation before the event loop advances to the next phase."),

    ("15.3 Comprehensive Web Application Security Defense Matrix",
     "• <b>XSS (Cross-Site Scripting):</b> Attacker injects malicious JavaScript. Mitigate with Content Security Policy (`Content-Security-Policy: default-src 'self'; script-src 'nonce-...'`), contextual HTML output encoding, and `HttpOnly` cookie flags.<br/>"
     "• <b>CSRF (Cross-Site Request Forgery):</b> Malicious site tricks victim's browser into executing state-changing API request. Mitigate with `SameSite=Lax` or `Strict` cookie attributes, custom request headers (`X-Requested-With`), and anti-CSRF synchronizer tokens.<br/>"
     "• <b>SSRF (Server-Side Request Forgery):</b> Attacker tricks backend into querying internal metadata endpoints (e.g. `http://169.254.169.254/latest/meta-data/`). Mitigate with strict URL allowlists, disabling HTTP redirects, blocking private IP ranges (`10.0.0.0/8`, `127.0.0.0/8`), and requiring IMDSv2 session tokens.<br/>"
     "• <b>SQL Injection:</b> Mitigate exclusively using Parameterized Queries / Prepared Statements (e.g. `SELECT * FROM users WHERE id = $1`). Never use string interpolation in SQL.")
]

MEGA_LEETCODE_10 = [
    ("Problem 15: Longest Increasing Subsequence (Patience Sorting $O(N \\log N)$)",
     "<b>Problem:</b> Given integer array `nums`, return length of longest strictly increasing subsequence.<br/>"
     "<b>Approach:</b> Maintain `tails` array where `tails[i]` stores smallest tail element of all increasing subsequences of length $i+1$. Use binary search (`bisect_left`) to update `tails` in $O(N \\log N)$ time and $O(N)$ space.<br/>"
     "<code>from bisect import bisect_left<br/>"
     "def lengthOfLIS(nums: list[int]) -> int:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;tails = []<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for x in nums:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;idx = bisect_left(tails, x)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if idx == len(tails): tails.append(x)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else: tails[idx] = x<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return len(tails)</code>"),

    ("Problem 16: Number of Connected Components (Disjoint Set Union with Path Compression)",
     "<b>Problem:</b> Given $n$ nodes and array of undirected edges, find number of connected components.<br/>"
     "<b>Approach:</b> Disjoint Set Union (Union-Find) with path compression and union by rank. Processes $E$ edges in near-constant $O(E \\cdot \\alpha(N))$ time.<br/>"
     "<code>class DSU:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def __init__(self, n): self.parent = list(range(n)); self.count = n<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def find(self, i):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self.parent[i] != i: self.parent[i] = self.find(self.parent[i])<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return self.parent[i]<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def union(self, i, j):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;root_i, root_j = self.find(i), self.find(j)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if root_i != root_j:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.parent[root_i] = root_j; self.count -= 1<br/><br/>"
     "def countComponents(n: int, edges: list[list[int]]) -> int:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;dsu = DSU(n)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for u, v in edges: dsu.union(u, v)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return dsu.count</code>"),

    ("Problem 17: Binary Tree Maximum Path Sum",
     "<b>Problem:</b> Given binary tree root, return maximum path sum of any non-empty path.<br/>"
     "<b>Approach:</b> Post-order DFS. At each node, compute max gain from left and right subtrees (ignoring negative gains with `max(0, gain)`). Update global max with `root.val + left_gain + right_gain`. Return `root.val + max(left_gain, right_gain)`. $O(N)$ time, $O(H)$ space.<br/>"
     "<code>def maxPathSum(root) -> int:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;max_sum = float('-inf')<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def dfs(node):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nonlocal max_sum<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not node: return 0<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;l = max(0, dfs(node.left))<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;r = max(0, dfs(node.right))<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_sum = max(max_sum, node.val + l + r)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return node.val + max(l, r)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;dfs(root)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return max_sum</code>"),

    ("Problem 18: Maximum Product Subarray (Kadane's Multiplicative Variant)",
     "<b>Problem:</b> Given integer array `nums`, find contiguous non-empty subarray with largest product.<br/>"
     "<b>Approach:</b> Because multiplying two negative numbers yields a positive number, track both `curr_max` and `curr_min` simultaneously at each position. $O(N)$ time, $O(1)$ space.<br/>"
     "<code>def maxProduct(nums: list[int]) -> int:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;res = max(nums)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;curr_min, curr_max = 1, 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for n in nums:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tmp = curr_max * n<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;curr_max = max(n * curr_max, n * curr_min, n)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;curr_min = min(tmp, n * curr_min, n)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;res = max(res, curr_max)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return res</code>"),

    ("Problem 19: Rotting Oranges (Multi-Source BFS)",
     "<b>Problem:</b> In a 2D grid, return minimum minutes until no fresh oranges remain. If impossible, return -1.<br/>"
     "<b>Approach:</b> Multi-source BFS starting with all rotten orange coordinates in queue. Count fresh oranges. Process level by level, decrementing fresh count in $O(M \\times N)$ time.<br/>"
     "<code>from collections import deque<br/>"
     "def orangesRotting(grid: list[list[int]]) -> int:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;q, fresh = deque(), 0<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;m, n = len(grid), len(grid[0])<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for r in range(m):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for c in range(n):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if grid[r][c] == 2: q.append((r, c))<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;elif grid[r][c] == 1: fresh += 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;mins = 0<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;while q and fresh > 0:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for _ in range(len(q)):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;r, c = q.popleft()<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nr, nc = r + dr, c + dc<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;grid[nr][nc] = 2; fresh -= 1; q.append((nr, nc))<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mins += 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return mins if fresh == 0 else -1</code>"),

    ("Problem 20: Validate Binary Search Tree (Range Propagation)",
     "<b>Problem:</b> Given root of binary tree, determine if it is a valid Binary Search Tree (BST).<br/>"
     "<b>Approach:</b> Recursive validation propagating allowable `(low, high)` range bounds down the tree in $O(N)$ time and $O(H)$ space.<br/>"
     "<code>def isValidBST(root) -> bool:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def validate(node, low=float('-inf'), high=float('inf')):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not node: return True<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not (low < node.val < high): return False<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return validate(node.left, low, node.val) and validate(node.right, node.val, high)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return validate(root)</code>")
]

print("Loaded mega volume expansion module.")
