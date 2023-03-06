import csv
import os

results = []
for file_name in os.listdir("vi-wordnet"):
    if file_name.startswith('alphabet'):
        with open(os.path.join("vi-wordnet", file_name), 'r') as file:
            lines = file.read().splitlines()
            for line1 in lines:
                for line2 in lines:
                    result = line1 + line2
                    results.append(result)

with open("vi-wordnet/keywords.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # write each element of the array as a row in the CSV file
    for element in results:
        writer.writerow([element])
