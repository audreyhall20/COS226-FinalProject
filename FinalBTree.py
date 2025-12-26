'''
Audrey Hall 
DS 226 - Final Project 

DUE: DEC 19 @ 11:59

B+ Tree Structuring algorithm for indexed fields
'''

from typing import List, Union, Any, Optional

# Create a b tree per indexed field
    # [2] release_date -- MM/DD/YYYY (no leading 0s for single digits)
    # [4] box_office_revenue -- $ float 
    # [5] rating -- float from 0.0-10.0

class BucketNode:
    # A node in the B+ Tree
    def __init__(self, maxdegree, is_leaf = False):
        self.maxdegree = maxdegree
        self.leaf = is_leaf # use leaf to match visualizer
        self.values = []
        self.links = ['Bucket'] # B+ tree links (pointer to other nodes) aka values-- set to links to match visualizer language -- for internal node/children pointers
        self.keys = []  # keys/data -- for internal node keys
        self.next = None # refers to next keys
        self.parent = None

    # determine if curNode is leaf. Node is a leaf if it has no children / no child links
    def is_leaf(self):
        return self.leaf

    def is_full(self):
        return len(self.keys) >= self.maxdegree   
         

class BplusTree:

    def __init__(self, maxdegree = 5):
        # initial root is leaf
        self.root = BucketNode(maxdegree, is_leaf = True)
        self.maxdegree = maxdegree

    # receives sorted list of (key, original_index) from FinalProj.py
    # for simplicity, this implementation uses standard insertion.
    def bulkAddCSV(self, preparedData: List[tuple]):
        for key, index in preparedData:
            self.insert(key, index)

    def insert(self, key: Any, value: Any):
        node = self.root
        # find the correct leaf
        while not node.is_leaf():
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.links[i]

        # check if key already exists in this leaf to handle duplicates
        for i in range(len(node.keys)):
            if node.keys[i] == key:
                node.values[i].append(value)
                return 
            
                # # if key exists, append the index to the existing list
                # if isinstance(node.values[i], list):
                #     node.values[i].append(value)
                # else:
                #     node.values[i] = [node.values[i], value]
                # return

        # if key is new, insert into leaf in sorted order
        idx = 0
        # found = False
        # while idx < len(node.keys):
        #     if node.keys[idx] == key:
        #         # key exsits, append to exsisting list of record IDs
        #         node.values[idx].append(value)
        #         found = True
        #         break
        #     elif node.keys[idx] > key:
        #         # found spot where new key should go 
        #         break
        #     idx += 1

        # if not found: 
        #     # key is new, insert key and new list containing the value
        #     node.keys.insert(idx, key)
        #     node.values.insert(idx, [value])

        while idx < len(node.keys) and key > node.keys[idx]:
            idx += 1
            
        node.keys.insert(idx, key)
        node.values.insert(idx, [value]) # CRITICAL: wrap in brackets []

        # handle split if full
        if node.is_full():
            self._split(node)

    def _split(self, node: BucketNode):
        mid = len(node.keys) // 2
        split_key = node.keys[mid]
        
        new_node = BucketNode(self.maxdegree, is_leaf = node.is_leaf())
        new_node.parent = node.parent

        if node.is_leaf():
            # Leaf split: keep split_key in the right node
            new_node.keys = node.keys[mid:]
            new_node.values = node.values[mid:]
            node.keys = node.keys[:mid]
            node.values = node.values[:mid]
            
            # Update leaf chaining
            new_node.next = node.next
            node.next = new_node
        else:
            # Internal split: split_key moves UP, not kept in children
            new_node.keys = node.keys[mid+1:]
            new_node.links = node.links[mid+1:]
            for child in new_node.links:
                child.parent = new_node
            
            node.keys = node.keys[:mid]
            node.links = node.links[:mid+1]

        if node.parent is None:
            # Create new root
            new_root = BucketNode(self.maxdegree, is_leaf = False)
            new_root.keys = [split_key]
            new_root.links = [node, new_node]
            self.root = new_root
            node.parent = new_root
            new_node.parent = new_root
        else:
            # Push split_key to parent
            p = node.parent
            idx = 0
            while idx < len(p.keys) and split_key > p.keys[idx]:
                idx += 1
            p.keys.insert(idx, split_key)
            p.links.insert(idx + 1, new_node)
            if p.is_full():
                self._split(p)

    def search(self, key: Any) -> List[Any]:
        """Returns all values (indices) associated with a key"""
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            node = node.links[i]
        
        results = []
        for i, k in enumerate(node.keys):
            if k == key:
                # Since node.values[i] is a list, use extend instead of append
                results.extend(node.values[i])
        return results
    

    def range_search(self, lower_bound, upper_bound):
        results = []
        if self.root is None: 
            return []

        node = self.root

        # 1. Navigate to the correct leaf
        while not node.is_leaf():
            i = 0
            # USE > instead of >= to prevent overshooting
            while i < len(node.keys) and lower_bound > node.keys[i]:
                # if lower_bound <= node.keys[i]:
                #     break
                i += 1
            # Ensure we don't go out of bounds of the links
            #child_index = min(i, len(node.links) - 1)
            #node = node.links[child_index]
            node = node.links[i]

        # 2. Traverse the leaf chain
        currentLeaf = node

        # DEBUG: see what the leaf looks like
        #print(f"DEBUG: Arrived at leaf. Keys in this leaf: {currentLeaf.keys[:5]}")

        while currentLeaf:
            # SAFETY CHECK: Use the shorter of the two lengths to prevent IndexError
            #num_items = min(len(currentLeaf.keys), len(currentLeaf.values))

            #for i in range(num_items):
            for i in range(len(currentLeaf.keys)):
                k = currentLeaf.keys[i]
                #k = float(currentLeaf.keys[i])

            # for i, key in enumerate(currentLeaf.keys):
            #     # Ensure we compare numbers to numbers
            #     try: 
            #         k = float(key) # Standardize to float for numeric safety
            #         u_bound = float(upper_bound)
            #         l_bound = float(lower_bound)
            #     except(ValueError, TypeError):
            #         k = key
            #         u_bound = upper_bound
            #         l_bound = lower_bound

                # CRITICAL: Compare k (float) to upper_bound (float/int)
                if k > upper_bound:
                    return results

                # CRITICAL: Compare k (float) to lower_bound (float/int)
                if k >= lower_bound:
                    results.extend(currentLeaf.values[i])
                    # val = currentLeaf.values[i]
                    # if isinstance(val, list):
                    #     results.extend(val)
                    # else:
                    #     results.append(val)
            
            currentLeaf = currentLeaf.next
        return results
    
