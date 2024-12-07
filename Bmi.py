import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import numpy as np
from matplotlib.patches import Wedge

# Database setup
conn = sqlite3.connect('bmi_calculator.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS bmi_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    name TEXT,
    weight REAL,
    height REAL,
    bmi REAL,
    category TEXT
)
''')
conn.commit()

# BMI calculation and categorization
def calculate_bmi():
    try:
        name = name_entry.get()
        weight = float(weight_entry.get())
        height = float(height_entry.get()) / 100  # Convert to meters
        if weight <= 0 or height <= 0:
            raise ValueError("Weight and height must be positive numbers.")

        bmi = weight / (height ** 2)
        if bmi < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi < 25:
            category = "Normal weight"
        elif 25 <= bmi < 30:
            category = "Overweight"
        else:
            category = "Obesity"

        # Update display
        bmi_label.config(text=f"Your BMI: {bmi:.2f}")
        category_label.config(text=f"Category: {category}")

        # Save to database
        cursor.execute(
            "INSERT INTO bmi_data (timestamp, name, weight, height, bmi, category) VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), name, weight, height, bmi, category)
        )
        conn.commit()

        # Refresh data view
        view_data()

        # Update BMI gauge
        create_bmi_gauge(bmi)

    except ValueError as e:
        messagebox.showerror("Input Error", f"Invalid input: {e}")

# View historical data
def view_data():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT id, timestamp, name, weight, height, bmi, category FROM bmi_data")
    for row in cursor.fetchall():
        tree.insert('', tk.END, values=row)

# Create BMI gauge
# Create BMI gauge
def create_bmi_gauge(bmi):
    ranges = [16, 18.5, 25, 30, 40]
    colors = ['red', 'yellow', 'green', 'orange']
    labels = ['Underweight', 'Normal', 'Overweight', 'Obesity']

    ax.cla()  # Clear the previous chart
    ax.axis('off')  # Hide the axes

    # Adjusted width and radius for wedge segments to avoid overlap
    wedge_width = 0.2  # Narrower wedge width
    radius = 0.7  # Adjusted radius to fit the gauge properly

    # Draw gauge segments
    for i in range(len(ranges) - 1):
        start_angle = 90 - (ranges[i] - 16) * 180 / 24  # Angle calculation for each range
        end_angle = 90 - (ranges[i + 1] - 16) * 180 / 24
        wedge = Wedge((0, 0), radius, start_angle, end_angle, color=colors[i], width=wedge_width)  # Adjusted width
        ax.add_patch(wedge)

        # Adjust label position in the center of each segment
        angle = (start_angle + end_angle) / 2
        x = 0.6 * np.cos(np.deg2rad(angle))  # Adjusted label position closer to center
        y = 0.6 * np.sin(np.deg2rad(angle))
        ax.text(x, y, labels[i], ha='center', va='center', fontsize=6)

    # Draw needle
    needle_angle = 90 - (bmi - 16) * 180 / 24  # Angle for the needle
    ax.plot([0, 0.75 * np.cos(np.deg2rad(needle_angle))],  # Adjusted needle length
            [0, 0.75 * np.sin(np.deg2rad(needle_angle))], color='black', linewidth=2)

    canvas.draw()

# Plot BMI trend
def plot_trend():
    cursor.execute("SELECT timestamp, bmi FROM bmi_data")
    data = cursor.fetchall()
    if not data:
        messagebox.showinfo("No Data", "No BMI data to display.")
        return

    timestamps = [datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in data]
    bmis = [row[1] for row in data]

    plt.figure(figsize=(7, 4))
    plt.plot(timestamps, bmis, marker='o', color='blue')
    plt.title("BMI Trend Over Time")
    plt.xlabel("Date")
    plt.ylabel("BMI")
    plt.grid(True)
    plt.show()

# GUI Setup
root = tk.Tk()
root.title("BMI Calculator")

# Input fields
tk.Label(root, text="Name:").grid(row=0, column=0, padx=10, pady=5)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Weight (kg):").grid(row=1, column=0, padx=10, pady=5)
weight_entry = tk.Entry(root)
weight_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Height (cm):").grid(row=2, column=0, padx=10, pady=5)
height_entry = tk.Entry(root)
height_entry.grid(row=2, column=1, padx=10, pady=5)

# Buttons
calculate_button = tk.Button(root, text="Calculate BMI", command=calculate_bmi)
calculate_button.grid(row=3, column=0, columnspan=2, pady=10)

plot_button = tk.Button(root, text="View BMI Trend", command=plot_trend)
plot_button.grid(row=4, column=0, columnspan=2, pady=10)

# Output
bmi_label = tk.Label(root, text="Your BMI: ")
bmi_label.grid(row=5, column=0, columnspan=2)

category_label = tk.Label(root, text="Category: ")
category_label.grid(row=6, column=0, columnspan=2)

# Historical data table
tree = ttk.Treeview(root, columns=("ID", "Date", "Name", "Weight", "Height", "BMI", "Category"), show='headings')
tree.grid(row=7, column=0, columnspan=2, pady=10)
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=100)

# Create BMI gauge
fig, ax = plt.subplots(figsize=(2, 2))  # Adjusted figure size
ax.axis('off')
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=8, column=0, columnspan=2)

# Populate data view
view_data()

root.mainloop()

# Close database
conn.close()
