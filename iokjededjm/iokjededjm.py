import praw
from .config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, USERNAME,PASSWORD
from .config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT
from typing import List
import pandas as pd
import psycopg2
from psycopg2 import sql
import warnings
warnings.filterwarnings("ignore")



def get_reddit_client():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        password=PASSWORD,
        username=USERNAME
    )

def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            # sslmode='require',
            # sslrootcert=SSL_ROOT_CERT
        )
        return conn
    except Exception as e:
        return None

def close_db_connection(conn):
    if conn:
        conn.close()
def insert_df_to_table(df, subreddit_handle):
    try:
        connection = connect_to_db()
        
        if connection:
            cursor = connection.cursor()

            # Create table if not exists
            create_table_query = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    reviews TEXT NOT NULL
                );
            """).format(sql.Identifier(subreddit_handle.lower() + '_reddit_posts'))
            cursor.execute(create_table_query)

            # Insert data into the table
            insert_query = sql.SQL("INSERT INTO {} (reviews) VALUES (%s)").format(
                sql.Identifier(subreddit_handle.lower() + '_reddit_posts')
            )
            for row in df.itertuples(index=False):
                cursor.execute(insert_query, (row[0],))  # Assuming only one column 'reviews' exists in df

            connection.commit()

            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()

            cursor.close()
            close_db_connection(connection)
        else:
            print("Failed to connect to the database.")

    except Exception as error:
        raise  # Re-raise the exception to be handled in the calling function

    #print(f"Values inserted successfully into {subreddit_handle.lower() + '_reddit_posts'} table!")
    return 








def fetch_posts_and_comments(subreddit_handle: str, limit: int = 5):
    reddit = get_reddit_client()
    subreddit = reddit.subreddit(subreddit_handle)

    # Fetch posts
    posts = []
    for post in subreddit.hot(limit=limit):
        posts.append([
            post.title, post.score, post.id, str(post.subreddit), post.url,
            post.num_comments, post.selftext, post.created
        ])
    
    df_posts = pd.DataFrame(posts, columns=[
        'title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'
    ])
    
    # Fetch comments for each post
    sub_comments = []
    for post_id in df_posts['id']:
        submission = reddit.submission(post_id)
        sub_comments.append(submission.selftext)
    
    df_comments = pd.DataFrame(sub_comments, columns=[f'{subreddit_handle}_reddit_posts'])
    df_comments = df_comments[df_comments[f'{subreddit_handle}_reddit_posts'].str.strip().astype(bool)]
    
    # Insert DataFrame into PostgreSQL
    insert_df_to_table(df_comments, subreddit_handle)
    
    # Save to CSV if needed
    # csv_filename = f"{subreddit_handle}_reddit_posts_n{limit}_{pd.Timestamp.now().strftime('%m_%d_%y')}.csv"
    # df_comments.to_csv(csv_filename, index=False)
    
    return


