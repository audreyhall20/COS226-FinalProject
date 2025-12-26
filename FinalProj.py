'''
Audrey Hall 
DS 226 - Final Project 

DUE: DEC 19 @ 11:59

Main functioning code
'''


from FinalBTree import BplusTree
from FinalHash import MyHashTable
from typing import List, Dict, Any
import csv  # to read in data from MOCK_DATA movie file
import os   # helps with results file export - tells you where your file went on your computer

# Must use the following structures
#   B+ Tree: for range queries on indexed fields 
#       (create one tree per indexed field)
#   Hash table: for exact value searches on all searchable fields 
#       (create a table for every field that can be searvhed at the time of database creation)
#   Primary Data Storage: made first and needs to be sorted so B+ tree can be bulk loaded
#       
#   B+ and Hash will store references to the records in the primary data storage


# records class manages primary data stroage - holds all of the data from MOCK_DATA file
class RecordDatabase():
    def __init__(self):
        # primary storage: list to hold movie records (dictionaries)
        self.primStorage: List[Dict[str, Any]] = []

        # dictionaries to hold btree and hash indecies 
        self.BplusTreeIndices: Dict[str, Any] = {}  # ex. {'release year': BplusTree_Object}
        self.hashIndices: Dict[str, Any] = {}       # ex. {'title': hash_Object}

    # bulk add data from csv file into primary storage
    # -> indicates functions return type
    def bulkAddCSV(self, csvFilePath: str, initIndexField: str = None) -> None:
        print(f"Starting bulk data load from {csvFilePath}...") 

        # Step 1 - Read data into primary storage 
        try: 
            with open(csvFilePath, mode = 'r', newline='', encoding = 'utf8') as file:
                reader = csv.DictReader(file)
                #self.primStorage = list(reader)
                self.primStorage = []
                for row in reader:
                    row['_deleted'] = False  # Add this flag
                    self.primStorage.append(row)
            print(f"Loaded {len(self.primStorage)} records into primary storage.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return
        
        # Step 2 - Build Hash Tables (Requirement: build these at database creation)
        # This provides O(1) search for exact values immediately.
        self.buildAllHashTables()

        # Step 3 - ONLY create B+ Tree if initIndexField was provided
        if initIndexField:
            # Sort and create the specific B+ Tree index requested
            self.primStorage.sort(key = lambda record: self.sortKey(record, initIndexField))
            self.createIndex(initIndexField)

        print("Bulk load process complete.")


    #@staticmethod
    def sortKey(self, record: Dict[str, Any], fieldName: str) -> Any:
        value = record.get(fieldName, "")
        if value is None: return 0

        # Handle numeric and special types
        if fieldName == 'release_date':
            return self.dateSortableInt(value)

        if fieldName in {'box_office_revenue', 'rating', 'duration_minutes'}:
            try:
                # Clean out currency/commas and convert to float
                clean_val = str(value).replace('$', '').replace(',', '').strip()
                return float(clean_val) if clean_val else 0.0
            except ValueError:
                return 0.0
                
        # Alphabetical fields
        return str(value).strip().lower()


    # this manages primStorage logic and hands data over to bTree class
    def createIndex(self, fieldName: str):
        # BTree implementation will be called here to bulk-load index
        print(f"Building B+ Tree index on {fieldName}...")

        # prepare data: create list of (key, index) touples 
        # need key to sort by, and the 'i' to point back to primStorage 
        preparedData = []
        for i, record in enumerate(self.primStorage):
            key = self.sortKey(record, fieldName)
            preparedData.append((key, i))

        # sort the preped data by the key before bulk loading 
        preparedData.sort(key = lambda x: x[0])

        # for testing - print first and last 5 values being sent to Btree bulk loader, to prove its sorted before adding
        print([x[0] for x in preparedData[:5]])
        print([x[0] for x in preparedData[-5:]])

        # 1 prepare data from primStorage
        # 2 instantiate bTree from other file 
        newTree = BplusTree()
        # call bulk load logic defined in other file
        newTree.bulkAddCSV(preparedData)   

        # Try to find just ONE record that we know exists -- used for testing because indexes were being created but ranged searches weren't working for a while
            # test_key = preparedData[0][0] # The very first key we tried to insert
            # test_search = newTree.range_search(test_key, test_key)
            # print(f"DEBUG: Tree Verification for {fieldName}:")
            # print(f"  Attempting to find key {test_key}...")
            # print(f"  Results found: {len(test_search)}")

        self.BplusTreeIndices[fieldName] = newTree

        # for testing because date range isn't returning any results
        #print(f"Index for {fieldName} created. First 3 keys in tree: {newTree.get_min_keys(3)}")
        

    def buildAllHashTables(self) -> None:
        # define searchable fields - reasons for each are explained in README file
        searchFields = ['movie_title', 'genre', 'director', 'duration_minutes', 'production_company']

        print(f"Creating hash tables for fields: {searchFields}")

        for field in searchFields: 
            # create instance of external hash table class 
            newTable = MyHashTable(size = len(self.primStorage) * 2)

            # iterate through primary storage
            # enumerate gives the 'i' (reference / index) and the 'record'
            for i, record in enumerate(self.primStorage):
                keyValue = record.get(field)

                if keyValue is not None:
                    # strip whitespace and make it a string - this ensures '90 ' and '90' are treated the same
                    #cleanValue = str(keyValue).strip()
                    # store the key and the index (reference), not the whole record
                    newTable.insert(str(keyValue).strip().lower(), i)

            # store the hash table in index dictionary
            self.hashIndices[field] = newTable

        print("All hash tables built successfully!")


    # Searches the Hash Table for a specific value and returns full records
    def exactSearch(self, field: str, value: str) -> List[Dict[str, Any]]:
        if field not in self.hashIndices:
            print(f"Error: No hash index available for '{field}'.")
            return []

        # Get the hash table for this field
        table = self.hashIndices[field]
        
        # The hash table returns a list of integer indices (references)
        #record_indices = table.search(value)
        indices = self.hashIndices[field].search(value.lower().strip())
        
        # Convert those indices into the actual movie dictionaries
        # 'if not...' filters out deleted records
        results = [self.primStorage[idx] for idx in indices if not self.primStorage[idx].get('_deleted')]
        return results
    
    
    # executes a range query using the B+ Tree for the specified field
    def rangeQuery(self, field: str, lower: str, upper: str):
        if field not in self.BplusTreeIndices:
            print(f"Error: {field} is not indexed.")
            return []

        # Prepare bounds based on field type
        try:
            if field == 'release_date':
                lowBound = self.dateSortableInt(lower)
                upBound = self.dateSortableInt(upper)
            elif field == 'box_office_revenue':
                lowBound = self.clean_currency(lower)
                upBound = self.clean_currency(upper)
            # elif field in {'rating', 'duration_minutes', 'box_office_revenue'}:
            #     lowBound = float(lower.replace('$', '').replace(',', '').strip())
            #     upBound = float(upper.replace('$', '').replace(',', '').strip())
            elif field == 'rating': # Add an explicit ELIF for rating
                lowBound = float(lower)
                upBound = float(upper)
            else:
                lowBound = lower.strip().lower()
                upBound = upper.strip().lower()
        except Exception as e:
            print(f"Error: Input values for {field} must be numeric or MM/DD/YYYY.")
            return []

        # Check logic
        if lowBound > upBound:
            print("Error: Lower bound cannot be higher than upper bound.")
            return []
        
        print(f"DEBUG: Searching B+ Tree for {field} with bounds: {lowBound} to  {upBound}")
        
        # Perform the search
        tree = self.BplusTreeIndices[field]
        record_indices = tree.range_search(lowBound, upBound)
        
        return [self.primStorage[idx] for idx in record_indices if not self.primStorage[idx].get('_deleted')]
    

    def dateSortableInt(self, date_str):
        try:
            # This handles M/D/YYYY and MM/DD/YYYY
            parts = str(date_str).strip().split('/')
            if len(parts) == 3:
                m = int(parts[0])
                d = int(parts[1])
                y = int(parts[2])
                # Formula: YYYYMMDD (e.g., 20230105)
                # This ensures Jan 5th is 20230105 and Oct 10th is 20231010
                return y * 10000 + m * 100 + d
        except (ValueError, IndexError):
            return 0
        return 0

    def clean_currency(self, value):
        try:
            return float(str(value).replace('$', '').replace(',', '').strip())
        except ValueError:
            return 0.0

    # helper to print search results in a readable format
    def displayResults(self, results: List[Dict[str, Any]]) -> None:
        # Filter out logically deleted records
        activeResults = [r for r in results if not r.get('_deleted', False)]

        if not activeResults:
            print("No active records found.")
            return

        print(f"\n--- Found {len(results)} Result(s) ---")
        # Print a header
        print(f"{'Title':<30} | {'Director':<20} | {'Genre':<15} | {'Rating'}")
        print("-" * 80)
        
        for movie in results:
            title = movie.get('movie_title', 'N/A')[:28]
            director = movie.get('director', 'N/A')[:18]
            genre = movie.get('genre', 'N/A')[:13]
            rating = movie.get('rating', 'N/A')
            print(f"{title:<30} | {director:<20} | {genre:<15} | {rating}")


    # Exports a list of search results to a new CSV file
    def exportToCSV(self, results: List[Dict[str, Any]], fileName: str):
        if not results:
            print("No results to export.")
            return

        # Ensure filename ends with .csv
        if not fileName.endswith('.csv'):
            fileName += '.csv'

        try:
            # The fieldnames are the keys from the first record
            keys = results[0].keys()
            csv_columns = [key for key in keys if key != '_deleted']
            
            with open(fileName, mode='w', newline='', encoding='utf8') as output_file:
                #writer = csv.DictWriter(output_file, fieldnames=keys)
                writer = csv.DictWriter(output_file, fieldnames=csv_columns, extrasaction='ignore')
                writer.writeheader()

                # if user deletes data before trying to export to a CSV file, this will ensure the deleted data is not included in the file
                active_results = [r for r in results if not r.get('_deleted', False)]
                writer.writerows(active_results)

                writer.writerows(results)
                
            # get the fill filepath
            fullPath = os.path.abspath(fileName)
            print(f"Successfully exported {len(results)} records to {fileName}")
            print(f"File saved at: {fullPath}")

        except Exception as e:
            print(f"Error exporting to CSV: {e}")


    # Locates records and marks them as deleted
    def deleteRecords(self, field: str, value: str):
        # Use your existing exactSearch to find the targets
        #results = self.exactSearch(field, value)

        results = []
        
        # try Hash Table first
        if field in self.hashIndices:
            results = self.exactSearch(field, value)
        
        # if not in Hash, try B+ Tree (exact search is just a range query where low == high)
        elif field in self.BplusTreeIndices:
            print(f"Searching B+ Tree index for '{field}'...")
            # We need to format the value (e.g., turn '0.5' string into 0.5 float)
            if field == 'release_dat/e':
                search_val = self.dateSortableInt(value)
            elif field == 'rating' or field == 'box_office_revenue':
                search_val = self.clean_currency(value)
            else:
                search_val = value
                
            results = self.rangeQuery(field, str(value), str(value))
        
        if not results:
            print(f"No records found matching {field} = {value}.")
            return

        count = 0
        for record in results:
            if not record['_deleted']:
                record['_deleted'] = True
                count += 1
        
        print(f"Successfully marked {count} records as deleted.")




# create a user interface
def userInterface(db: RecordDatabase):
    # 5 required commands: create index, extract value search, range query, export results, delete from active database
    
    # Initialize last results (for option 4) here so it's always defined
    lastResults = []  
    
    while True: 
        print("\n--- COS 226 Final Project Database System ---")
        print("1. Create an Index")
        print("2. Perform an Exact Value Search")
        print("3. Perform a Range Query")
        print("4. Export Results to CSV")
        print("5. Delete Records from Active Database")
        print("6. Exit")
    
        # display current status (requirement in 3.1)
        indexedFields = list(db.BplusTreeIndices.keys())
        print(f"Current B+ Tree Indexed Fields: {indexedFields if indexedFields else 'None'}")

        userChoice = input("\nSelect an option (1-6): ").strip()

        if userChoice == '1':
            print("Available fields to index are: 'release_date', 'box_office_revenue', or 'rating'. Please type the exact title.")
            field = input("Enter the field name to index: ").strip()
            db.createIndex(field)

        elif userChoice == '2': 
            field = input("Enter field to search (movie_title, genre, director, duration_minutes, production_company): ").strip()
            value = input(f"Enter exact value for '{field}': ").strip().lower()

            lastResults = db.exactSearch(field, value.lower().strip()) 
            db.displayResults(lastResults)

            print(f"Results for '{value}' in '{field}'.")

        # NOTE: release dates only go from year 1990-2022
        # NOTE: ratings go from 0.0 - 10.0
        elif userChoice == '3':
            print(f"Available indexed fields to perform a range query are: {indexedFields if indexedFields else 'None'}")
            field = input("Enter indexed field for range query: ").strip()

            if field not in db.BplusTreeIndices:
                print(f"Error: {field} is not indexed. Range query on works on indexed fields. Please create an Index before performing a range query.")
            else: 
                lower = input("Enter lower bound: ").strip()
                upper = input("Enter upper bound: ").strip()

                # check moved to rangeQuery
                # if lower > upper:
                #     print(f"Error: Lower bound ({lower}) cannot be greater than upper bound ({upper}).")
                #     return []

                lastResults = db.rangeQuery(field, lower, upper)

                if not lastResults:
                # Check if the bounds are even within the dataset's actual range
                    print(f"No records found for {field} between {lower} and {upper}.")
                    if (field == "release_date"):
                        print("Tip: Release years in the file goes from 1900 - 2022, and are formated MM/DD/YYYY. Make sure you're searching within this range.")
                    elif(field == "rating"):
                        print("Tip: Rating scale in the file goes from 0.0 - 10.0. Make sure you're searching within this range.")
                    
                    print("Tip: Check your spelling or ensure the range exists in the database.")
                else:
                    db.displayResults(lastResults)


        elif userChoice == '4':
            if not lastResults:
                print("Error: You must perform a search (Option 2 or 3) before exporting.")
            else:
                fileName = input("What do you want to call your file: ").strip()
                db.exportToCSV(lastResults, fileName)

            print("Exporting results to a CSV file...")
            #print("awaiting complete implementation...")

        elif userChoice == '5': 
            allSearchable = list(db.hashIndices.keys()) + list(db.BplusTreeIndices.keys())
            print(f"Searchable fields for deletion: {allSearchable}")
            
            field = input("Enter the active database which you would like to delete: ").strip()
            value = input(f"Enter value for '{field}': ").strip()

            confirm = input(f"Are you sure you want to delete records where {field} is {value}? (y/n): ")
            if confirm.lower() == 'y':
                db.deleteRecords(field, value)
                print("Deleting records from active database")

        elif userChoice == '6': 
            print("Exiting system. Goodbye!")
            break 

        else: 
            print("Invalid choice. Please try again, enter a number between 1-6.")




def main():

    file = "MOCK_DATA.csv"

    db = RecordDatabase()

    # load data into primary storageS
    db.bulkAddCSV(file)

    # open user interface
    userInterface(db)

    

if __name__ == "__main__":
    main()
