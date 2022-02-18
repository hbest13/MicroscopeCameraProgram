import csv
# work with csv files
tray_file_name = "trays.csv"
filter_file_name = "trayFilters.csv"

fields = []
rows = []

# reading csv file
with open(tray_file_name, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile, skipinitialspace=True)

    # extracting field names through first row
    fields = next(csvreader)

    # extracting each data row one by one
    for row in csvreader:
        rows.append(row)


    # get total number of rows
    print("Total no. of rows: %d" % (csvreader.line_num))

# printing the field names
print('Field names are:' + ', '.join(field for field in fields))

#  printing first 5 rows
print('\nFirst 5 rows are:\n')
for row in rows[:5]:
    # parsing each column of a row
    for col in row:
        print("%10s" % col),
    print('\n')