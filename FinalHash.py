'''
Audrey Hall 
DS 226 - Final Project 

DUE: DEC 19 @ 11:59

Hash algorithm for searchable fields
'''

# decided to use chaining for hashing fuction

# create a hash table for EVERY searchable field
    # [0] movie_title 
	# [1] genre -- romance, drama, horror, action, comedy
	# [3] director
	# [6] duration_minutes
    # [7] production_company
    
class DataItem:
    def __init__(self, line):
        self.movieName = line[0]
        self.genre = line[1]
        self.releaseDate = line[2]
        self.director = line[3]
        self.revenue = self.parseRevenue(line[4])    # need to handle '$' at beginning
        self.rating = float(line[5]) if line[5] else 0.0
        self.minDuration = int(line[6]) if line[6] else 0
        self.productionComp = line[7]
        self.quote = line[8]

    # Helper to clean revenue data
    def parseRevenue(self, rev_str):
        if rev_str.startswith('$'):
            rev_str = rev_str.replace('$', '')
        try:
            return float(rev_str)
        except ValueError:
            return 0.0

class MyHashTable:
    def __init__(self, size = 15000):
        self.size = size
        self.table = [[] for _ in range(self.size)]

    # helper function to calculate hash index      
    def unicodeHash(self, key):
        # ensure key is a string for hashing 
        str_key = str(key)

        sumChars = 0
        for char in str_key:
            sumChars += ord(char)
            
        # Using a large prime multiplier helps reduce common factors.
        large_multiplier = 997
        expanded_key = sumChars * large_multiplier

        # mod by the size of the table
        return expanded_key % self.size

    # should be inside hash class? was causing errors 
    # Inserts a key and its reference index into the hash table, uses chaining to handle collisions   
    def insert(self, key, recordIndex):
        # insert specific hash function
        hashVal = self.unicodeHash(key)
        self.table[hashVal].append((key, recordIndex))

    
    # Returns a list of record indices that match the given key.
    def search(self, key):
        
        hashVal = self.unicodeHash(key)
        bucket = self.table[hashVal]
        
        # Search the chain for all matches 
        # (Important for fields like 'genre' where many records share one key)
        results = []
        for item_key, item_index in bucket:
            if item_key == key:
                results.append(item_index)
        
        return results

    # Function to add a key (dataItem) to a specific hash table array - using double hashing for collisions
    def addChaining(key, item, hashTableArr, tableSize, hashFunction):
        
        # 1. Get the initial hash index
        index = self.unicodeHash(key, tableSize)

        # 2. Check the bucket (the list at that index)
        bucket = hashTableArr[index]
        
        # Collision count for THIS specific key insertion
        collisions = 0
        
        # If the index is empty, initialize it with a list
        if bucket is None:
            hashTableArr[index] = [item]
            # Note: In Chaining, the first item added to a bucket is NOT a collision.
            return (True, 0)
        
        # If the index is occupied (a list exists), iterate through the chain
        # Every item we check in the chain is a COLLISION
        for itemExsit in bucket:
            # Check if the key already exists (Movie Title or Quote)
            # We assume 'key' matches the item's primary attribute for this table
            itemKey = getattr(itemExsit, 'movieName') if key == itemExsit.movieName else getattr(itemExsit, 'quote')
            
            if key == itemKey:
                # Key found. This is typically an update in real-world use.
                # We don't update here, just return the collisions encountered to find it.
                return (True, collisions) 
            
            # If the item is different, it is a collision event (a link in the chain)
            collisions += 1

        # 3. If the loop completes, the key is new. Append the DataItem to the chain/bucket
        bucket.append(item)
        
        return (True, collisions) # Successful insertion
        


        
def main():
    #size = 15000
    pass

if __name__ == "__main__":
    main()
