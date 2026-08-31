"""
20 High-Frequency LeetCode Problem Solutions & 5 Additional System Design Case Studies.
"""

LEETCODE_20 = [
    ("Problem 1: LRU Cache (Design)",
     "<b>Problem:</b> Design a data structure that follows the constraints of a Least Recently Used (LRU) cache with $O(1)$ `get` and `put`.<br/>"
     "<b>Approach:</b> Combine a Hash Map (for $O(1)$ key lookup) with a Doubly Linked List (for $O(1)$ node removal and insertion at head). Dummy head and tail nodes simplify edge cases.<br/>"
     "<code>class Node:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def __init__(self, k=0, v=0): self.k, self.v = k, v; self.prev = self.next = None<br/><br/>"
     "class LRUCache:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def __init__(self, cap: int):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.cap, self.map = cap, {}<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.head, self.tail = Node(), Node()<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.head.next, self.tail.prev = self.tail, self.head<br/><br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def _remove(self, n): n.prev.next, n.next.prev = n.next, n.prev<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def _add_head(self, n):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;n.next, n.prev = self.head.next, self.head<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.head.next.prev = self.head.next = n<br/><br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def get(self, k: int) -> int:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if k not in self.map: return -1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;n = self.map[k]; self._remove(n); self._add_head(n)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return n.v<br/><br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def put(self, k: int, v: int):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if k in self.map: self._remove(self.map[k])<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;n = Node(k, v); self.map[k] = n; self._add_head(n)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(self.map) > self.cap:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lru = self.tail.prev; self._remove(lru); del self.map[lru.k]</code>"),

    ("Problem 2: Course Schedule II (Topological Sort / Kahn's BFS)",
     "<b>Problem:</b> Given `numCourses` and `prerequisites` pairs `[a, b]`, return the ordering of courses you should take to finish all courses. If impossible, return `[]`.<br/>"
     "<b>Approach:</b> Build in-degree array and adjacency list. Add 0-in-degree nodes to queue. Process nodes, decrementing neighbors' in-degrees. If order length equals `numCourses`, valid DAG exists.<br/>"
     "<code>from collections import deque<br/>"
     "def findOrder(numCourses: int, prerequisites: list[list[int]]) -> list[int]:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;adj = {i: [] for i in range(numCourses)}<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;in_deg = [0] * numCourses<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for dest, src in prerequisites:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;adj[src].append(dest); in_deg[dest] += 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;q = deque([i for i in range(numCourses) if in_deg[i] == 0])<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;order = []<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;while q:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;u = q.popleft(); order.append(u)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for v in adj[u]:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;in_deg[v] -= 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if in_deg[v] == 0: q.append(v)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return order if len(order) == numCourses else []</code>"),

    ("Problem 3: Trapping Rain Water (Two Pointers)",
     "<b>Problem:</b> Given `height` array representing elevation map, compute how much water it can trap after raining.<br/>"
     "<b>Approach:</b> Two pointers with `left_max` and `right_max`. Move the pointer with smaller max inward, adding `max - height[ptr]` to total trapped water in $O(N)$ time and $O(1)$ space.<br/>"
     "<code>def trap(height: list[int]) -> int:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;if not height: return 0<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;l, r = 0, len(height) - 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;l_max, r_max, water = height[l], height[r], 0<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;while l < r:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if l_max < r_max:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;l += 1; l_max = max(l_max, height[l]); water += l_max - height[l]<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;r -= 1; r_max = max(r_max, height[r]); water += r_max - height[r]<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return water</code>"),

    ("Problem 4: Merge K Sorted Lists (Min-Heap Priority Queue)",
     "<b>Problem:</b> Merge $k$ sorted linked lists and return it as one sorted list.<br/>"
     "<b>Approach:</b> Push `(node.val, i, node)` tuples of list heads into Min-Heap. Pop smallest, attach to merged list, and push `node.next` in $O(N \\log K)$ time.<br/>"
     "<code>import heapq<br/>"
     "def mergeKLists(lists):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;heap = []<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for i, l in enumerate(lists):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if l: heapq.heappush(heap, (l.val, i, l))<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;dummy = curr = ListNode(0)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;while heap:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;val, i, node = heapq.heappop(heap)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;curr.next = node; curr = curr.next<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if node.next: heapq.heappush(heap, (node.next.val, i, node.next))<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return dummy.next</code>"),

    ("Problem 5: Subarray Sum Equals K (Prefix Sums + Hash Map)",
     "<b>Problem:</b> Find total number of continuous subarrays whose sum equals to $k$.<br/>"
     "<b>Approach:</b> Maintain running prefix sum `curr_sum`. Check if `curr_sum - k` exists in hash map of previous prefix sum frequencies. $O(N)$ time and $O(N)$ space.<br/>"
     "<code>def subarraySum(nums: list[int], k: int) -> int:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;count, curr_sum = 0, 0<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;prefix_counts = {0: 1}<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for x in nums:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;curr_sum += x<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;count += prefix_counts.get(curr_sum - k, 0)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prefix_counts[curr_sum] = prefix_counts.get(curr_sum, 0) + 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return count</code>"),

    ("Problem 6: Lowest Common Ancestor in Binary Tree",
     "<b>Problem:</b> Given a binary tree and two nodes $p$ and $q$, find their lowest common ancestor (LCA).<br/>"
     "<b>Approach:</b> Recursive post-order traversal. If current root is null, $p$, or $q$, return root. Search left and right subtrees; if both non-null, current root is LCA.<br/>"
     "<code>def lowestCommonAncestor(root, p, q):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;if not root or root == p or root == q: return root<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;left = lowestCommonAncestor(root.left, p, q)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;right = lowestCommonAncestor(root.right, p, q)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;if left and right: return root<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return left if left else right</code>"),

    ("Problem 7: Coin Change (1D Bottom-Up Dynamic Programming)",
     "<b>Problem:</b> Return fewest number of coins needed to make up amount $A$ using given coin denominations.<br/>"
     "<b>Approach:</b> `dp[i]` stores min coins for amount `i`. Iterate `dp[i] = min(dp[i], dp[i - coin] + 1)` in $O(\\text{amount} \\times \\text{len}(coins))$ time.<br/>"
     "<code>def coinChange(coins: list[int], amount: int) -> int:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;dp = [float('inf')] * (amount + 1)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;dp[0] = 0<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for c in coins:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for i in range(c, amount + 1):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dp[i] = min(dp[i], dp[i - c] + 1)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return dp[amount] if dp[amount] != float('inf') else -1</code>"),

    ("Problem 8: Longest Consecutive Sequence (Hash Set)",
     "<b>Problem:</b> Given an unsorted array of integers, find length of longest consecutive elements sequence in $O(N)$ time.<br/>"
     "<b>Approach:</b> Insert all numbers into a Hash Set. Only start counting sequence from numbers that are sequence starts (where `num - 1 not in set`).<br/>"
     "<code>def longestConsecutive(nums: list[int]) -> int:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;num_set = set(nums)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;longest = 0<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for x in num_set:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if x - 1 not in num_set:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;curr, length = x, 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;while curr + 1 in num_set:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;curr += 1; length += 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;longest = max(longest, length)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return longest</code>")
]

EXTRA_CASE_STUDIES = [
    ("Case Study 6: Designing a Distributed Web Crawler (e.g. Googlebot)",
     "<b>Requirements:</b> Crawl billions of web pages monthly, adhere strictly to `robots.txt`, parse HTML hyperlinks, avoid infinite loops.<br/>"
     "<b>Architecture:</b><br/>"
     "1. <b>URL Frontier:</b> Priority queues (Host Queue & Priority Queue) ensuring politeness (delay between requests to same host).<br/>"
     "2. <b>Deduplication:</b> Distributed Bloom Filters on Redis cluster to check URL seen status in $O(1)$ memory; Document checksums (SimHash) to eliminate duplicate HTML content.<br/>"
     "3. <b>DNS Resolver:</b> Local in-memory DNS caching cluster to avoid bottlenecks on external DNS queries.<br/>"
     "4. <b>Storage:</b> Raw HTML stored in S3/HDFS; link graph stored in distributed graph DB (Neo4j / Cassandra)."),

    ("Case Study 7: Designing a Video Streaming Platform (e.g. YouTube / Netflix)",
     "<b>Requirements:</b> Upload 4K videos, transcode to multiple resolutions (1080p, 720p, 480p), adaptive bitrate streaming with <1s buffering.<br/>"
     "<b>Architecture:</b><br/>"
     "1. <b>Upload & Chunking:</b> Multipart direct upload to S3; S3 Event triggers Kafka message.<br/>"
     "2. <b>Transcoding DAG:</b> Apache Spark / FFMPEG cluster splits video into 5-second chunk segments (`.ts`) and creates HLS / MPEG-DASH manifest files (`.m3u8`).<br/>"
     "3. <b>CDN Distribution:</b> Geo-distributed CDN edge servers (Cloudflare/CloudFront) cache top 20% most-watched video segments locally, providing sub-20ms streaming latency.")
]

print("Loaded extra leetcode and system design modules.")
