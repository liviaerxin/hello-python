"""
Dynamic Programming,

Find the longest string between two strings.

I have this book to read
   i
You have this book to write
     j

      x b c     `s2`
  [[0,0,0,0],
a  [0,0,0,0],
b  [0,0,1,0],
c  [0,0,0,2]]

`s1`

key: dp[i][j] = dp[i-1][j-1] + 1 "diag + 1" if dp[i] == dp[j]
"""


def find_longest_substring(s1: str, s2: str) -> str:
    n = len(s1) + 1
    m = len(s2) + 1
    dp = [[0] * m for _ in range(n)]
    max_len = 0
    for i in range(1, n):
        for j in range(1, m):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_len:
                    max_len = dp[i][j]
                    end = i
    return s1[end - max_len : end]


s1 = "abc"
s2 = "xbc"
s1 = "I have this book to read"
s2 = "You have this book to write"
print(find_longest_substring(s1, s2))
