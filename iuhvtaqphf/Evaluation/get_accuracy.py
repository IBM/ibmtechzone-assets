# Function to calculate accuracy
def get_accuracy(test_data, TP):
    acc = TP/len(test_data)*100
    return acc   