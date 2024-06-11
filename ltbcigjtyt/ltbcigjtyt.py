import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_token = 'Your Slack Token'
client_slack = WebClient(token=slack_token)

def list_channels():
    try:
        response = client_slack.conversations_list()
        channels = response['channels']
        for channel in channels:
            print(f"Name: {channel['name']}, ID: {channel['id']}")
    except SlackApiError as e:
        print(f"Error fetching channels: {e.response['error']}")

def fetch_conversation_history(channel_id):
    try:
        # Fetch conversation history from the channel
        result = client_slack.conversations_history(channel=channel_id)
        conversation_history = result["messages"]
        print(f"{len(conversation_history)} messages found in {channel_id}")
        
        messages_list = []
        for idx, message in enumerate(conversation_history):
            if "subtype" not in message or message["subtype"] not in ["channel_join", "bot_add"]:
                message_dict = {
                    'client_msg_id': message.get('client_msg_id', 'N/A'),
                    'user': message.get('user', 'N/A'),
                    'text': message.get('text', ''),
                    'parent_user_id': message.get('parent_user_id', 'N/A'),
                    'ts': message.get('ts', 'N/A'),
                    'thread_ts': message.get('thread_ts', 'N/A'),
                    'id': str(idx + 1)
                }
                messages_list.append(message_dict)
                
                # Fetch thread replies if there are any
                if 'thread_ts' in message:
                    thread_ts = message['thread_ts']
                    replies = fetch_thread_replies(channel_id, thread_ts)
                    for reply_idx, reply in enumerate(replies):
                        reply_dict = {
                            'client_msg_id': reply.get('client_msg_id', 'N/A'),
                            'user': reply.get('user', 'N/A'),
                            'text': reply.get('text', ''),
                            'parent_user_id': reply.get('parent_user_id', 'N/A'),
                            'ts': reply.get('ts', 'N/A'),
                            'thread_ts': reply.get('thread_ts', 'N/A'),
                            'id': f"{idx + 1}.{reply_idx + 1}"
                        }
                        messages_list.append(reply_dict)
        
        return messages_list
    except SlackApiError as e:
        print(f"Error fetching conversation history: {e.response['error']}")
        return []

def fetch_thread_replies(channel_id, thread_ts):
    try:
        result = client_slack.conversations_replies(channel=channel_id, ts=thread_ts)
        thread_replies = result["messages"][1:] 
        return thread_replies
    except SlackApiError as e:
        print(f"Error fetching thread replies: {e.response['error']}")
        return []

def main():
    list_channels()
    print("___________________________________________")
    channel_id = input("Enter the channel ID: ")
    conversation_history = fetch_conversation_history(channel_id)
    print(conversation_history)

if __name__ == "__main__":
    main()