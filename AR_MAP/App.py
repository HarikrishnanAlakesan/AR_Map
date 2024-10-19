import cv2
import numpy as np
import pyttsx3
import tkinter as tk
import sqlite3
from datetime import datetime

# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speech rate
engine.setProperty('volume', 1)   # Set volume to maximum

# Function to make the system speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Database setup
def setup_database():
    conn = sqlite3.connect('visit_history.db')  # Create a database file
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Function to record a visit in the database
def record_visit(destination):
    conn = sqlite3.connect('visit_history.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO visits (destination) VALUES (?)', (destination,))
    conn.commit()
    conn.close()

# Function to get visit history
def get_visit_history():
    conn = sqlite3.connect('visit_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT destination, COUNT(*) FROM visits GROUP BY destination')
    history = cursor.fetchall()
    conn.close()
    return history

# Function to draw a vertical arrow on the frame
def draw_vertical_arrow(image, position):
    height, width = image.shape[:2]
    arrow_x = position
    arrow_y_top = height // 4
    arrow_y_bottom = (3 * height) // 4

    # Draw the arrow shaft
    shaft_width = 15
    cv2.rectangle(image, (arrow_x - shaft_width // 2, arrow_y_bottom), 
                  (arrow_x + shaft_width // 2, arrow_y_top), (0, 255, 255), -1)

    # Draw the arrowhead (triangle)
    arrowhead_height = 30
    triangle_points = np.array([ 
        (arrow_x - 30, arrow_y_top), 
        (arrow_x + 30, arrow_y_top), 
        (arrow_x, arrow_y_top - arrowhead_height) 
    ], np.int32)

    cv2.fillPoly(image, [triangle_points], (0, 255, 255))

# Function to draw a left-pointing arrow on the frame
def draw_left_arrow(image, position):
    height, width = image.shape[:2]
    arrow_y = position
    arrow_x_left = width // 4
    arrow_x_right = (3 * width) // 4

    # Draw the arrow shaft
    shaft_width = 15
    cv2.rectangle(image, (arrow_x_left, arrow_y - shaft_width // 2), 
                  (arrow_x_right, arrow_y + shaft_width // 2), (0, 255, 255), -1)

    # Draw the arrowhead (triangle)
    arrowhead_width = 30
    triangle_points = np.array([
        (arrow_x_left, arrow_y - 30),
        (arrow_x_left, arrow_y + 30),
        (arrow_x_left - arrowhead_width, arrow_y)
    ], np.int32)

    cv2.fillPoly(image, [triangle_points], (0, 255, 255))

# Function to draw a right-pointing arrow on the frame
def draw_right_arrow(image, position):
    height, width = image.shape[:2]
    arrow_y = position
    arrow_x_left = width // 4
    arrow_x_right = (3 * width) // 4

    # Draw the arrow shaft
    shaft_width = 15
    cv2.rectangle(image, (arrow_x_left, arrow_y - shaft_width // 2), 
                  (arrow_x_right, arrow_y + shaft_width // 2), (0, 255,255), -1)

    # Draw the arrowhead (triangle)
    arrowhead_width = 30
    triangle_points = np.array([
        (arrow_x_right, arrow_y - 30),
        (arrow_x_right, arrow_y + 30),
        (arrow_x_right + arrowhead_width, arrow_y)
    ], np.int32)

    cv2.fillPoly(image, [triangle_points], (0, 255, 255))

# Function to draw a stylish button with rounded corners and shadow effect
def draw_stylish_button(image, button_text, y_position):
    height, width = image.shape[:2]
    button_position = (width // 2 - 40, y_position)  # Centered below the arrows

    # Button rectangle with rounded corners
    button_color = (0, 255, 0)  # Green color
    shadow_color = (0, 100, 0)  # Darker green for shadow effect
    button_radius = 10
    button_rect = (width // 2 - 70, y_position - 30, width // 2 + 70, y_position + 30)

    # Draw shadow effect
    cv2.rectangle(image, (button_rect[0] + 5, button_rect[1] + 5), 
                  (button_rect[2] + 5, button_rect[3] + 5), shadow_color, -1)

    # Draw button rectangle
    cv2.rectangle(image, (button_rect[0], button_rect[1]), 
                  (button_rect[2], button_rect[3]), button_color, -1, lineType=cv2.LINE_AA)

    # Draw button text
    draw_text(image, button_text, (button_rect[0] + 30, y_position + 10), (255, 255, 255))  # White text

# Function to draw the text on the screen
def draw_text(image, text, position, color=(255, 255, 255)):  # Default color is black
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, text, position, font, 1, color, 2, cv2.LINE_AA)

# Function to draw a red circle in the center of the frame
def draw_red_circle(image):
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    radius = 50
    color = (0, 0, 255)  # Red color in BGR
    thickness = -1  # Fill the circle
    cv2.circle(image, center, radius, color, thickness)

# Open the camera stream from IP Webcam
def run_ipwebcam(destination):
    url = 'http://192.168.1.3:8080/video'
    cap = cv2.VideoCapture(url)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    stage = 0  # This will track which stage we're in (0 to 5)
    initial_command_spoken = False  # Track if the initial command has been spoken

    # Function to handle mouse clicks
    def handle_mouse(event, x, y, flags, param):
        nonlocal stage, initial_command_spoken
        # Button boundaries for "Next"
        next_button_x_min = cap.get(3) // 2 - 70
        next_button_x_max = cap.get(3) // 2 + 70
        next_button_y_min = cap.get(4) - 90
        next_button_y_max = cap.get(4) - 30
        
        # Button boundaries for "Close"
        close_button_x_min = cap.get(3) // 2 - 50
        close_button_x_max = cap.get(3) // 2 + 50
        close_button_y_min = cap.get(4) - 70
        close_button_y_max = cap.get(4) - 30
        
        # Check for left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check if the click is within the "Next" button boundaries
            if stage < 5 and (next_button_x_min <= x <= next_button_x_max) and (next_button_y_min <= y <= next_button_y_max):
                stage += 1  # Move to the next stage

                # Record visit to the database
                record_visit(destination)

                if destination == "KFC":
                    # Define the next command to speak based on the next stage for KFC
                    if stage == 1:
                        speak("Turn left for 12 meters.")
                    elif stage == 2:
                        speak("Go straight for 35 meters.")
                    elif stage == 3:
                        speak("Turn right for 10 meters.")
                    elif stage == 4:
                        speak("Go straight for 22 meters.")
                    elif stage == 5:
                        speak("You have reached KFC.")
                elif destination == "McDonald's":
                    # Define the next command to speak based on the next stage for McDonald's
                    if stage == 1:
                        speak("Turn right 50 meters.")
                    elif stage == 2:
                        speak("Go straight for 50 meters.")
                    elif stage == 3:
                        speak("Turn left 20 meters.")
                    elif stage == 4:
                        speak("Go straight for 15 meters.")
                    elif stage == 5:
                        speak("You have reached McDonald's.")

            # Check if the click is within the "Close" button boundaries
            elif stage == 5 and (close_button_x_min <= x <= close_button_x_max):
                cv2.destroyAllWindows()  # Close the window

    # Set mouse callback
    cv2.namedWindow("Arrow and Text Overlay")
    cv2.setMouseCallback("Arrow and Text Overlay", handle_mouse)

    # Initial command based on the selected destination
    if destination == "KFC":
        speak("Go straight for 30 meters.")  # Speak the first command for KFC
    elif destination == "McDonald's":
        speak("Go straight for 20 meters.")  # Speak the first command for McDonald's

    initial_command_spoken = True

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Define positions for arrows and text
        arrow_position = frame.shape[1] // 2  # Horizontally centered
        text_position = (50, 50)

        # Define stages for KFC navigation
        if destination == "KFC":
            if stage == 0:
                draw_vertical_arrow(frame, arrow_position)
                draw_text(frame, "Go Straight (30 meters)", text_position)

            elif stage == 1:
                draw_left_arrow(frame, frame.shape[0] // 2)
                draw_text(frame, "Turn Left", text_position)

            elif stage == 2:
                draw_vertical_arrow(frame, arrow_position)
                draw_text(frame, "Go Straight (35 meters)", text_position)

            elif stage == 3:
                draw_right_arrow(frame, frame.shape[0] // 2)
                draw_text(frame, "Turn Right", text_position)

            elif stage == 4:
                draw_vertical_arrow(frame, arrow_position)
                draw_text(frame, "Go Straight (22 meters)", text_position)

            elif stage == 5:
                draw_red_circle(frame)
                draw_text(frame, "You have reached your destination!", text_position)

        # Define stages for McDonald's navigation
        elif destination == "McDonald's":
            if stage == 0:
                draw_vertical_arrow(frame, arrow_position)
                draw_text(frame, "Go Straight (20 meters)", text_position)

            elif stage == 1:
                draw_right_arrow(frame, frame.shape[0] // 2)
                draw_text(frame, "Turn Right", text_position)

            elif stage == 2:
                draw_vertical_arrow(frame, arrow_position)
                draw_text(frame, "Go Straight (50 meters)", text_position)

            elif stage == 3:
                draw_left_arrow(frame, frame.shape[0] // 2)
                draw_text(frame, "Turn Left", text_position)

            elif stage == 4:
                draw_vertical_arrow(frame, arrow_position)
                draw_text(frame, "Go Straight (15 meters)", text_position)

            elif stage == 5:
                draw_red_circle(frame)
                draw_text(frame, "You have reached your destination!", text_position)

        # Draw the stylish "Next" button
        draw_stylish_button(frame, "Next", int(frame.shape[0] - 60))

        cv2.imshow("Arrow and Text Overlay", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

# Tkinter window setup
def show_history():
    history = get_visit_history()
    history_text = "Visit History:\n\n"
    
    kfc_count = next((count for dest, count in history if dest == "KFC"), 0)
    mcd_count = next((count for dest, count in history if dest == "McDonald's"), 0)

    history_text += f"KFC: {kfc_count} visits\n"
    history_text += f"McDonald's: {mcd_count} visits\n"

    history_window = tk.Toplevel()
    history_window.title("Visit History")
    history_window.geometry("250x150")

    # Load and set background image for history window
    bg_image = tk.PhotoImage(file='bgh.png')
    bg_label = tk.Label(history_window, image=bg_image)
    bg_label.place(relwidth=1, relheight=1)

    label = tk.Label(history_window, text=history_text, font=("Arial", 12), bg='white')
    label.pack(pady=20)

# Start the Tkinter window
def start_program():
    setup_database()  # Set up the database

    root = tk.Tk()
    root.title("Navigation Options")
    root.geometry("300x300")

    # Load and set background image for main window
    bg_image = tk.PhotoImage(file='bgi.png')
    bg_label = tk.Label(root, image=bg_image)
    bg_label.place(relwidth=1, relheight=1)

    label = tk.Label(root, text="Choose your Destination", font=("Arial", 16), bg='white')
    label.pack(pady=20)

    kfc_button = tk.Button(root, text="KFC", command=lambda: run_ipwebcam("KFC"), width=10, height=2, bg="lightblue", font=("Arial", 14, "bold"))
    kfc_button.pack(pady=10)

    mcd_button = tk.Button(root, text="McDonald's", command=lambda: run_ipwebcam("McDonald's"), width=10, height=2, bg="lightgreen", font=("Arial", 14, "bold"))
    mcd_button.pack(pady=10)

    history_button = tk.Button(root, text="History", command=show_history, width=10, height=2, bg="lightyellow", font=("Arial", 14, "bold"))
    history_button.pack(pady=10)

    root.mainloop()

# Start the Tkinter window
start_program()
