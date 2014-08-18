#install.packages("XML")
#install.packages("dplyr")
library(dplyr)
library(XML)
library(RCurl)

getPBP <- function(url){
  tab <- readHTMLTable(url,as.data.frame = FALSE)[[3]]
  if(!is.null(tab)){
    tab <- data.frame(tab,stringsAsFactors = FALSE)
    names(tab) <- c("Play.Info","Play.Result")
    tab <- rbind(c("First Quarter",NA),tab)
  }
  if(is.null(tab)){
  	tab <- "none"
  	}
  return(tab)
}

getGameLinks <- function(url){
  htmllinks <- getHTMLLinks(url)
  gamelinks <- c()
  for(i in 1:length(htmllinks)){
    if(grepl("recap",htmllinks[i])){gamelinks <- c(gamelinks,htmllinks[i])}
  }
  return(gamelinks)
}

cleanPBP <- function(df,home,away,hcode,acode){
	numplays <- nrow(df)
	Q <- 1
	off.Points <- 0
	def.Points <- 0
	home.Points <- 0
	away.Points <- 0
	off <- ""
	def <- ""
	plays <- c()
	for(i in 1:numplays){
		if(is.na(df[i,"Play.Result"])){
			if(grepl("Quarter",df[i,"Play.Info"])){
				if(grepl("First",df[i,"Play.Info"])){Q <- 1}
				if(grepl("Second",df[i,"Play.Info"])){Q <- 2}
				if(grepl("Third",df[i,"Play.Info"])){Q <- 3}
				if(grepl("Fourth",df[i,"Play.Info"])){Q <- 4}
			}
			if(grepl("Overtime",df[i,"Play.Info"])){Q <- 5}
			if(grepl(" at ",df[i,"Play.Info"])){
				off <- unlist(strsplit(df[i,"Play.Info"]," at "))[1]
			}
			if(grepl("continued",df[i,"Play.Info"])){
				off <- unlist(strsplit(df[i,"Play.Info"]," continued"))[1]
			}
			if(grepl("extra point",df[i,"Play.Info"])){
				df[i,"Play.Result"] <- df[i,"Play.Info"]
			}
			if(grepl("Possession",df[i,"Play.Info"])){
				nums <- grep("^[0-9]",unlist(strsplit(df[i,"Play.Info"]," ")),value = TRUE)
				home.Points <- as.numeric(nums[1])
				away.Points <- as.numeric(substr(nums[2],1,nchar(nums[2]) - 1))
			}
		}
		if(!is.na(df[i,"Play.Result"])){	
			info <- unlist(strsplit(df[i,"Play.Info"],"-"))
			if(length(info) == 3){
				down <- info[1]
				distance <- info[2]
				spot <- info[3]
			}
			if(length(info) != 3){
				down <- NA
				distance <- NA
				spot <- NA
			}
			if(off == home){
				off.Points <- home.Points
				def.Points <- away.Points
				def <- away
				if(grepl(hcode,spot)){spot <- 100 - as.numeric(substr(spot,nchar(spot) - 1,nchar(spot)))}
				if(!grepl(hcode,spot)){spot <- as.numeric(substr(spot,nchar(spot) - 1,nchar(spot)))}
			}
			if(off != home){
				off.Points <- away.Points
				def.Points <- home.Points
				def <- home
				if(grepl(acode,spot)){spot <- 100 - as.numeric(substr(spot,nchar(spot) - 1,nchar(spot)))}
				if(!grepl(acode,spot)){spot <- as.numeric(substr(spot,nchar(spot) - 1,nchar(spot)))}
			}
			playtype <- "dunno"
			playresult <- "Play"
			clock <- substr(df[i,"Play.Result"],2,unlist(gregexpr(")",df[i,"Play.Result"])) - 1)
			if(grepl("kicked",df[i,"Play.Result"])){
				playtype <- "Kickoff"
				playresult <- "Return"}
			if(grepl("punt",df[i,"Play.Result"])){
				playtype <- "Punt"
				playresult <- "Return"}
			if(grepl("intercepted",df[i,"Play.Result"])){
				playtype <- "Pass"
				playresult <- "Turnover"}
			if(grepl("sacked",df[i,"Play.Result"])){playtype <- "Pass"}
			if(grepl("rushed",df[i,"Play.Result"])){playtype <- "Rush"}
			if(grepl("passed",df[i,"Play.Result"])){playtype <- "Pass"}
			if(grepl("field goal",df[i,"Play.Result"])){
				playtype <- "Field.Goal"
				playresult <- "Kick"}
			if(grepl("extra point",df[i,"Play.Result"])){
				playtype <- "Extra.Point"
				playresult <- "Kick"
				off.Points <- off.Points + 6}
			if(grepl("lost",df[i,"Play.Result"])){playtype <- "Rush"}
			if(length(unlist(strsplit(df[i,"Play.Result"],".",fixed = TRUE))) == 1 & grepl("penalized",df[i,"Play.Result"])){playtype <- "Penalty"}
			if(grepl("recovered",df[i,"Play.Result"])){playresult <- "Turnover"}
			if(grepl("Touchdown",df[i,"Play.Result"])){playresult <- "Touchdown"}
			if(playtype == "dunno"){playtype <- "Rush"}
			playinfo <- c(down,distance,spot,clock,Q,off,def,off.Points,def.Points,playtype,playresult,home.Points,away.Points,df[i,"Play.Info"],df[i,"Play.Result"])
			plays <- rbind(plays,playinfo)
		}
	}
	plays <- data.frame(plays,row.names = NULL,stringsAsFactors = FALSE)
	names(plays) <- c("Down","Distance","Spot","Clock","Quarter","Offense","Defense","Offense.Points","Defense.Points","Play.Type","Result","Home.Team.Points","Away.Team.Points","Play.Info","Play.Result")
	return(plays)
}

			
	

fullPBP <- function(url){
  gamelinks <- getGameLinks(url)
  cbs <- "http://www.cbssports.com"
  tab <- c()
  for(link in gamelinks){
    link <- paste0(cbs,link)
    recaplink <- unlist(strsplit(link,"recap"))
    pbplink <- paste0(recaplink[1],"playbyplay",recaplink[2])
    rawgame <- getPBP(pbplink)
    page <- getURL(link)
    title <- substr(page,unlist(gregexpr("<title>",page)),unlist(gregexpr("</title>",page)))
    Away.Name <- unlist(strsplit(unlist(strsplit(title," - "))[2]," at "))[1]
    Home.Name <- unlist(strsplit(unlist(strsplit(title," - "))[2]," at "))[2]
    if(length(rawgame) > 1){
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
  
seasonfun <- function(url,weekvec){
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
