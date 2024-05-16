import difflib

# Here we are considering that "document 1" is the ground truth and we have to compare "document 2" with it.
# So we are checking what all keywords are missing or extra in document 2

def compare_documents(doc1, doc2):

    differ = difflib.Differ()
    diff = list(differ.compare(doc1.split(), doc2.split()))
    index1 = 0
    index2 = 0
    indices_missing = []    #missing text index is of doc 1
    indices_extra = []   #extra text index is of doc2
    for line in diff:
        if line.startswith('-'):
            if index1 < len(doc1.split()):
                indices_missing.append(index1)
            index1 += 1
        elif line.startswith('+'):
            if(len(line[2:].strip())<=1):  
                index2 += 1
                continue
            indices_extra.append(index2)
            if index2 < len(doc2.split()):
                index2 += 1
        else:
            index1 += 1
            index2 += 1

    print("Indices of missing text:", indices_missing)
    print("Indices of extra text:", indices_extra) #check this
    
    missing_text = []
    extra_text =[]
    current_extra = ""
    for i, line in enumerate(diff): 
        if line.startswith('- '):
            missing_text.append(line[2:])      
            current_extra = ""
        elif line.startswith('+ '):
            if(len(line[2:].strip())>1):          
                current_word = line[2:]
                current_extra += current_word + " "         
                if i == len(diff) - 1 or not diff[i + 1].startswith('+ '):
                    extra_text.append(current_extra.strip())
                    current_extra = ""


    missing_text = '; '.join(missing_text)
    extra_text = '; '.join(extra_text)
    matcher = difflib.SequenceMatcher(None, doc1, doc2)
    similarity_ratio = matcher.ratio()

    return similarity_ratio, missing_text, extra_text


# We can pass our documents text in compare_documents() 

doc1=""" 
1. **Acceptance of Terms**: Your use of this service constitutes your acceptance of these terms and conditions.
2. **Privacy Policy**: Your privacy is important to us. Please review our Privacy Policy to understand how we collect, use, and protect your personal information.
3. **Use Restrictions**: You agree to use the service only for lawful purposes and in accordance with these terms and any applicable laws and regulations.
4. **Intellectual Property**: All content provided through the service is the property of [Company Name] and is protected by copyright and other intellectual property laws.
5. **Limitation of Liability**: We are not liable for any damages or losses arising from your use of the service, including but not limited to direct, indirect, incidental, or consequential damages.
"""



doc2=""" 
1. **Acceptance of Terms**: Your use of this service constitutes your acceptance of these terms and conditions.
2. **Privacy Policy**: Your privacy is important to us. Please review our Privacy Policy to understand how we collect, use, and protect your personal information.
3. **Use Restrictions**: You agree to use the service only for lawful purposes and in accordance with these terms and any applicable laws and regulations.
5. **Limitation of Liability**: We are not liable for any damages or losses arising from your use of the service, including but not limited to direct, indirect, incidental, or consequential damages.
"""

similarity_ratio, missing_text, extra_text = compare_documents(doc1,doc2)


print("Similarity ratio:",  round(similarity_ratio * 100, 2),"%")
print("Missing text:\n", missing_text)
print("Extra text:\n", extra_text)
