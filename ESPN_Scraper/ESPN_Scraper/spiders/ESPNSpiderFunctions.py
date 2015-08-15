


def Extract_Team_Code(game_code, team):
	if team == "v":
		return int(int(math.floor(float(game_code)/1e12)))
	elif team == "h":
		return int(int(math.floor(float(game_code)/1e8)) % 1e4)
	else:
		flag = raw_input("h or v?")
		return Extract_Team_Code(game_code, flag)