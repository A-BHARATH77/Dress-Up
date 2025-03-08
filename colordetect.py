import cv2
import pandas as pd
import os

# Define the path where images are uploaded
upload_folder = 'src/uploads'
csv_path = 'reduced_color.csv'

# Get the latest uploaded image
def get_latest_image(folder):
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not files:
        raise FileNotFoundError("No image files found in the uploads folder.")
    
    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(folder, f)))
    return os.path.join(folder, latest_file)

try:
    img_path = get_latest_image(upload_folder)
except FileNotFoundError as e:
    print(e)
    exit()

print(f"Using latest uploaded image: {img_path}")

# Reading CSV file
index = ['color', 'color_name', 'hex', 'R', 'G', 'B', 'color_1', 'color_2', 'color_3', 'color_4', 'color_5']
df = pd.read_csv(csv_path, names=index, header=None)

# Reading image
img = cv2.imread(img_path)
img = cv2.resize(img, (800, 600))

# Declaring global variables
clicked = False
r = g = b = xpos = ypos = 0
printed = False  # Flag to control printing only once

# Function to get the closest matching color
def get_color_name(R, G, B):
    minimum = 1000
    closest_row = None
    for i in range(len(df)):
        if pd.isna(df.loc[i, 'R']) or pd.isna(df.loc[i, 'G']) or pd.isna(df.loc[i, 'B']):
            continue

        d = abs(R - int(df.loc[i, 'R'])) + abs(G - int(df.loc[i, 'G'])) + abs(B - int(df.loc[i, 'B']))
        if d <= minimum:
            minimum = d
            cname = df.loc[i, 'color_name']
            closest_row = df.loc[i]

    if closest_row is not None:
        print("Closest matching color:")
        print(closest_row)
    
    return cname

# Function to get x, y coordinates of mouse double click
def draw_function(event, x, y, flags, params):
    global printed
    if event == cv2.EVENT_LBUTTONDBLCLK and not printed:
        global b, g, r, xpos, ypos, clicked
        clicked = True
        xpos = x
        ypos = y
        b, g, r = img[y, x]
        b = int(b)
        g = int(g)
        r = int(r)
        printed = True

# Creating window
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_function)

while True:
    cv2.imshow('image', img)
    if clicked:
        cv2.rectangle(img, (20, 20), (600, 60), (b, g, r), -1)
        text = get_color_name(r, g, b) + ' R=' + str(r) + ' G=' + str(g) + ' B=' + str(b)
        cv2.putText(img, text, (50, 50), 2, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        if r + g + b >= 600:
            cv2.putText(img, text, (50, 50), 2, 0.8, (0, 0, 0), 2, cv2.LINE_AA)

        printed = False
        clicked = False

    key = cv2.waitKey(20) & 0xFF
    if key == 27:
        break

    if cv2.getWindowProperty('image', cv2.WND_PROP_VISIBLE) < 1:
        break

cv2.destroyAllWindows()
