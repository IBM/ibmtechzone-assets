Custom Office Add-in’s/plugin to create a custom GenAI solution using WatsonX

Following solution use Yeoman Generator for Office Add-ins (also called "Yo Office") which is an interactive Node.js-based command line tool that creates Office Add-in development projects.

# Setup 
1: Install the generator locally and use the tool. To download/use the tool follow the instructions: https://learn.microsoft.com/en-us/office/dev/add-ins/develop/yeoman-generator-overview

4: Create your ‘yo office’ setup[depends where which add-in we want to create. 
     Ex. Excel/Outlook/Word/PowerPoint/Onenote etc]
5: Now go to your ‘Project-folder’/src/taskpane/ , customise your taskpane.css, taskpane.html, taskpane.js as per your use case. 
Also add one .py file to create a flask service to get data from the UI and send it to LLM for customised response.  
6. When your Setup is ready, it will automatically launch Excel/Powerpoint/Outlook [depends on which service you are creating your customised plugin/add-in]


# Steps to Run :  [Summerization use case]
1> Once your plugin/add-in is integrated with the desired service, you can see the custom HTML/CSS changes if following files are modified inside ‘Project-folder’/src/taskpane/ . [Add files from .zip]
2> Now run your flask service[app.py] is up and ready then, update the same endpoint information in your javascript[integrated in HTML code	.]
3> Now when you click on ‘Summerize Data’ button on the plugin we have added, itwill send the excel data to llm in app.py and display result.


