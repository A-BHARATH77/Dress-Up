import pandas as pd
from bs4 import BeautifulSoup
import os
#https://www.colorhexa.com/color-names
data = [
      {"color_name": "cool_black", "human_readable_name": "Cool Black", "color_code": "#002e63", "r":0, "g":46, "b":99},
]
# Convert dataset to DataFrame
df = pd.DataFrame(data)
# HTML content to extract color schemes from (replace this with your actual HTML content)
html_content = """

"""

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Function to extract color codes from a color scheme section
def extract_colors_from_scheme(scheme_name, exclude_color):
    scheme = soup.find("div", id=scheme_name)
    colors = []
    if scheme:
        color_items = scheme.find_all("li")
        if color_items:  # Check if there are any <li> items
            for item in color_items:
                color_code = item.find("a").text.strip()
                # Only add the color code if it's not the same as the main color
                if color_code != exclude_color:
                    colors.append(color_code)
        else:
            print(f"No color items found in {scheme_name} section.")
    else:
        print(f"Scheme with id {scheme_name} not found.")
    return colors

# Iterate over each row in the DataFrame to add the color combinations
for index, row in df.iterrows():
    # Extract color schemes excluding the main color
    complementary_colors = extract_colors_from_scheme("complementary", row["color_code"])
    analogous_colors = extract_colors_from_scheme("analogous", row["color_code"])
    split_complementary_colors = extract_colors_from_scheme("split-complementary", row["color_code"])
    triadic_colors = extract_colors_from_scheme("triadic", row["color_code"])
    tetradic_colors = extract_colors_from_scheme("tetradic", row["color_code"])
    
    # Add the color schemes to the DataFrame
    df.at[index, 'Complementary Colors'] = ', '.join(complementary_colors)
    df.at[index, 'Analogous Colors'] = ', '.join(analogous_colors)
    df.at[index, 'Split Complementary Colors'] = ', '.join(split_complementary_colors)
    df.at[index, 'Triadic Colors'] = ', '.join(triadic_colors)
    df.at[index, 'Tetradic Colors'] = ', '.join(tetradic_colors)

# Check if the CSV file already exists
csv_file = "reduced_color.csv"

if os.path.exists(csv_file):
    # If the file exists, load the existing data
    existing_df = pd.read_csv(csv_file)
    # Append the new data
    df_combined = pd.concat([existing_df, df], ignore_index=True)
    # Save the updated DataFrame back to CSV
    df_combined.to_csv(csv_file, index=False)
else:
    # If the file does not exist, create a new file
    df.to_csv(csv_file, index=False)

# Display the updated DataFrame
print(df)
