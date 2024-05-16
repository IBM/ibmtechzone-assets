import watson_nlp

pii_model = watson_nlp.load("entity-mentions_rbr_multi_pii")


def get_pii_scores(input):
    pii_scores = []
    for text in input: # if we need to pass dataframe series df.values.tolist()
        out = pii_model.run(text, language_code="en")
        print(out)
        p = [c.confidence for c in out.mentions]
        print(p)
        if p:
            pii_scores.append(max(p))
        else:
            pii_scores.append(0)

    return pii_scores

input =['Please find my credit card number here: 378282246310005. Thanks for the payment.','Please find my bank account number here: 378282246310005.']
print("Here are the PII scores:",get_pii_scores(input))