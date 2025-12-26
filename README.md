# COS226-FinalProject
File runs from the FinalProj.py file, needs FinalHash.py and FinalBTree.py to properly run. Ececute the file, and choose numbered indexes to perfrom different tasks. 
Important notes for entering searchable data (some should also be clarrified in the code if input gets enterd wrong):
	
The efficiency of initializing the database is O(N * K) where N is the number of records and K is the number of fields being hashed. We iterate through the CSV once to load the memory, then again through the records to to populate the hash tables, making the complexity linear. The efficiency of creating the indxes within the Btree is O(N log N). B Tree insertion is generally already pretty efficient. The efficiency for an exact value queries is O(1) on average. For a ranged search efficiency is O(log N + M). O(log N) is the time is takes to get to the first lead node that satisfies the lower_bound. Because leafs are linked together, it can simply traverse leaves horizontaly until upper_bound is hit. A deletion has efficiency of O(log N) to find the value, and then O(1) to update the value to deleted. 

Example commands and their expected outputs: 
	Perform an exact value search: enter 2, enter the field title, enter what you'd like to search for
		Movie Title: if found will return the title, director, genre, and rating. 
			Ex- 'Thief who came to dinner, the' will return: 
			--- Found 1 Result(s) ---
			Title                          | Director             | Genre           | Rating
			--------------------------------------------------------------------------------
			Thief Who Came to Dinner, Th   | Marillin Copeland    | Action          | 6.1
			Results for 'thief who came to dinner, the' in 'movie_title'.
			
  Genre: will return all movies within that genre, as well as title, director, and rating. 
			Ex- searching 'romance' will find 3088 results
			
  Director: searching for 'Loree Jeram' returns:
			--- Found 1 Result(s) ---
			Title                          | Director             | Genre           | Rating
			--------------------------------------------------------------------------------
			Othello                        | Loree Jeram          | Drama           | 9.4
			Results for 'loree jeram' in 'director'.
			
  Duration Minutes: search for '214' will retun 84 results
		
  Production Company: searching for 'buzzdog' will return 41 results
		
 Perform a range search: create an indexed field by entering 1, then enter 3, enter a lower and upper bound range
		Release dates from 01/01/2020 - 21/31/2020 will return 132 results
		Box office revenues from 1 million - 10 million (must be entered with 0s not as string query) will return 1328 results
		Ratings from 7.0-9.5 will return 3980 results
		
 Deleting from an active database: 
		Select an option (1-6): 5
		Searchable fields for deletion: ['movie_title', 'genre', 'director', 'duration_minutes', 'production_company', 'release_date', 'rating', 'box_office_revenue']
		Enter the active database which you would like to delete: director 
		Enter value for 'director': Katya Aucutt
		Are you sure you want to delete records where director is Katya Aucutt? (y/n): y
		Successfully marked 1 records as deleted
		
 Exporting results to a CSV file: 
		What do you want to call your file: 1mil_10mil_movies
		Successfully exported 1328 records to 1mil_10mil_movies.csv
		File saved at: C:\Users\ArtHeart\Desktop\DS & Algorithms\1mil_10mil_movies.csv
		Exporting results to a CSV file...
		
  Will give you a path to where the CSV file was saved.

For creating the hash tables, I decided to implement a chaining hash method. This may not have been the best choice because of the amount of reapeats in almost any given category- especially genres, dates, and sometimes production company or director. However, in a past implementation of hash tables, chaining resulted in less hash indicies and thus slightly quicker searches. 

The B Tree was fairly simple overall to set up, however indexing the fields to handle $ infront of box office revenue, swaping the order of dates to actually process in chronological order, and handle the ratings properly was a little bit of a challenege. In the first and last of those indexes, 0s kept not being handled properly, 10.0 and 1.0 were swapped. $3,000 was registering as smaller than $900 because 3 is smaller than 9. 

The searchable fields I chose were all fields in the file except for Quotes. Quotes I decided to not make searchable, either through an indexed rang query or even for a general search because each movie quote is going to be far too unique to be easily searched for. It is possible that in a database, someone could want to search for a quote from a move, but I feel the chances of the quote they remember and the small quote stored in a certain database would macth up. If the database had access to the whole script of any given movie, then I think quote would be a reasonable field to make searchable. Otherwise, if someone wanted to search for a quote they would have to be incredibly specific with their search query. For general searchable fields I used movie title, genre, director, minutes, and production company. These are all fields that a user could have a general sense of, and get the results they want. For indexed fields I chose release date, box office revenue, and rating because number fields are what people are most likely to perform a ranged search on. 

Any known limitations or isses:
	When deleting an item, the field does get marked as deleted, but if you run a search before deleting the item, 'LastResults' stores the last returned range of items. The item is deleted, but it won't show as deleted unless the user runs the same search. Then that next set of returned results will not have the deleted item. The first few times I tested deleting an item, I deleted then searched, so I did not realize this was a problem until too late.
	
 All field titles must include _ between words not spaces
	
 Most things shouldn't be case sensitive, but I didn't have time to fully test this 
	
 Dates should be entered as MM/DD/YYYY (including backslashes)
	Ratings go from 0.0 to 10.0
	The avaibale years of movie release go from 1900-2022 (years before or after that range are unsearchable)
Availale movie genres are: comedy, romance, horror, action, drama



Link to video demonstrating functionality of program:
