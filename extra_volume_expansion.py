"""
Volume expansion module: 12 More LeetCode Problems, Production Post-Mortem & DevOps/Cloud Architecture.
"""

EXTRA_LEETCODE_12 = [
    ("Problem 9: Median from Data Stream (Two Heaps: Max-Heap & Min-Heap)",
     "<b>Problem:</b> Design a data structure that supports adding integers from a data stream and finding the median in $O(1)$ time.<br/>"
     "<b>Approach:</b> Maintain a Max-Heap `small` (storing smaller half of numbers) and a Min-Heap `large` (storing larger half). Balance sizes so that `len(small) == len(large)` or `len(small) == len(large) + 1`. Time: $O(\\log N)$ add, $O(1)$ find median.<br/>"
     "<code>import heapq<br/>"
     "class MedianFinder:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def __init__(self): self.small, self.large = [], []  # small is max-heap (negated)<br/><br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def addNum(self, num: int):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;heapq.heappush(self.small, -num)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self.small and self.large and (-self.small[0] > self.large[0]):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;val = -heapq.heappop(self.small)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;heapq.heappush(self.large, val)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(self.small) > len(self.large) + 1:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;heapq.heappush(self.large, -heapq.heappop(self.small))<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;elif len(self.large) > len(self.small):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;heapq.heappush(self.small, -heapq.heappop(self.large))<br/><br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;def findMedian(self) -> float:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(self.small) > len(self.large): return float(-self.small[0])<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return (-self.small[0] + self.large[0]) / 2.0</code>"),

    ("Problem 10: Minimum Window Substring (Sliding Window with Hash Map)",
     "<b>Problem:</b> Given two strings $s$ and $t$, return minimum window substring of $s$ containing all characters in $t$.<br/>"
     "<b>Approach:</b> Sliding window tracking character counts. Expand right until valid (`have == need`), then shrink left to find minimum valid substring in $O(N)$ time.<br/>"
     "<code>from collections import Counter<br/>"
     "def minWindow(s: str, t: str) -> str:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;if not t or not s: return ''<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;t_count, window = Counter(t), {}<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;have, need = 0, len(t_count)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;res, res_len = [-1, -1], float('inf')<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;l = 0<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for r, char in enumerate(s):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;window[char] = window.get(char, 0) + 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if char in t_count and window[char] == t_count[char]: have += 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;while have == need:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if (r - l + 1) < res_len:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;res = [l, r]; res_len = r - l + 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;window[s[l]] -= 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if s[l] in t_count and window[s[l]] < t_count[s[l]]: have -= 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;l += 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;l, r = res<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return s[l:r+1] if res_len != float('inf') else ''</code>"),

    ("Problem 11: Top K Frequent Elements (Bucket Sort $O(N)$)",
     "<b>Problem:</b> Given an integer array `nums` and integer $k$, return the $k$ most frequent elements in $O(N)$ time.<br/>"
     "<b>Approach:</b> Frequency counter + Array of buckets where index represents frequency. Iterate backwards from highest frequency bucket.<br/>"
     "<code>from collections import Counter<br/>"
     "def topKFrequent(nums: list[int], k: int) -> list[int]:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;count = Counter(nums)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;buckets = [[] for _ in range(len(nums) + 1)]<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for n, c in count.items(): buckets[c].append(n)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;res = []<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for i in range(len(buckets) - 1, 0, -1):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for n in buckets[i]:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;res.append(n)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if len(res) == k: return res<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return res</code>"),

    ("Problem 12: Longest Common Subsequence (2D Dynamic Programming)",
     "<b>Problem:</b> Given two strings `text1` and `text2`, return length of their longest common subsequence.<br/>"
     "<b>Approach:</b> `dp[i][j]` represents LCS of `text1[0..i]` and `text2[0..j]`. If chars match, `dp[i][j] = 1 + dp[i-1][j-1]`; else `max(dp[i-1][j], dp[i][j-1])`. Time $O(M \\times N)$, Space $O(M \\times N)$.<br/>"
     "<code>def longestCommonSubsequence(text1: str, text2: str) -> int:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;m, n = len(text1), len(text2)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;dp = [[0] * (n + 1) for _ in range(m + 1)]<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for i in range(1, m + 1):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for j in range(1, n + 1):<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if text1[i-1] == text2[j-1]: dp[i][j] = 1 + dp[i-1][j-1]<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else: dp[i][j] = max(dp[i-1][j], dp[i][j-1])<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return dp[m][n]</code>"),

    ("Problem 13: Merge Intervals",
     "<b>Problem:</b> Given an array of `intervals`, merge all overlapping intervals.<br/>"
     "<b>Approach:</b> Sort intervals by `start` time. Iterate and merge with previous interval if `curr.start <= prev.end`. $O(N \\log N)$ time, $O(N)$ space.<br/>"
     "<code>def merge(intervals: list[list[int]]) -> list[list[int]]:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;intervals.sort(key=lambda x: x[0])<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;merged = []<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;for interval in intervals:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not merged or merged[-1][1] < interval[0]: merged.append(interval)<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else: merged[-1][1] = max(merged[-1][1], interval[1])<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return merged</code>"),

    ("Problem 14: Search in Rotated Sorted Array",
     "<b>Problem:</b> Search for `target` in a rotated sorted array in $O(\\log N)$ time.<br/>"
     "<b>Approach:</b> Modified binary search. Determine whether left half `[l..mid]` or right half `[mid..r]` is sorted, and check if `target` lies within the sorted half.<br/>"
     "<code>def search(nums: list[int], target: int) -> int:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;l, r = 0, len(nums) - 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;while l <= r:<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;mid = (l + r) // 2<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if nums[mid] == target: return mid<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if nums[l] <= nums[mid]:  # Left half sorted<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if nums[l] <= target < nums[mid]: r = mid - 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else: l = mid + 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:  # Right half sorted<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if nums[mid] < target <= nums[r]: l = mid + 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else: r = mid - 1<br/>"
     "&nbsp;&nbsp;&nbsp;&nbsp;return -1</code>")
]

DEVOPS_AND_ARCHITECTURE = [
    ("13.1 Production Post-Mortem & Blameless Root Cause Analysis (RCA) Framework",
     "When production outages occur, engineering teams must conduct blameless RCAs.<br/>"
     "• <b>The 5 Whys Methodology:</b> Drill down past superficial symptoms to systemic engineering root causes.<br/>"
     "• <b>Post-Mortem Document Structure:</b><br/>"
     "  1. <i>Incident Summary:</i> Duration, customer impact (e.g. 2.4% error rate on checkout for 18 mins), Sev Level (Sev-1).<br/>"
     "  2. <i>Timeline:</i> Detailed UTC timestamp breakdown from initial alert trigger to rollback and mitigation.<br/>"
     "  3. <i>Root Cause:</i> Deep technical explanation of the failure mode (e.g. unindexed query causing DB connection pool exhaustion).<br/>"
     "  4. <i>Action Items:</i> Direct JIRA tickets categorized as P0 (Prevent Immediate Recurrence) and P1 (Improve Observability)."),

    ("13.2 Modern CI/CD Pipelines & Zero-Downtime Deployment Strategies",
     "• <b>Blue-Green Deployment:</b> Maintain two identical production environments (Blue = Active, Green = Staging). Deploy new version to Green, run smoke tests, and switch router/load balancer traffic instantly. Fast rollback.<br/>"
     "• <b>Canary Releases:</b> Route 2% of user traffic to new version; monitor error rates and latency in Prometheus/Datadog; incrementally ramp up to 10%, 50%, 100%.<br/>"
     "• <b>Database Migration Safety:</b> Never deploy destructive DB schema changes in one step. Follow the <b>Expand and Contract (Parallel Run)</b> pattern: (1) Add new column/table; (2) Dual-write to both old and new schema; (3) Backfill historical data; (4) Switch reads to new schema; (5) Deprecate and drop old schema."),

    ("13.3 Containerization & Kubernetes Architecture (Pods, ReplicaSets, Services, Ingress)",
     "• <b>Linux Containers (Cgroups & Namespaces):</b> Containers are not VMs. They are isolated Linux processes utilizing <b>Namespaces</b> (PID, Mount, Net, IPC isolation) and <b>Cgroups</b> (CPU, Memory resource limits).<br/>"
     "• <b>Kubernetes Core Architecture:</b><br/>"
     "  • <i>Control Plane:</i> `kube-apiserver` (REST gateway), `etcd` (distributed key-value store for cluster state), `kube-scheduler` (assigns pods to nodes), `kube-controller-manager` (reconciles desired vs actual state).<br/>"
     "  • <i>Worker Nodes:</i> `kubelet` (ensures containers are running in Pods), `kube-proxy` (maintains network iptables rules), Container Runtime (containerd).<br/>"
     "  • <i>Networking:</i> ClusterIP (internal), NodePort (exposes on host port), Ingress (Layer 7 routing with TLS termination).")
]

print("Loaded volume expansion module.")
