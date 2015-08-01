#install.packages("XML")
#install.packages("dplyr")
#install.packages("RCurl")
library(dplyr)
library(XML)
library(RCurl)

getPBP <- function(url){ #getPBP will pull the table from the play by play web site 
  tab <- readHTMLTable(url,as.data.frame = FALSE)[[3]] # the play by play is the third table on the web page
  if(!is.null(tab)){
    tab <- data.frame(tab,stringsAsFactors = FALSE) # I want to be able to edit strings later so no factors
    names(tab) <- c("Play.Info","Play.Result")
    tab <- rbind(c("First Quarter",NA),tab) # adding this so we can use the same logic for each quarter late
  }
  if(is.null(tab)){ # some times the web page doesn't exist, this is my solution
  	tab <- "none"
  	}
  return(tab)
}

getGameLinks <- function(url){ # getGameLinks finds all links to the game recaps for each game on the scoreboard page
  htmllinks <- getHTMLLinks(url) 
  gamelinks <- c()
  for(i in 1:length(htmllinks)){ # the links to the recaps all have the word "recap" in them so we only want those.
    if(grepl("recap",htmllinks[i])){gamelinks <- c(gamelinks,htmllinks[i])}
  }
  return(gamelinks)
}

cleanPBP <- function(df,home,away,hcode,acode){ # this function changes the raw data to machine readable data
	numplays <- nrow(df) # first we want to initialize everything
	Q <- 1
	off.Points <- 0
	def.Points <- 0
	home.Points <- 0
	away.Points <- 0
	off <- ""
	def <- ""
	playtype <- "dunno"
	playresult <- "Play"
	plays <- c()
	for(i in 1:numplays){
		playtype <- "dunno"
		playresult <- "dunno"
		if(is.na(df[i,"Play.Result"])){ # When the play result is empty it means its the start of the quarter, start of possesion, or scoring drive summary
			if(grepl("Quarter",df[i,"Play.Info"])){
				if(grepl("First",df[i,"Play.Info"])){Q <- 1}
				if(grepl("Second",df[i,"Play.Info"])){Q <- 2}
				if(grepl("Third",df[i,"Play.Info"])){Q <- 3}
				if(grepl("Fourth",df[i,"Play.Info"])){Q <- 4}
			}
			if(grepl("Overtime",df[i,"Play.Info"])){Q <- 5}
			if(grepl(" at ",df[i,"Play.Info"])){ # tells us who is on offense
				off <- unlist(strsplit(df[i,"Play.Info"]," at "))[1]
			}
			#if(grepl("continued",df[i,"Play.Info"])){ # weird quirk in how CBS reports half time
			#	Q <- 3
			#}
			if(grepl("extra point",df[i,"Play.Info"])){ # extra point info is included in the play info, so lets move that
				df[i,"Play.Result"] <- df[i,"Play.Info"]
				df[i,"Play.Info"] <- NA
			}
			if(grepl("Possession",df[i,"Play.Info"])){ # Possession is contained in any scoring summary, so we can find the score of the home and away team
				nums <- grep("^[0-9]",unlist(strsplit(df[i,"Play.Info"]," ")),value = TRUE) # splits the possession summary up and returns only numbers
				away.Points <- as.numeric(nums[1]) # away points is always the first number
				home.Points <- as.numeric(substr(nums[2],1,nchar(nums[2]) - 1)) # there is a comma attached to the home points we need to drop
			}
		}
		if(!is.na(df[i,"Play.Result"])){ 
			info <- unlist(strsplit(df[i,"Play.Info"],"-"))
			if(length(info) == 3){
				down <- info[1]
				distance <- info[2]
				spot <- info[3]
			}
			if(length(info) != 3){ # sometimes the playinfo doesn't contain the down-distance-spot, so we ignore those
				down <- NA
				distance <- NA
				spot <- NA
			}
			if(off == home){
				off.Points <- home.Points
				def.Points <- away.Points
				def <- away
				if(grepl(paste0("-",hcode,"[0-9]"),df[i,"Play.Info"]) & !is.na(spot)){spot <- 100 - as.numeric(unlist(strsplit(spot,hcode))[2])} # if the home team has the ball on their side of the field then they are on the far side of the 50
				else if(!grepl(paste0("-",hcode,"[0-9]"),df[i,"Play.Info"]) & !is.na(spot)){spot <- as.numeric(unlist(strsplit(spot,acode))[2])} # if not then they are close to the endzone
			}
			if(off != home){
				off.Points <- away.Points
				def.Points <- home.Points
				def <- home
				if(grepl(paste0("-",acode,"[0-9]"),df[i,"Play.Info"]) & !is.na(spot)){spot <- 100 - as.numeric(unlist(strsplit(spot,acode))[2])} # if the away team has the ball on their side of the 50 they are far away
				else if(!grepl(paste0("-",acode,"[0-9]"),df[i,"Play.Info"]) & !is.na(spot)){spot <- as.numeric(unlist(strsplit(spot,hcode))[2])} # if not they are close
			}
			if(grepl("50",info[3])){spot <- 50}
			clock <- substr(df[i,"Play.Result"],2,unlist(gregexpr(")",df[i,"Play.Result"])) - 1) # takes the clock info from play result
			###############################################################################################################################
			# The logic for the play type is as follows:																			      #
			# > If there is any mention of a kickoff its a kickoff																		  #
			# > If there is any mention of a punt its a punt																			  #
			# > If there is any mention of an interception its a pass																	  #
			# > If there is any mention of a sack its a pass (this is different than the NCAA which counts sacks as run plays)            #
			# > If there is any mention of rushed it is a run																			  #
			# > If there is any mention of a pass its a pass																			  #
			# > If there is any mention of a field goal its a FG																		  #
			# > If there is any mention of an extra point its an extra point															  #
			# > In my research any time "lost" is used instead of "loss" its a run, but this may not be 100% accurate                     #
			# > If there is any mention of a kickoff its a kickoff 																		  #
			# > Penalties are always mentioned in their own sentence, so if there is only one sentence then the whole play was a penalty, #
			#   not that there was a penalty after a run or something																	  #	
			# > If we still don't know the play then call it a run																		  #	
			###############################################################################################################################
			if(grepl("kicked",df[i,"Play.Result"])){
				playtype <- "Kickoff"
				playresult <- "Return"}
			if(grepl("punt",df[i,"Play.Result"])){
				playtype <- "Punt"
				if(grepl("block",df[i,"Play.Result"])){playresult <- "Blocked"}
				else if(grepl("faircatch",df[i,"Play.Result"])){playresult <- "Fair.Catch"}
				else if(grepl("returned",df[i,"Play.Result"])){playresult <- "Return"}
				else playresult <- "Return"}
			if(grepl("intercepted",df[i,"Play.Result"])){
				playtype <- "Pass"
				playresult <- "Interception"}
			if(grepl("sacked",df[i,"Play.Result"])){
				playtype <- "Pass"
				playresult <- "Sack"}
			if(grepl("rushed",df[i,"Play.Result"])){
				playtype <- "Rush"
				playresult <- "Run"}
			if(grepl("passed",df[i,"Play.Result"])){
				playtype <- "Pass"
				if(grepl("incomplete",df[i,"Play.Result"])){
					playresult <- "Incompletion"}
				if(!grepl("incomplete",df[i,"Play.Result"])){
					playresult <- "Completion"}}
			if(grepl("field goal",df[i,"Play.Result"])){
				playtype <- "Field.Goal"
				if(grepl("block",df[i,"Play.Result"])){playresult <- "Blocked"}
				else if(grepl("missed",df[i,"Play.Result"])){playresult <- "Missed.FG"}
				if(grepl("made",df[i,"Play.Result"])){playresult <- "Made.FG"}}
			if(grepl("extra point",df[i,"Play.Result"])){
				playtype <- "Extra.Point"
				playresult <- "Kick"
				off.Points <- off.Points + 6}
			if(grepl("lost",df[i,"Play.Result"]) & !grepl("sack",df[i,"Play.Result"])){
				playtype <- "Rush"
				playresult <- "Run"}
			if(length(unlist(strsplit(df[i,"Play.Result"],".",fixed = TRUE))) == 1 & grepl("penalized",df[i,"Play.Result"])){
				playtype <- "Penalty"
				playresult <- "Penalty"}
			if(grepl("fumble",df[i,"Play.Result"])){playresult <- "Fumble"}
			if(grepl("Touchdown",df[i,"Play.Result"])){playresult <- "Touchdown"}
			#if(playtype == "dunno"){playtype <- "Rush"}
			playinfo <- c(down,distance,spot,clock,Q,off,def,off.Points,def.Points,playtype,playresult,home.Points,away.Points,df[i,"Play.Info"],df[i,"Play.Result"])
			plays <- rbind(plays,playinfo)
		}
	}
	plays <- data.frame(plays,row.names = NULL,stringsAsFactors = FALSE)
	names(plays) <- c("Down","Distance","Spot","Clock","Quarter","Offense","Defense","Offense.Points","Defense.Points","Play.Type","Result","Home.Team.Points","Away.Team.Points","Play.Info","Play.Result")
	plays$Yards.Spot <- NA
	plays$Yards.Desc <- NA
	for(j in 1:(nrow(plays) - 1)){if(plays[j + 1,"Quarter"] != plays[j,"Quarter"]){plays[j,"Quarter"] <- plays[j + 1,"Quarter"]}}
	for(j in 1:(nrow(plays) - 1)){
		if(!(plays[j,"Play.Type"] == "Kickoff" | plays[j,"Play.Type"] == "Field.Goal" | plays[j,"Play.Type"] == "Punt" | plays[j,"Play.Type"] == "Extra.Point")){
			if(plays[j,"Offense"] == plays[j+1,"Offense"]){
				if(plays[j,"Quarter"] != 2 | plays[j+1,"Quarter"] != 3){
					if(!is.na(plays[j + 1,"Spot"])){
						plays[j,"Yards.Spot"] <- as.numeric(plays[j,"Spot"]) - as.numeric(plays[j + 1,"Spot"])}
					if(is.na(plays[j + 1,"Spot"])){
						plays[j,"Yards.Spot"] <- as.numeric(plays[j,"Spot"]) - 0}
				}
			}
		}
		if(j > 1){
			if(plays[j - 1,"Result"] == "Touchdown" & plays[j + 1,"Play.Type"] == "Kickoff" & plays[j,"Play.Type"] != "Extra.Point"){
				plays[j,"Play.Type"] <- "Two.Point.Attempt"
				plays[j,"Yards.Spot"] <- NA
				plays[j,"Offense.Points"] <- as.numeric(plays[j,"Offense.Points"]) + 6}}
		if(plays[j,"Play.Type"] == "Rush" | plays[j,"Play.Type"] == "Pass"){
			yardinfo <- unlist(strsplit(substr(plays[j,"Play.Result"],8,nchar(plays[j,"Play.Result"]))," "))
			num <- as.numeric(yardinfo[grep("[0-9]",yardinfo)[1]])
			if(plays[j,"Result"] == "Incompletion" | plays[j,"Result"] == "Interception"){plays[j,"Yards.Desc"] <- 0}
			else if(grepl(" loss ", plays[j,"Play.Result"]) | grepl(" lost ", plays[j,"Play.Result"])){plays[j,"Yards.Desc"] <- (-1)*num}
			else if(grepl(" no ",plays[j,"Play.Result"])){plays[j,"Yards.Desc"] <- 0}
			else plays[j,"Yards.Desc"] <- num
		}
	}
	return(plays)
}

			
	

fullPBP <- function(url){ # thins finds all the play by play files of the scoreboard link
  gamelinks <- getGameLinks(url) # finds recap links
  cbs <- "http://www.cbssports.com" # we have to manually stick this in front of the links
  tab <- c()
  for(link in gamelinks){
    link <- paste0(cbs,link)
    recaplink <- unlist(strsplit(link,"recap"))
    pbplink <- paste0(recaplink[1],"playbyplay",recaplink[2])
    rawgame <- getPBP(pbplink) # finds the play by play for that link
    page <- getURL(link) # this finds the home and away team's full name so we can use it later
    title <- substr(page,unlist(gregexpr("<title>",page)),unlist(gregexpr("</title>",page)))
    Away.Name <- unlist(strsplit(unlist(strsplit(title," - "))[2]," at "))[1]
    Home.Name <- unlist(strsplit(unlist(strsplit(title," - "))[2]," at "))[2]
    if(length(rawgame) > 1){ # if there was actually a game returned
		gameinfo <- unlist(strsplit(link,"_"))
      Home.Team <- unlist(strsplit(gameinfo[3],"@"))[2]
      Away.Team <- unlist(strsplit(gameinfo[3],"@"))[1]
      cleandata <- cleanPBP(rawgame,Home.Name,Away.Name,Home.Team,Away.Team)
      cleandata$Date <- gameinfo[2]
      cleandata$Home.Team <- unlist(strsplit(gameinfo[3],"@"))[2]
      cleandata$Away.Team <- unlist(strsplit(gameinfo[3],"@"))[1]
      cleandata$Game.Code <- with(cleandata,paste0(Home.Team,Away.Team,Date))
      tab <- rbind(tab,cleandata)
    }
  }
  return(tab)
}
  
seasonfun <- function(url,weekvec){ # this allows you to find the play by play for multiple weeks at the same time
	data <- c()
	for(i in weekvec){
		weeklink <- paste0(unlist(strsplit(url,"week"))[1],"week",i)
		weekdata <- fullPBP(weeklink)
		weekdata$Week <- i
		data <- rbind(data,weekdata)
	}
	return(data)
}
## to run the code just do
## data <- fullPBP("http://www.cbssports.com/collegefootball/scoreboard/FBS/2013/week15") OR
## postseasondata <- seasonfun("http://www.cbssports.com/collegefootball/scoreboard/FBS/2013/week15",15:17)
