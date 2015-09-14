import os
import re
import csv

# Returns the contents of a .csv file in an array
def Read_CSV(file_name):
	data = []
	with open(file_name, "r") as csvfile:
		data_reader = csv.reader(csvfile)
		for row in data_reader:
			data.append(row)
	for i in range(0, len(data)):
		for j in range(0, len(data[i])):
			data[i][j] = re.sub("\"", "", data[i][j])
	return data


# Writes the contents of data to a .csv file
def Write_CSV(data, file_name):
	with open(file_name, "w") as csvfile:
		data_writer = csv.writer(csvfile, lineterminator = '\n')
		data_writer.writerows(data)


abbv_arr_1 = Read_CSV("2013 Stats/abbrevations.csv")
abbv_arr_2 = Read_CSV("2014 Stats/abbrevations.csv")
tmp_abbv_arr_1 = abbv_arr_1
tmp_abbv_arr_2 = abbv_arr_2

for abbv_1 in tmp_abbv_arr_1:
	here = False
	for abbv_2 in abbv_arr_2:
		if abbv_1[0] == abbv_2[0]:
			here = True
			break
	if not here:
		abbv_arr_2.append(abbv_1)

for abbv_2 in tmp_abbv_arr_2:
	here = False
	for abbv_1 in abbv_arr_1:
		if abbv_2[0] == abbv_1[0]:
			here = True
			break
	if not here:
		abbv_arr_1.append(abbv_2)

Write_CSV(abbv_arr_1, "2013 Stats/abbrevations.csv")
Write_CSV(abbv_arr_2, "2014 Stats/abbrevations.csv")