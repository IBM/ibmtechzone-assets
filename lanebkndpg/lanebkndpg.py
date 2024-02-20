import requests
import urllib.request
from dotenv import load_dotenv
import os

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from ibm_cloud_sdk_core import IAMTokenManager
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator, BearerTokenAuthenticator

import logging
import streamlit as st

def generate(input, model_id, parameters):

    api_key = os.environ["ibm_cloud_api_key"]
    project_id = os.environ["project_id"]

    access_token = IAMTokenManager(
        apikey = api_key,
        url = "https://iam.cloud.ibm.com/identity/token"
    ).get_token()

    wml_url = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-28"
    Headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "model_id": model_id,
        "input": input,
        "parameters": parameters,
        "project_id": project_id
    }
    response = requests.post(wml_url, json=data, headers=Headers)
    print(response)
    if response.status_code == 200:
        return response.json()["results"][0]["generated_text"]
    else:
        return ""

def main(complaint):
    summary_result = ""
    sentiment_result = ""
    tone_result = ""
    urgency_result = ""
    rca_result = ""
    investigation_result = ""
    resolution_result = ""

    load_dotenv()
    
    # Do something with the entered text (e.g., process, store, or display it)
    input = "provide short summary of below customer complaint.\n\"" + complaint + "\""
    #print(input)
    model_id = "meta-llama/llama-2-70b-chat"
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 400,
        "min_new_tokens": 1,
        "repetition_penalty": 1,
        "beam_width": 1
    }

    summary_result = generate(input, model_id, parameters)
    #print(summary_result)

    #Evaluate Sentiment of the complaint
    input = "Provide sentiment of the below customer complaint.\n\"" + complaint + "\"\n"
    model_id = "google/flan-t5-xxl"
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 20,
        "min_new_tokens": 1,
        "repetition_penalty": 2,
        "beam_width": 1
    }

    sentiment_result = generate(input, model_id, parameters)
    
    #Evaluate Tone of the Complaint
    input = "Provide 1 sentence summary about the tone of the below customer complaint.\n\"" + complaint + "\"\n"
    model_id = "meta-llama/llama-2-70b-chat"
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 50,
        "min_new_tokens": 1,
        "repetition_penalty": 1,
        "beam_width": 1
    }
    
    tone_result = generate(input, model_id, parameters)

    #Ealuate urgency of the given customer complaint
    input = "Classify below text as urgent if it shows urgency else classify it as non-urgent.\n\"" + complaint + "\""
    model_id = "google/flan-ul2"
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 10,
        "min_new_tokens": 1,
        "repetition_penalty": 1,
        "beam_width": 1
    }
    print(input)
    urgency_result = generate(input, model_id, parameters)

    #Classify the given Customer complaint
    input = '''Classify below text as "Card blocked without customer intimation" or "Dormancy closure without customer intimation" or "Incorrect Customer Contact Details" or "Incorrect Regular Payment setup" or "Non-delivery of replacement card"

Input:
The bank closed my credit card without my authorization. When new card was sent out, which I did not receive. Several unauthorized transactions totaling over 18,000 dollars were made. Report of unauthorized atm/check card was made but bank took not further action. Two years later I still have not heard from the bank. To this day, I still have not received a dime from the bank.

Output:
Card blocked without customer intimation

Input:
I am a XXXX XXXX resident who works in XXXX XXXX. \nI have had both checkings and savings accounts with M & T Bank for several years. For the past several weeks, I have been experiencing issues using my checking account. I XXXX noticed this problem when attempting to purchase groceries at my local XXXX supermarket about a month or so ago. When I chose the credit option, my card was declined. I knew my account had more than enough money to cover my groceries, so I instinctively used the debit option, and the transaction approved. Every week since then, I have experienced the same issue, despite purchasing groceries every Friday at the same supermarket, around the same time of day for the past year. \nLast week, I went to purchase crabs for {$100.00} and once again, my card was declined under credit although I had the funds. I instead used another credit card. I called M & T Customer service who informed me that due to high fraud activity in the area, M & T would not allow credit transactions, and that I have to use debit because entering my PIN verifies my identity. The customer service agent could not confirm where the fraud was occurring or how long the bank would inhibit credit transactions. \nRecently, I treated my boyfriend to dinner at XXXX XXXX in XXXX. Our bill was {$180.00}. When I attempted to pay, the waiter informed me that my transaction kept showing an error and requested I used a different card. As you can probably imagine, this was extremely embarrassing. Once again, I resorted to using another credit card. Knowing I had the funds in my account to more than cover the bill for the meal, I called M & T Customer Service after leaving the restaurant. XXXX XXXX employee ID XXXX ) informed me that my card was declined due to fraud in the area. Once again, XXXX could not inform me where the fraud was occurring XXXX please note my transactions fail in both XXXX and XXXX XXXX XXXX and he could not confirm for how long or the monetary amount these transactions would be stopped for. XXXX also informed me that the next time I go out to eat, I should call M & T Bank and ask them to allow the transaction to go through. I informed XXXX that this is unacceptable and also asked him what I should do if my transactions fail when customer service is closed. He then suggested I take out cash or ask the company to do smaller transactions that cover the whole bill. I informed XXXX that this is ludicrous and that I do n't feel comfortable going to the ATM late at night or walking around with large amounts of cash. I asked XXXX if there is anything that could be done and he told me no. We ended the call. \nI then called my sister and mother, who stated they have been experiencing the same issues with M & T Bank. My sister suggested I contact the Attorney General. When I called M & T back and informed XXXX that I would be contacting the Attorney General, he no longer decided nothing could be done. He transferred me to his supervisor, who informed me she would place a \" fraud exclusion '' on my account, which would now allow me to make purchases on my card without problems. \nI highly suspect that these issues are not truly fraud related or preventative. M & T never sent me notification that fraud was a concern and that I would only be able to use debit. Additionally, M & T used to allow my transactions to go through, and would email me about potential fraud relating to the completed transaction. I was fine with this approach. I do not agree with M & T stopping me from being able to use MY money that I work hard for in the manner that I please. M & T was recently in the news for charging erroneous overdraft fees to their consumers. It appears M & T is continuing unethical business practices towards consumers.

Output:
Card blocked without customer intimation

Input:
Several times now I have had credit and debit cards cancelled and new numbers issued, with very little explanation or information given by the issuing agent. This has happened with bank  XXXX, a XXXX Debt card in the past year and multiple times with Citizens Bank XXXX Citizens XXXX. \nTo be specific for this complaint. Yesterday I tried to use my Citizens debit card to buy gas at a local station. The card was declined. The manager thought it was the processor on his gas pump and had me switch pumps. Card declined again. He had me come in to the store and he tried manually - card declined. Finally I pulled out a 20 % interest credit card not related to bank and paid for gas with that. \nThis morning I contacted Citizens and was told that my card was \" flagged '' because of some sort of breach and used terms that were very generic like \" suspicious activity. '' I have seen nothing on my statements or online account information ( I check my account online almost every day as a rule ) involving unauthorized charges. I was given a supervisor who worked with me to allow two charges to be reprocessed, but also told me my newspaper subscription attempt had been declined overnight, and contacting the newspaper to recharge would have been time consuming - she wanted to get me my new card \" overnight. '' I asked WHO used my card or attempted to use it, and/or which company that I trusted with this information was breached or hacked. Even when I was given to a supervisor I was told Citizens had no information, that XXXX was the entity directing the card be cancelled and replaced. Before I hung up, I asked about another account with the bank and was told that THAT debit card - a second card with a second account - was ALSO \" flagged '' to be replaced. \n\nI contacted XXXX and was told that they could connect me to Citizens to explain how the cards were compromised. bank blames XXXX, XXXX blames bank  and I ca n't learn the manner my account information was \" compromised '' and in what way. I understand that hackers break into banks and vendors and steal numbers. I want to know WHICH bank or vendor was vulnerable. I believe it 's my right to know ; that if I am to be careful or cautious I have a right to know how this happened. Furthermore, if we are looking at patterns here, it will keep happening and when it does, I want to know when, who, and how.

Output:
Card blocked without customer intimation

Input:
I was shocked to see my business account closed without any intimation .  I would like to get it re-instated ASAP /\nAlso, need a full explanation on why this account was closed in the first place

Output:
Dormancy closure without customer intimation

Input:
I lost my husband in 2007 and from the proceeds of his will, a trustee account was setup in 2011 to which a deposit of 4377772 pounds was made into this account. I setup the account for my sons , one of whom has Cri-Du-chat syndrome. At the time of the opening the account, I made it clear that the use of funds would be minimal and very infrequent. I noticed i had not received annual bank statement and hence enquired with the bank. I was distressed to hear that the account has been closed due to dormancy. I was given know further information , nor what has happened to the funds. This has raised the memories of my husband death all over again. A simple intimation from the bank would have avoided all the pain for our family.  I hope we can resolve this urgently .

Output:
Dormancy closure without customer intimation

Input:
I was surprised to find out my card was blocked. I called the branch and was told my account has been closed.\nTruly shocking. I enquired the reason and was told the account was closed to non-use for specified period.\nI am left with no access to my account . I was never informed about  the closure before or after the fact. Do you guys even have a policy for the same ?

Output:
Dormancy closure without customer intimation

Input:
Good evening, I moved into my address six months ago  and since then bank has been sending letters addressed to a company called XXY Limited. I know this company pertains to the previous owner of the house and even more frustratingly , her correct compnay address has been updated on Companies House and is pulickly available. For six months, I have sent back the letters to bank  .. yet they still keep coming.So, having got 2 new letters yesterday, I went in branch and handed them over to sfaff who said they will mark on the account hat the person  had gone away. AS I have no end of problems with old owners and not their bank accounts, I said in passing that that culd I just confirm that if there were any issues with this account, I take it issues wuld go against the name and not our address. The lady at the branch told me that it would go against both. I questioned this and said that seeing as I was telling bank that this person no longer resided at our address , how could any makr be placed agsinst it or bailiffs' be sent around ? she said shoud woudl try and contact the customer to update tbut said that it was just unfortunate . I was horrified so rang up and managed to get through to the same branch - the lady was very helpful but could only say that she would do everything to update the address by calling the customer .i compalined through Twitter and while your Twitter person was happy to confirm that wwe woudl no longer receive any more letter or marketing for that account, they would not confirm the matter of black marks or bailiff and cited data protection. i find this astounding. Having dealt with other banks on matter concerning the ex-owner, they have been more than happy to  provide reassurance that there will no come back back on us oru our addreess. However, bank is doing exactly opposite of that.

Output:
Incorrect Customer Contact Details

Input:
I have received 3 letters entitled ' funds transfer debit advice ' with a name different from mine. Please note the transactions are also not posted to my bank account . I  contacted bank fraud team which advised me to Branch for resolution.I was advised to send these letter back with the mark ' Not known at this address' which I did.  I was assured that the letters would now stop. \nToday, I again received 2 more letters addresses to the same person . Cna you fix this please?

Output:
Incorrect Customer Contact Details

Input:
I am not a bank customer . But I suspect one of your customer is registered with my address. In the past I have receieved loan repayment letters for the person at my address. I am not aware of this person . I had sent the letter back to Bank at that point. Now I am applying for a loan with Bank of Ireland and the application is getting declined to the bank customer registered under my address and it has affected muy credit score. I want to get this sorted out as soon as possible.

Output:
Incorrect Customer Contact Details

Input:
I had cancelled the instructions due to a dispute with my othe bank and had suspended my STO for the time being.\nI got that resolved and had instructured my bank to re-instate the STO from last month onwards. \nMy instructions to re-instate a STO to transfer funds to other bank account were not actioned.\nHave missed out on additional interest income due to the non-transfer.\nI would like to get a confirmation that the STO has now been re-instated and compensation for the lost interest of the 53.4 £ 

Output:
Incorrect Regular Payment setup

Input:
I had requested the bank to amend the standing order for British Council for this month to cover my additional charges for seminar registration.\nBut I got a message that the STO itself has been cancelled . Whats happening? Can you rectify before the due date?

Output:
Incorrect Regular Payment setup

Input:
I have sent a written instructions for a new Standing order to settle my council bills. I got a letter saying the request for setup could not be completed due to missing information but did not actually mention any specifics? Can you urgently help since the bill are due this week.

Output:
Incorrect Regular Payment setup

Input:
I wrote a secure message from my online account yesterday saying that my debit card was due to expire that day and I had not received a new card.  I asked how should I go about getting another photo card . I was informed that I would get a reply within 48 hours. I tried to login online today and repeatedly told my details do not match your system. I can only conclude that my card has expired since I can no longer access my account online with it. If this is the case, how can I possobly acccess the reply to my secure message . Further more , why was this not mentioend in the auto-response I received when I was told I would get a reply within 48 hours.Surely I am not the first person whose card has expired and new card has not arrvied before hand.I would appreciate if you please contact me by phone as soon as possible to tell me when my replacement card and I assume separately a new pin number also, will be sent to me .Thanks you

Output:
Non-delivery of replacement card

Input:
Mt debit card has expired in the Dominican Republic. I cant make international calls to banks because the system here is not able to cope with the automated systems. I  need a new card in UK. I tried webchat and they told me the only way is to contact the Customer Service via telephone. This is a a problem. I need someone to contact me please

Output:
Non-delivery of replacement card

Input:
I went to hotel with her expired card and while swiping the card I realized that card is expired. I havent receieved the card which was sent 2 weeks before expiry. Not got any communication. I had to ask my colleague to pay for the bills.

Output:
Non-delivery of replacement card

Input:

''' + complaint
    
    model_id = "google/flan-ul2"
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 50,
        "min_new_tokens": 1,
        "repetition_penalty": 1,
        "beam_width": 1
    }
    print(input)
    rca_result = generate(input, model_id, parameters)
    rca_result = rca_result.replace("Output: ", "")

    # Generate investigation steps
    input = '''Provide investigation steps for the given Customer Complaint.

I recently lost a card in bank ATM and raised a request for replacment card. I was surpised to receive a replacement card for my wife instead of me.I need the card urgently before the Easter weekend since I am going on a vacation.

1. Check customer card history 
2. Check if card replacement has been requested 
3. Check if card was blocked 
4. Check if customer is eligible for D&I

My card has been declined while making a payment . I called the bank and found out that my card has been reported lost ! and has been blocked . It was my husband who had reported a card lost 2 days go. Has there been a mix-up?I want her card to be re-instated and an explanation why this happened. I am travelling for the next 3 weeks and would need this  to be sorted out urgently.

1. Check card history of both wife and husband 
2. Check if the correct card was blocked by the bank

My husband had called the bank earlier this week to get this card on the joint account cancelled. When I used my card yestreday in a shop it got declined. What has happened? Have you guys blocked my card?

1. Check customer card history 
2. Check if card replacement has been requested 
3. Check if the correct card was blocked by the bank 
4. Check if customer is eligible for D&I

My card has been declined while making a payment . I called the bank and found out that my card has been reported lost ! and has been blocked . It was my husband who had reported a card lost 2 days go. Has there been a mix-up?I want her card to be re-instated and an explanation why this happened. I am travelling for the next 3 weeks and would need this  to be sorted out urgently.

1. Check card history of both wife and husband 
2. Check if the correct card was blocked by the bank

''' + complaint + '''\n'''
    
    model_id = "google/flan-ul2"
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 100,
        "min_new_tokens": 1,
        "repetition_penalty": 2,
        "beam_width": 1
    }
    print(input)
    investigation_result = generate(input, model_id, parameters)

    input = '''Provide resolution steps for the given Customer Complaint.

I recently lost a card in bank ATM and raised a request for replacment card. I was surpised to receive a replacement card for my wife instead of me.I need the card urgently before the Easter weekend since I am going on a vacation.

1. Raise request for card replacement and PIN with high priority. 
2. Offer an amount as a D&I for the inconvenience  caused.

My card has been declined while making a payment . I called the bank and found out that my card has been reported lost ! and has been blocked . It was my husband who had reported a card lost 2 days go. Has there been a mix-up?I want her card to be re-instated and an explanation why this happened. I am travelling for the next 3 weeks and would need this  to be sorted out urgently.

1. Raise request for card replacement and PIN with high priority for both husband and wife. 
2. Offer an amount as a D&I for the inconvenience  caused.

My husband had called the bank earlier this week to get this card on the joint account cancelled. When I used my card yestreday in a shop it got declined. What has happened? Have you guys blocked my card?

1. Raise request for card replacement and PIN with high priority for wife. 
2. Offer an amount as a D&I for the inconvenience caused. 
3. Raise a request to update communication channel to send notification before account closure or card blockage.

My card has been declined while making a payment . I called the bank and found out that my card has been reported lost ! and has been blocked . It was my husband who had reported a card lost 2 days go. Has there been a mix-up?I want her card to be re-instated and an explanation why this happened. I am travelling for the next 3 weeks and would need this  to be sorted out urgently.

1. Raise request for card replacement and PIN with high priority for both husband and wife. 
2. Offer an amount as a D&I for the inconvenience  caused.

I had a situation where my card was retained by the cash machine couple of days. 
I immedialy raised a request to get this back from the bank.
Yesterday , my husband had some issue with his card on the joint account , so he called to get this blocked and replaced. In the process, the advisor blocked and replaced my card.

''' + complaint + '''\n'''
    
    model_id = "google/flan-ul2"
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 100,
        "min_new_tokens": 1,
        "repetition_penalty": 2,
        "beam_width": 1
    }
    print(input)
    resolution_result = generate(input, model_id, parameters)
    
    st.markdown("**Complaint Summary :** \n" + summary_result)
    st.markdown("**Complaint Sentiment :** \n" + sentiment_result)
    st.markdown("**Complaint Tone:** \n" + tone_result)
    st.markdown("**Complaint Urgency :** \n" + urgency_result)
    st.markdown("**Complaint RCA :** \n" + rca_result)
    st.markdown("**Recommended Investigation Steps :** \n" + investigation_result)
    st.markdown("**Recommended Resolution Steps :** \n" + resolution_result)

if __name__ == "__main__":
    st.title('Customer Complaints Journey')
    complaint = st.text_area('Type your Customer Complaint here')
    if st.button('Evaluate'):
        main(complaint)