from os import listdir
from os.path import isdir, isfile, join
import csv
import re


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

# MAIN
paths = ["./pbp/", "./drive/"]
for i in range(0,len(paths)):
	path = paths[i]
	print path
	game_files = [f for f in listdir(path) if isfile(join(path, f))]
	for game_file in game_files:
		if game_file[len(game_file)-4:len(game_file)] != ".csv":
			continue
		print "Analyzing " + str(game_file)
		pbp_file = path + game_file
		pbp_data = Read_CSV(pbp_file)
		try:
			if int(long(pbp_data[0][0]) % 1e8) == 0:
				print pbp_data[0][0]
				print game_file[0:len(game_file)-4]
				raw_input()
				pbp_data[0][0] = game_file[0:len(game_file)-4]
				Write_CSV(pbp_data, game_file)
		except:
			print pbp_data[0][0]
			print game_file[0:len(game_file)-4]
			raw_input()
			pbp_data[0][0] = game_file[0:len(game_file)-4]
			Write_CSV(pbp_data, path + game_file)