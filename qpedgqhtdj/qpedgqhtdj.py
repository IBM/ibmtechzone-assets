from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from langchain.agents import initialize_agent
from langchain.agents import Tool
from langchain.pydantic_v1 import BaseModel, Field
class BlogPosts(BaseModel):
    """Provides list of all the relevant blog posts and links based on the user query input."""
    query: str = Field(description="list of key words to search the blogpost for.")

def get_post_names(query):
    """Provides list of all the relevant blog posts and links based on the user query input.
    Output can have more than one post titles."""

    # striping off unwanted text if any
    query = query.replace('search terms', '')
    query = query.replace('keywords', '')
    query = query.replace(':', '')
    query = query.replace("'", '')

    posts=[]
    driver = webdriver.Chrome() # Update this with your chromedriver path
    blog_url = "YOUR_BLOG_DOMAIN"
    blog_url = blog_url+"search?q="+query
    # Open the blog website in the browser
    driver.get(blog_url)

    time.sleep(5)  # Wait for 5 seconds to let the page load

    # Find all the search results (assuming search results are represented as links)
    search_results = driver.find_elements(By.CSS_SELECTOR, 'h3')

    # Extract and print the titles of the search results
    print("Titles and links of blog posts:")
    for result in search_results:
        post_title = result.text
        post_link = result.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
#         print(f"Title: {post_title}")
#         print(f"Link: {post_link}")
#         print()
        post_title_link = post_title+":"+post_link
        posts.append(post_title)

    # Close the browser
    driver.quit()

    return {"response": posts}
get_post_names_tool = Tool(
    name="get_posts",
    func=get_post_names,
    description="Provides list of all the relevant blog posts and the links based on the user query input.",
    args_schema = BlogPosts
)
class SinglePost(BaseModel):
    """Given a blog title - find and open the blog in new browser window."""
    link: str = Field(description="link of the blogpost to open in new window")

def open_blog_post_new_window(link):
    """given link for a blog article - open it in new window"""

    # striping off unwanted text if any
    link = link.replace('search terms', '')
    link = link.replace("'", '')

    posts=[]
    driver = webdriver.Chrome() # Update this with your chromedriver path

    driver.get(link)

    time.sleep(5)  # Wait for 5 seconds to let the page load


    return {"response": "Post opened"}
open_blog_post_tool = Tool(
    name="open_blog_post_new_window",
    func=open_blog_post_new_window,
    description="given link for a blog article - open it in new window",
    args_schema = SinglePost
)
tools = [
    get_post_names_tool,
    open_blog_post_tool
]
PREFIX = "<<SYS>> You are smart that selects a function from list of functions based on user queries.\
Run only one function tool at a time or in one query.<</SYS>>\n"
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    max_iterations = 4,
    agent_kwargs={
        'prefix': PREFIX, 
#         'format_instructions': FORMAT_INSTRUCTIONS,
#         'suffix': SUFFIX
    }
)
print(agent.agent.llm_chain.prompt.template)
A = agent.run("Fetch me titles of blog posts relevant to keywords: 'marathon training'. \
I just want the list of titles.\
DO NOT OPEN ANY LINKS.")
