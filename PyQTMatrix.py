import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QFileDialog, QCheckBox, QHBoxLayout
from PyQt5 import QtCore, QtGui, QtWidgets
import datetime
import os
import sys
import pandas as pd
date = datetime.date.today()
julian_date = date.toordinal() - datetime.date(date.year, 1, 1).toordinal() + 1


os.chdir("C:/Users/Zachary/OneDrive/Documents/Coding Projects/Improving the Breeding Program")

filenamecross = f"Crosses for the day/Possible_crossings_{julian_date}.csv"

matching_dict_male = {}

with open(filenamecross, newline='') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    for row in reader:
        key = (row[8])  # Use the 2nd and 9th columns as the key
        value = (row[1])  # Use the 3rd and 10th columns as the value
        matching_dict_male[key] = value
        
matching_dict_female = {}

with open(filenamecross, newline='') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    for row in reader:
        key = (row[7])  # Use the 2nd and 9th columns as the key
        value = (row[2])  # Use the 3rd and 10th columns as the value
        matching_dict_female[key] = value

matching_dict = {}

matching_dict.update(matching_dict_male)
matching_dict.update(matching_dict_female)

varieties1 = []
for key, value in matching_dict.items():
    if '-' in key:
        prefix = key.split('-')[0][-2:-1]
        if prefix in ['1', '2']:
            varieties1.append(value)  # use alternate spelling
        else:
            varieties1.append(key)  # use primary spelling
    else:
        varieties1.append(key)  # use primary spelling
        if value:
            varieties1.append(value)  # append alternate spelling if it exists
varieties = [entry.replace('-', '') for entry in varieties1]

# Load matrix from CSV file
matrix = []
with open("MasterPX/matrix5cov.csv", 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        matrix.append(row)

# Filter matrix based on list of varieties
filtered_matrix = [matrix[0]]
for i in range(1, len(matrix)):
    if matrix[i][0] in varieties:
        # Filter the row to only include columns corresponding to the listed varieties
        filtered_row = [matrix[i][0]]
        filtered_row += [matrix[i][j] for j in range(1, len(matrix[i])) if matrix[0][j] in varieties]
        filtered_matrix.append(filtered_row)
filtered_matrix[0] = [matrix[0][j] for j in range(1, len(matrix[i])) if matrix[0][j] in varieties]

matching_varieties = {}

for var in varieties:
    for key in matching_dict.keys():
        if var[-3:] == key[-3:]:
            matching_varieties[key] = var 
            matching_varieties[value] = matching_dict[key]
            break
        
        
new_dict = {value: key for key, value in matching_varieties.items()}       
filtered_matrix[0].insert(0, 'n/a')

df = pd.DataFrame(filtered_matrix)
# set first column as index
df.set_index(0, inplace=True)

# set column names from first row
df.columns = df.iloc[0]

# remove index name
df.index.name = None

# drop first row (since it's now used for column names)
df.drop(df.index[0], inplace=True)

# Rename the row names with the values from the dictionary
df = df.rename(index=new_dict)

# Rename the column names with the values from the dictionary
df = df.rename(columns=new_dict)


# set the working directory
os.chdir("C:/Users/Zachary/OneDrive/Documents/Coding Projects/Improving the Breeding Program")








class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Sorter")
        self.sort_order = {}
        
               # Create a dictionary to store the label widgets for each variety
        self.count_labels = {}
        
        # Create a QVBoxLayout to store the count labels
        self.count_layout = QVBoxLayout()
        
        # Load the tassels dataset and store the male and female tassel counts in a dictionary
        self.tassel_counts = {}
        with open(f"Tassles/Tassles_{julian_date}.csv") as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                variety = row[0]
                male_count = int(row[1]) if row[1].isdigit() else 0  # Handle non-numeric values
                female_count = int(row[2]) if row[2].isdigit() else 0  # Handle non-numeric values
                self.tassel_counts[variety] = {"male": male_count, "female": female_count}
        
                

##############################################################################################################################
        
        
        # Create the table widget
        self.table = QTableWidget()
        self.setCentralWidget(self.table)

        # Create the export button
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_csv)

        # Create the show rejected checkbox
        self.show_rejected_checkbox = QCheckBox("Show rejected")
        self.show_rejected_checkbox.setChecked(False)
        self.show_rejected_checkbox.stateChanged.connect(self.update_table_visibility)

# Create the table widget
        self.table = QTableWidget()
        self.setCentralWidget(self.table)
        # Create the export button
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_csv)
        # Create the show rejected checkbox
        self.show_imbred_checkbox = QCheckBox("Inbred")
        self.show_imbred_checkbox.setChecked(False)
        self.show_imbred_checkbox.stateChanged.connect(self.update_table_visibility)
        
        self.show_ls_checkbox = QCheckBox("Leaf Scald")
        self.show_ls_checkbox.setChecked(False)
        self.show_ls_checkbox.stateChanged.connect(self.update_table_visibility2)
        
        self.show_mosaic_checkbox = QCheckBox("Mosaic")
        self.show_mosaic_checkbox.setChecked(False)
        self.show_mosaic_checkbox.stateChanged.connect(self.update_table_visibility3)
        
        
        # Initialize the report dictionary with all varieties
        self.report = {variety: {"count": 0, "rows": []} for variety in self.tassel_counts}
        self.group_cols = {
            "Misc": [3, 4,5,6,7,8,9],
            "Historical": [10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25],
            "Pedigree": [26,27,33,34,59,62],
            "Theoretical": [28,29,30,31,32, 33,35,36,37,38,39,40,41,42,43,44, 45, 46],
            "Disease": [47,48,49,50,51,52,53,54,60,61],
            "Molecular Data" : [55,56,57,58]
             # Add more groups and corresponding columns as needed
        }
        # Create the toggle group checkboxes
        self.group_checkboxes_layout = QHBoxLayout()
        for group in self.group_cols:
            checkbox = QCheckBox(group)
            checkbox.setChecked(True) # Set the checkbox as checked by default
            checkbox.stateChanged.connect(lambda _, group=group: self.toggle_group_visibility(group))
            self.group_checkboxes_layout.addWidget(checkbox)
        
        # Create the main layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(self.group_checkboxes_layout) # Add the checkboxes layout to the main layout
        layout.addLayout(self.count_layout)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.show_imbred_checkbox)
        button_layout.addWidget(self.show_mosaic_checkbox)
        button_layout.addWidget(self.show_ls_checkbox)
       
        layout.addLayout(button_layout)


        # Add the layout to a widget and set it as the central widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        # Connect the itemChanged signal of the table widget to the update_report method
        self.table.itemChanged.connect(
            lambda item: self.update_report(item, 1, "female") if item.column() == 0 else None
        )
        self.table.itemChanged.connect(
            lambda item: self.update_report(item, 2, "male") if item.column() == 0 else None
        )



       
    def update_report(self, item, column_index, count_key):
    # Get the variety and row index of the checked item from the specified column
        if item and item.column() == 0 and item.row() is not None:
            row_index = item.row()
            variety_item = self.table.item(row_index, column_index)
            variety = variety_item.text() if variety_item is not None else None
            if variety is not None:
                # Update the report dictionary based on the current selection
                    if item.checkState() == QtCore.Qt.Checked:
                        self.report[variety]["count"] += 1
                        self.report[variety]["rows"].append(row_index)
                    else:
                        self.report[variety]["count"] -= 1
                        try:
                            self.report[variety]["rows"].remove(row_index)
                        except ValueError:
                            pass
        
                    # If the number of selected rows equals the total number of rows for the variety, remove all other rows with the same variety
                    count = self.tassel_counts[variety][count_key]
                    if self.report[variety]["count"] == count:
                        for row_index in range(self.table.rowCount()):
                            if row_index not in self.report[variety]["rows"] and self.table.item(row_index, column_index).text() == variety:
                                self.table.hideRow(row_index)
                    else:
                        for row_index in range(self.table.rowCount()):
                            if row_index not in self.report[variety]["rows"] and self.table.item(row_index, column_index).text() == variety:
                                self.table.showRow(row_index)
                                
                                
   




#allows the varaibles to be sorted by clicking the header
    def sort_table(self, column_index):
        # Toggle sort order for the clicked column
        if column_index not in self.sort_order:
            self.sort_order[column_index] = QtCore.Qt.DescendingOrder
        elif self.sort_order[column_index] == QtCore.Qt.AscendingOrder:
            self.sort_order[column_index] = QtCore.Qt.DescendingOrder
        else:
            self.sort_order[column_index] = QtCore.Qt.AscendingOrder

        # Sort the table by the clicked column and sort order
        self.table.sortItems(column_index, self.sort_order[column_index])

        # Update the sort order for the clicked column
        for col, order in self.sort_order.items():
            if col != column_index:
                self.sort_order[col] = None   

    



 


#loads the csv to populate the table
    def load_csv(self, filenamecross):
    # Load the CSV file into the table widget
        with open(filenamecross, newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)[7:]  # Get all headers
            self.table.setColumnCount(len(headers) + 2) 
            self.table.setHorizontalHeaderLabels(["Export"] + headers)
            self.table.setHorizontalHeaderItem(62, QtWidgets.QTableWidgetItem("Kinship Matrix"))
            self.table.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem("F_POLLEN_RATING"))
            self.table.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem("M_POLLEN_RATING"))
            self.table.setHorizontalHeaderItem(16, QtWidgets.QTableWidgetItem("CROSS_FREQUENCY"))
            self.table.setHorizontalHeaderItem(17, QtWidgets.QTableWidgetItem("FEM_EFFICIENCY"))
            self.table.setHorizontalHeaderItem(18, QtWidgets.QTableWidgetItem("MALE_EFFICIENCY"))
            self.table.setHorizontalHeaderItem(19, QtWidgets.QTableWidgetItem("CROSSEFFICIENCY"))
            seen_combinations = {}
            for i, row in enumerate(reader):
                combination = (row[0], row[1])
                if combination in seen_combinations:
                    seen_combinations[combination] += 1
                else:
                    seen_combinations[combination] = 1
                if row[4] == "" and seen_combinations[combination] > 1:
                    continue
                if row[59] == '1' or row[60] == '1' or row[61] == '1':
                    if not self.show_rejected_checkbox.isChecked():
                        continue
                self.table.insertRow(i)
                

                # Add a checkbox to the first column of each row
                checkbox = QTableWidgetItem()
                checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                checkbox.setCheckState(QtCore.Qt.Unchecked)
                checkbox.row_index = i  # Store the original row index as an attribute
                self.table.setItem(i, 0, checkbox)
               
                for j, value in enumerate(row[7:]):
                        item = QTableWidgetItem(value)
                        self.table.setItem(i, j+1, item)
                        # Call matrix() method for each item in the second and third columns
                        if j == 1 or j == 2:
                            self.matrix(item)

    def matrix(self, item):
        # Get the value from the dataframe using the row and column values
        row_index = item.row()
        if row_index >= self.table.rowCount():
            print(f"Error: row_index {row_index} is out of range")
            return
        combination2_item = self.table.item(row_index, 1)
        if combination2_item is None:
            print(f"Error: item at row {row_index}, column 1 is None")
            return
        combination2 = combination2_item.text()
        combination3_item = self.table.item(row_index, 2)
        if combination3_item is None:
            print(f"Error: item at row {row_index}, column 2 is None")
            return
        combination3 = combination3_item.text()
        combination4 = (combination2, combination3)
    
        try:
            value = df.loc[combination4]
        except KeyError:
            print(f"Error: index {combination4} not found in the DataFrame")
            return
    
        new_item = QTableWidgetItem(str(value))
        self.table.setItem(row_index, 62, new_item)



         



#Separates by group
    def toggle_group_visibility(self, group):
        cols = self.group_cols[group]
        is_hidden = self.table.isColumnHidden(cols[0])
        for col in cols:
            self.table.setColumnHidden(col, not is_hidden)


#shows and hides rejects
    def update_table_visibility(self):
        show_imbred = self.show_imbred_checkbox.isChecked()
        for i in range(self.table.rowCount()):
            row = self.table.item(i, 0).row_index
            if self.table.item(i, 59).text() == '1':
                if not show_imbred:
                    self.table.hideRow(i)
                else:
                    self.table.showRow(i)
                
    #shows and hides rejects
    def update_table_visibility2(self):
            show_mosaic = self.show_mosaic_checkbox.isChecked()
            for i in range(self.table.rowCount()):
                row = self.table.item(i, 0).row_index
                if self.table.item(i, 61).text() == '1':
                    if not show_mosaic:
                        self.table.hideRow(i)
                    else:
                        self.table.showRow(i)            
 
    def update_table_visibility3 (self):
            show_ls = self.show_ls_checkbox.isChecked()
            for i in range(self.table.rowCount()):
                row = self.table.item(i, 0).row_index
                if self.table.item(i, 60).text() == '1':
                    if not show_ls:
                        self.table.hideRow(i)
                    else:
                        self.table.showRow(i)                
                
                
                
                
                
#exports csv                 
    def export_csv(self):
        # Export the selected table data to a new CSV file
            filenamecross, _ = QFileDialog.getSavefilenamecross(self, "Export CSV", "", "CSV Files (*.csv)")
            if filenamecross:
                with open(filenamecross, 'w', newline='') as file:
                    writer = csv.writer(file)
                    headers = [self.table.horizontalHeaderItem(j).text() for j in range(1, self.table.columnCount())]
                    writer.writerow(headers)
                    selected_rows = [self.table.item(i, 0) for i in range(self.table.rowCount()) if self.table.item(i, 0).checkState() == QtCore.Qt.Checked]
                    selected_rows.sort(key=lambda item: item.row_index)  # Sort the selected rows by their original row index
                    for checkbox in selected_rows:
                        row_index = checkbox.row_index
                        row = [self.table.item(row_index, j).text() for j in range(1, self.table.columnCount())]
                        writer.writerow(row)
                        self.table.removeRow(row_index)

                



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Load the CSV file into the table widget
    window.load_csv(f"Crosses for the day/Possible_crossings_{julian_date}.csv")

    # Connect the table header clicked signal to the sort_table method
    window.table.horizontalHeader().sectionClicked.connect(window.sort_table)

    sys.exit(app.exec_())

