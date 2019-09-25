## JSON file descrition


course.name -> The name of the Course
course.childNodes -> course sections
    per childNodes
		.name -> Section Name
		childNodes
		    per childNodes:
			    .learningObjects   -> chapters/lessons of each section
				    per learningObjects:
					    .metadata
						    .name -> Chaptername
							.objective - > Task/Objective for the chapter
							.baseUrl -> Baseurl for the Videofile
							.cookies -> cookies needed for downloading
