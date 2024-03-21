"""
Heap can be efficiently used to access minimum element on O(1) along with pop and push an element on O(log n).

In heap, the items are represented in an array, making it efficient in memory.

- get_root(): Fast access to maximum/minimum element (O(1)) 
- pop(): Pop and return the smallest item(root) from the heap on (O(log n))
- push(): Push the item onto the heap on (O(log n))

"""
class HeapMin:
    # 0-base index
    def __init__(self):
        self.h = []

    def parent(self, i):
        return (i - 1) // 2

    def l_child(self, i):
        return i * 2 + 1
    
    def r_child(self, i):
        return i * 2 + 2

    def get_root(self):
        if not self.h:
            return None
        else:
            return self.h[0]
        
    def pop(self):
        if not self.h:
            return None
            
        root = self.h[0]
        
        size = len(self.h)
        if size == 1:
            self.h.pop()
            return root
    
        self.h[0] = self.h[size-1]
        self.h.pop()
        
        # Heapify
        current_i = 0
        while current_i < len(self.h):
            l_child_i = self.l_child(current_i)
            r_child_i = self.r_child(current_i)
            
            if l_child_i >= len(self.h):
                break
            
            if r_child_i >= len(self.h):
                child_i = l_child_i  
            elif self.h[l_child_i] < self.h[r_child_i]:
                child_i = l_child_i
                
            # Swap if current is greater than its least child
            if self.h[child_i] < self.h[current_i]:
                # Swap
                tmp = self.h[child_i]
                self.h[child_i] = self.h[current_i]
                self.h[current_i] = tmp
                # Go on
                current_i = child_i
        
        return root

    def push(self, x):
        index_x = len(self.h)
        self.h.append(x)

        current_i = index_x

        while current_i > 0:
            parent_i = self.parent(current_i)
            # Swap if current is less than its parent
            if  self.h[current_i] < self.h[parent_i]:
                # Swap
                tmp = self.h[parent_i]
                self.h[parent_i] = self.h[current_i]
                self.h[current_i] = tmp
                # Go on
                current_i = parent_i
            else:
                break
            
h = HeapMin()

h.push(3)
h.push(10)
h.push(20)
h.push(1)

print(h.h)

print(h.pop())
print(h.pop())
print(h.pop())
print(h.pop())
print(h.pop())