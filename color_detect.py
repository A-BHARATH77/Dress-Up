import cv2
import pandas as pd

# --------------------------------------------------------------------------

img_path = 'pic2.jpg'
csv_path = 'reduced_color.csv'

# reading csv file
index = ['color', 'color_name', 'hex', 'R', 'G', 'B', 'color_1', 'color_2', 'color_3', 'color_4', 'color_5']
df = pd.read_csv(csv_path, names=index, header=None)

# reading image
img = cv2.imread(img_path)
img = cv2.resize(img, (800, 600))

# declaring global variables
clicked = False
r = g = b = xpos = ypos = 0
printed = False  # Flag to control printing only once

# function to calculate minimum distance from all colors and get the most matching color
def get_color_name(R, G, B):
    minimum = 1000
    closest_row = None
    for i in range(len(df)):
        # Check if the row contains valid RGB values
        if pd.isna(df.loc[i, 'R']) or pd.isna(df.loc[i, 'G']) or pd.isna(df.loc[i, 'B']):
            continue  # Skip rows with missing RGB values

        # Calculate Euclidean distance between current color and dataset color
        d = abs(R - int(df.loc[i, 'R'])) + abs(G - int(df.loc[i, 'G'])) + abs(B - int(df.loc[i, 'B']))
        if d <= minimum:
            minimum = d
            cname = df.loc[i, 'color_name']
            closest_row = df.loc[i]  # Store the row that is the closest match

    # Print details of the closest matching row (entire row, including additional columns)
    if closest_row is not None:
        print("Closest matching color:")
        print(closest_row)
    
    return cname

# function to get x, y coordinates of mouse double click
def draw_function(event, x, y, flags, params):
    global printed  # Reference the printed flag
    if event == cv2.EVENT_LBUTTONDBLCLK and not printed:  # Print only once
        global b, g, r, xpos, ypos, clicked
        clicked = True
        xpos = x
        ypos = y
        b, g, r = img[y, x]
        b = int(b)
        g = int(g)
        r = int(r)
        printed = True  # Set flag to True after printing once

# creating window
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_function)

while True:
    cv2.imshow('image', img)
    if clicked:
        # Create a rectangle to show the color
        cv2.rectangle(img, (20, 20), (600, 60), (b, g, r), -1)

        # Creating text string to display (Color name and RGB values)
        text = get_color_name(r, g, b) + ' R=' + str(r) + ' G=' + str(g) + ' B=' + str(b)
        cv2.putText(img, text, (50, 50), 2, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        # For very light colors, we will display text in black color
        if r + g + b >= 600:
            cv2.putText(img, text, (50, 50), 2, 0.8, (0, 0, 0), 2, cv2.LINE_AA)

        # Reset printed flag after processing the click
        printed = False  # Reset the flag so the result will not print again until the next click
        clicked = False  # Reset clicked to allow a new click

    # Wait for user key press and check if the window was closed
    key = cv2.waitKey(20) & 0xFF
    if key == 27:  # Esc key
        break

    # Check if the window is being closed
    if cv2.getWindowProperty('image', cv2.WND_PROP_VISIBLE) < 1:
        break

cv2.destroyAllWindows()
