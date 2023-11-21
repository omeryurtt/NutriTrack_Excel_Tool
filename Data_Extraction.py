# This program retrieves food information using the USDA's FoodData Central (FDC) API and saves it to an Excel file.

# Import necessary libraries
import requests
import json
import time
import pandas as pd
from datetime import datetime

# Define the base URL of the FDC API and the API key
base_url = "https://api.nal.usda.gov/fdc/v1"
api_key = "YOUR_KEY"

# Specify the start and end indices for the requests (I found index numbers for each unique food in their excel file)
start_index = 2340760
end_index = 2346384

# Define the maximum number of requests per hour and the request interval (API doesn't let me more than one thousand per hour.)
max_requests_per_hour = 999
request_interval = 3600 / max_requests_per_hour

# Variables for request timing
start_time = time.time()
request_counter = 0

# Create a list to store food information
data_list= []

# Make an API request for each food in the specified index range
for i in range(start_index, end_index):
    
    # Create the URL for the API request
    url = f"{base_url}/food/{i}?api_key={api_key}"
    
    while True:
        # Send a request to the API
        response = requests.get(url)
    
        # Process the data if the request is successful
        if response.status_code == 200:
            data_dict = json.loads(response.text)
            
            # Get the food name
            food_name = data_dict.get("description", "Unknown")
            request_counter += 1
            
            # Get the current time (I just wanted to observe what nutrients it was getting and the time it took to capture the data. )
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"Food Name: {food_name},
                  Request Count: {request_counter},
                  Current Time: {current_time}")
            
            # Get the nutrition facts
            nutrition_facts = data_dict.get("foodNutrients", [])
    
            # Store nutrient information in a dictionary (After reviewing a sample .json response, I added the data I needed to the dictionary as I wanted to make my work easier in excel.)
            nutrient_data = {"Food Name": food_name}
            for nutrient in nutrition_facts:
                nutrient_name = nutrient.get("nutrient", {}).get("name", "Unknown")
                nutrient_amount = nutrient.get("amount", 0)
                nutrient_unit = nutrient.get("nutrient", {}).get("unitName", "Unknown")
                nutrient_data[f"{nutrient_name} ({nutrient_unit})"] = nutrient_amount

            # Add the data to the list
            data_list.append(nutrient_data)
            break
        else:
            # Display the error code and FDC_id if the API request fails
            print(f"API request failed. Error code:{response.status_code}. FDC_id: {i}")
            
            # Wait for 5 minutes in case of an error
            time.sleep(300)

    # Calculate the time elapsed between requests   (Since the response time for each request can be different, I optimized it using the time module.)
    elapsed_time = time.time() - start_time
    
    # Determine the waiting time (no need to wait if negative)
    wait_time = max(0, request_interval - elapsed_time)
    
    # Pause the program for the specified time
    time.sleep(wait_time)
    
    # Update the start time
    start_time = time.time()

# Convert the data to a Pandas DataFrame
df = pd.DataFrame(data_list)

# Save the DataFrame to an Excel file
df.to_excel('FDC_Data.xlsx', index=False)
