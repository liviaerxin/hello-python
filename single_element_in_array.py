# [Single Number II](https://leetcode.com/problems/single-number-ii)

"""
define the bitwise operation (6 conditions in total):
ones        0   0   0   0   1   1
twos        0   1   1   0   0   0
number      0   1   0   1   0   1
-results->
ones:       0   0   0   1   1   0
twos:       0   0   1   0   0   1
"""

def singleNumber(self, nums: list[int]) -> int:
    ones = 0
    twos = 0
    for num in nums:
        ones = (ones ^ num) & (~twos)
        twos = (twos ^ num) & (~ones)

    return ones

singleNumber([2, 2, 3, 2])

singleNumber([0,1,0,1,0,1,99])