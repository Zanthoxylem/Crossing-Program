import tkinter as tk
from tkinter import font

import csv
import datetime
import itertools
import pandas as pd
import os

# Define colors
bg_color = "#4B2E83"
label_color = "#ffffff"
button_color = "#FDD023"

# Define font
custom_font = ("Times New Roman", 22, "bold")


root = tk.Tk()
root.title("Tassel Survey")
root.configure(bg=bg_color)

# Set the window size to 800x600 pixels


# set the working directory
os.chdir("C:/Users/Zachary/OneDrive/Documents/Coding Projects/Improving the Breeding Program")

date = datetime.date.today()
julian_date = date.toordinal() - datetime.date(date.year, 1, 1).toordinal() + 1

def run_pyqt5_app():
    os.system("PyQTMatrix.py")

def submit():
    # Get date and julian date
    date = datetime.date.today()
    julian_date = date.toordinal() - datetime.date(date.year, 1, 1).toordinal() + 1

    # Read can, cart, and bay from CSV file
    with open("Photoperiod_Pos/Photoperiod_Pos_2022.csv", newline="") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    # Find row that matches selected can, cart, and bay
    matching_row = None
    for row in data:
        if row["CAN"] == can_entry.get() and row["CART"] == cart_entry.get() and row["BAY"] == bay_entry.get():
            matching_row = row
            break

    # Get variety from matching row (if found)
    if matching_row is not None:
        variety = matching_row["AVARIETY"]
    else:
        variety = "No match found"

    # Determine sex based on pollen rating
    pollen_rating = int(pollen_entry.get())
    if pollen_rating >= 1 and pollen_rating <= 4:
        sex = "male"
    elif pollen_rating >= 5 and pollen_rating <= 10:
        sex = "female"
    else:
        sex = "unknown"

    # Set the variety label text to the retrieved variety
    variety_label.config(text=variety)

    # Write data to CSV file
    filename = f"tassle_survey_data/tassel_survey_data_{julian_date}.csv"
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["AVARIETY","Can", "Cart", "Bay", "#Tas", "Pollen Rating", "Sex"])
        writer.writerow([ variety, can_entry.get(), cart_entry.get(), bay_entry.get(), tas_entry.get(), pollen_entry.get(), sex])

    # Clear input fields and display success message
    can_entry.set('')
    cart_entry.set('')
    bay_entry.set('')
    tas_entry.set(0)
    pollen_entry.set(0)
    success_label.config(text="Data successfully recorded for the date.")


def preview():
    # Get data from input fields
    bay = bay_entry.get()
    cart = cart_entry.get()
    can = can_entry.get()
    tassels = tas_entry.get()
    pollen_rating = pollen_entry.get()

    # Get variety based on selected bay, cart, and can
    with open("Photoperiod_Pos/Photoperiod_Pos_2022.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["BAY"] == bay and row["CART"] == cart and row["CAN"] == can:
                variety = row["AVARIETY"]
                break
        else:
            variety = "No match found"

    # Determine sex based on pollen rating
    pollen_rating = int(pollen_rating)
    if pollen_rating >= 1 and pollen_rating <= 4:
        sex = "male"
    elif pollen_rating >= 5 and pollen_rating <= 10:
        sex = "female"
    else:
        sex = "unknown"

    # Update the preview label with the selected options
    preview_text = f"Variety: {variety}\nBay: {bay}\nCart: {cart}\nCan: {can}\n"
    preview_text += f"#Tas: {tassels}\nPollen Rating: {pollen_rating}\nSex: {sex}"
    preview_label.config(text=preview_text)


def generate_combinations():
    # Read the CSV file
    filename = f"tassle_survey_data/tassel_survey_data_{date.toordinal() - datetime.date(date.year, 1, 1).toordinal() + 1}.csv"
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    # Extract unique male and female varieties and their tassles count
    male_varieties = {}
    female_varieties = {}
    for row in data:
        variety = row["AVARIETY"]
        sex = row["Sex"]
        tassles = row["#Tas"]
        if sex == "female":
            female_varieties[variety] = tassles
        elif sex == "male":
            male_varieties[variety] = tassles

    # Generate all possible combinations of male and female varieties
    combinations = list(itertools.product(female_varieties, male_varieties))

    # Create a pandas DataFrame with the generated combinations
    df = pd.DataFrame(combinations, columns=["FEMALE", "MALE"])

    # Export the data frame to a new CSV file
    df.to_csv(f"Combinations/Combinations_{julian_date}.csv", index=False)

    # Create a separate CSV file for the tassles data
    tassles_df = pd.DataFrame({
       "AVARIETY": list(male_varieties.keys()) + list(female_varieties.keys()),
       "MALE TASSLES": list(male_varieties.values()) + [""] * len(female_varieties),
       "FEMALE TASSLES": [""] * len(male_varieties) + list(female_varieties.values())
   })
    tassles_df.to_csv(f"Tassles/Tassles_{julian_date}.csv", index=False)



def match_crossings():
    # Read the ZT_CrossingDataset
    with open("CrossingDataset/ZT_CrossingDataset.csv", newline="") as f:
        reader = csv.DictReader(f)
        crossing_data = list(reader)

    # Read the combinations dataset
    combinations = pd.read_csv(f"Combinations/Combinations_{julian_date}.csv")

    # Filter the data based on the male and female varieties in the combinations dataset
    matched_data = []
    for row in crossing_data:
        if row["MALE"] in combinations["MALE"].values and row["FEMALE"] in combinations["FEMALE"].values:
            matched_data.append(row)

    # Check for any male/female combinations that didn't have a match in the crossing data
    missing_combinations = []
    for index, row in combinations.iterrows():
        if row["MALE"] not in [r[0] for r in row] or row["FEMALE"] not in [r[1] for r in row]:
            missing_combinations.append((row["MALE"], row["FEMALE"]))

    # Create a pandas DataFrame with the matched data
    matched_df = pd.DataFrame(matched_data)

    # Add missing data to the DataFrame
    for male, female in missing_combinations:
        male_data = {}
        female_data = {}
        for row in crossing_data:
            if row["MALE"] == male:
                male_data = {k: v for k, v in row.items() if k.startswith("M")}
            if row["FEMALE"] == female:
                female_data = {k: v for k, v in row.items() if k.startswith("F") and not k.endswith("UZZ")}
            if male_data and female_data:
                break
        matched_df = matched_df.append({"MALE": male, "FEMALE": female, **male_data, **female_data}, ignore_index=True)

    # Add an inbred column based on matching MFP/FMP or MMP/FFP
    inbred = []
    for index, row in matched_df.iterrows():
        if ((row["MFP"] != "NA" and row["FFP"] != "NA" and row["MFP"] == row["FFP"]) or (row["MMP"] != "NA" and row["FMP"] != "NA" and row["MMP"] == row["FMP"] or (row["MFP"] != "NA" and row["FFP"] != "NA" and row["MMP"] != "NA" and row["FMP"] != "NA" and row["MFP"] == row["MALE"] or row["FFP"] == row["MALE"] or row["MMP"] == row["MALE"] or row["FMP"] == row["MALE"] or row["MFP"] == row["FEMALE"] or row["FFP"] == row["FEMALE"] or row["MMP"] == row["FEMALE"] or row["FMP"] == row["FEMALE"]))):
            inbred.append(1)
        else:
             inbred.append(0)
    matched_df["inbred"] = inbred
    
    MOSAICSUS = []
    for index, row in matched_df.iterrows():
        if ((row["MMOS"] != "NA" and row["FMOS"] != "NA" and row["MMOS"] == row["FMOS"]) and (row["MMOS"] == "S" and row["FMOS"] == "S" and row["MMOS"] == row["FMOS"])):
            MOSAICSUS.append(1)
        else:
             MOSAICSUS.append(0)
    matched_df["MOSAICSUS"] = MOSAICSUS
    
    LFSUS = []
    for index, row in matched_df.iterrows():
        if ((row["MLS"] != "NA" and row["FLS"] != "NA" and row["MLS"] == row["FLS"]) and (row["MLS"] == "S" and row["FLS"] == "S" and row["MLS"] == row["FLS"])):
            LFSUS.append(1)
        else:
             LFSUS.append(0)
    matched_df["LFSUS"] = LFSUS

    
    matched_df = matched_df.replace("NA", "")

    # Export the data frames to new CSV files
    matched_df.to_csv(f"Crosses for the day/Possible_crossings_{julian_date}.csv", index=False)


def Cross():
    generate_combinations()
    match_crossings()
    


# Add padding around grid elements
for i in range(13):
    root.grid_rowconfigure(i, pad=5)

root.grid_columnconfigure(0, pad=10)
root.grid_columnconfigure(1, pad=10)





variety_label = tk.Label(root, text="Previous Entry: ")
variety_label.grid(row=3, column=0)

bay_label = tk.Label(root, text="Bay (1-6):")
bay_label.grid(row=4, column=0)


bay_entry = tk.StringVar(root)
bay_entry.set("1")

bay_buttons_frame = tk.Frame(root)
bay_buttons_frame.grid(row=4, column=1)

bay_buttons = []

bay_buttons = []
for i in range(1, 7):
    bay_button = tk.Radiobutton(bay_buttons_frame, text=str(i), variable=bay_entry, value=str(i), command=preview, fg="Black", activebackground="White", activeforeground="Black", bg = "Black")
    bay_button.pack(side="left")
    bay_buttons.append(bay_button)

cart_label = tk.Label(root, text="Cart (A, B, C):")
cart_label.grid(row=5, column=0)


cart_entry = tk.StringVar(root)
cart_entry.set("A")

cart_buttons_frame = tk.Frame(root)
cart_buttons_frame.grid(row=5, column=1)

cart_buttons = []
for cart in ["A", "B", "C"]:
    cart_button = tk.Radiobutton(cart_buttons_frame, text=cart, variable=cart_entry, value=cart, command=preview, fg="Black", activebackground="White", activeforeground="Black", bg = "Black")
    cart_button.pack(side="left")
    cart_buttons.append(cart_button)

can_label = tk.Label(root, text="Bucket Number (1-18):")
can_label.grid(row=6, column=0)


can_entry = tk.StringVar(root)
can_entry.set("1")

can_buttons_frame = tk.Frame(root)
can_buttons_frame.grid(row=6, column=1)

can_buttons = []
for i in range(1, 19):
    can_button = tk.Radiobutton(can_buttons_frame, text=str(i), variable=can_entry, value=str(i), command=preview, fg="Black", activebackground="White", activeforeground="Black", bg = "Black")
    can_button.pack(side="left")
    can_buttons.append(can_button)

tas_label = tk.Label(root, text="#Tas:")
tas_label.grid(row=7, column=0)


tas_entry = tk.IntVar(root)
tas_entry.set(0)

tas_buttons_frame = tk.Frame(root)
tas_buttons_frame.grid(row=7, column=1)

tas_buttons = []
for i in range(1, 11):
    tas_button = tk.Radiobutton(tas_buttons_frame, text=str(i), variable=tas_entry, value=i, command=preview, fg="Black", activebackground="White", activeforeground="Black", bg = "Black")
    tas_button.pack(side="left")
    tas_buttons.append(tas_button)

pol_label = tk.Label(root, text="Pollen Rating:")
pol_label.grid(row=8, column=0)


pollen_entry = tk.IntVar(root)
pollen_entry.set(0)
pollen_buttons_frame = tk.Frame(root)
pollen_buttons_frame.grid(row=8, column=1)

pollen_buttons = []
for i in range(1, 11):
    pollen_button = tk.Radiobutton(pollen_buttons_frame, text=str(i), variable=pollen_entry, value=i, command=preview, fg="Black", activebackground="White", activeforeground="Black", bg = "Black")
    pollen_button.pack(side="left")
    pollen_buttons.append(pollen_button)



submit_button = tk.Button(root, text="Submit", command=submit, fg="Black")
submit_button.grid(row=9, column=1)

success_label = tk.Label(root, text="")
success_label.grid(row=10, column=1, columnspan=1)


preview_label = tk.Label(root, text="")
preview_label.grid(row=11, column=1, columnspan=1)

generate_button = tk.Button(root, text="Determine Crosses for the Day", command=Cross, fg="Black")
generate_button.grid(row=12, column=0)



run_pyqt5_button = tk.Button(root, text="Generate Report", command=run_pyqt5_app, fg="Black")
run_pyqt5_button.grid(row=12, column=2)


# Modify labels, buttons, and frames for better appearance
variety_label.config(bg=bg_color, font=custom_font, fg=label_color)
bay_label.config(bg=bg_color, font=custom_font, fg=label_color)
cart_label.config(bg=bg_color, font=custom_font, fg=label_color)
can_label.config(bg=bg_color, font=custom_font, fg=label_color)
tas_label.config(bg=bg_color, font=custom_font, fg=label_color)
pol_label.config(bg=bg_color, font=custom_font, fg=label_color)
success_label.config(bg=bg_color, font=custom_font, fg=label_color)
preview_label.config(bg=bg_color, font=custom_font, fg=label_color)

bay_buttons_frame.config(bg=bg_color)
cart_buttons_frame.config(bg=bg_color)
can_buttons_frame.config(bg=bg_color)
tas_buttons_frame.config(bg=bg_color)
pollen_buttons_frame.config(bg=bg_color)

for button in bay_buttons + cart_buttons + can_buttons + tas_buttons + pollen_buttons:
    button.config(bg=button_color, font=custom_font, indicatoron=0, width=2, padx=2, pady=2, relief="flat")

submit_button.config(bg=button_color, font=custom_font, padx=5, pady=5)
generate_button.config(bg=button_color, font=custom_font, padx=5, pady=5)
run_pyqt5_button.config(bg=button_color, font=custom_font, padx=5, pady=5)

root.mainloop()
