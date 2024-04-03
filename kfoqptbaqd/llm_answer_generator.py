from ibm_watson import AssistantV2, ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import time
import asyncio

async def generate_llm_answers(questions, api_key, url, env_id):
    try:
        authenticator = IAMAuthenticator(api_key)
        assistant = AssistantV2(
            version='2023-06-15',
            authenticator=authenticator
        )
        assistant.set_service_url(url)

        answers = []
        for question in questions:
            response = assistant.message_stateless(
                assistant_id=env_id,
                input={'message_type': 'text',
                       'text': question
                       }
            ).get_result()
            answer = response['output']['generic'][0]['text']
            print(answer)
            answers.append(answer)
            await asyncio.sleep(1)
            # time.sleep(2)

        return answers
    except ApiException as e:
        raise Exception(f"Watson API error: {e.message}")
    except Exception as e:
        raise Exception(f"Error generating answers: {e}")
