grab the json file you get as a response from uberRequest.php

TODO PIC

## JSON file descrition


course.name -> The name of the Course
course.childNodes -> course sections
    per childNodes
		.name -> Section Name  ( usually one day)
		childNodes
		    per childNodes: -> subsection?? only one per section in my json files
			    .name -> shoud be the same as section name
			    .learningObjects   -> chapters/lessons of each section
				    per learningObjects:
					    .metadata
						    .name -> Chaptername
							.objective - > Task/Objective for the chapter
							.baseUrl -> Baseurl for the Videofile
							.cookies -> cookies needed for downloading from the baseUrl
							.durationSeconds -> length of the video
						slides: -> info about each slide, including stored notes
						    per slide:
				                .name 
								.notes   -> stored notes for the current slide

from baseURL/script.json we then get the inidivual slides:

slides
    per slides:
		.title -> Title for the current slide
		video: 
		    per video:
			    0 -> slide as 480.mp4
				1 -> slide as 720.mp4
				2 -> slide as 480.webm
				3 -> slide as 720.webm
				per subindex:
		            URI -> the URI for each slide
