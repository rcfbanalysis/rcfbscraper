# ===== PARSE 2013 TEAM DATA ==================================================
print "\n"
print "Reading 2013 team file..."
file_name = "2013 cfbstats Statistics/team.csv"
team_file = open(file_name, "r")
data = []
for row in team_file:
	data.append(row.strip("\n").split(","))
team_file.close()

# Find and replace new team names
dif_team_names = [["BYU", "Brigham Young"], ["Miami (Florida)", "Miami (Fla.)"], ["Mississippi", "Ole Miss"], ["USC", "Southern California"]]
for row in data:
	for i in range(0, len(dif_team_names)):
		if dif_team_names[i][0] == row[1]:
			row[1] = dif_team_names[i][1]

file_name = "team_alt.csv"
team_file = open(file_name, "w")
for line in data:
	team_file.write(",".join(line) + "\n")
team_file.close()


# ===== END PARSING ==================================================
print "Done! Press ENTER to continue."
raw_input()