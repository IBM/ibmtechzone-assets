import pandas as pd
import json


def _compare_entity(gt_json, pred_json):
    if type(gt_json) is str:
        gt_json = json.loads(gt_json)
            
    if type(pred_json) is str:
        pred_json = json.loads(pred_json)

    is_correct = 1
    tp = 0
    fp = 0
    fn = 0

    for k in gt_json.keys():
        gt_values = gt_json[k]
        gt_values = [str(item).lower() for item in gt_values if item != ""]

        pred_values = pred_json[k]
        pred_values = [str(item).lower() for item in pred_values if item != ""]

        gt_set = set(gt_values)
        pred_set = set(pred_values)

        tp+=len(gt_set & pred_set)
        fp+=len(pred_set - gt_set)
        fn+=len(gt_set - pred_set)

        # print(tp, fp, fn)
    precision = tp/(tp+fp) if (tp+fp)>0 else 0
    recall = tp/(tp+fn) if (tp+fn)>0 else 0

    if fp>0 or fn>0:
        is_correct = 0
    return is_correct, recall, precision

def eval_entity_extraction(gt_file_path, target_sheet="Evaluation"):
    df = read_excel(gt_file_path, "GT_Prediction")

    recall_values = []
    precision_values = []
    correct_list = []
    entities_list = []
    for i, row in df.iterrows():
        query = row["Question"]
        gt_entities = json.loads(row["GT Entities"])
        pred_entities = json.loads(row["Pred Entities"].replace("'", "\""))
        entities_list.append(pred_entities)
        is_correct, recall, precision = _compare_entity(gt_entities, pred_entities)
        correct_list.append(is_correct)
        recall_values.append(recall)
        precision_values.append(precision)
        
    accuracy = round(sum(correct_list)/len(correct_list), 3)
    final_recall = round(sum(recall_values)/len(recall_values), 3)
    final_precision = round(sum(precision_values)/len(precision_values), 3)

    df.loc[:, "is_correct"] = correct_list
    df.loc[:, "Recall"] = recall_values
    df.loc[:, "Precision"] = precision_values
    df.loc[len(df.index)] = ["", "", "", accuracy, final_recall, final_precision]

    write_excel(df, gt_file_path, sheetname=target_sheet)


def read_excel(filename, sheetname=0):
    df = pd.read_excel(open(filename, 'rb') , sheet_name=sheetname, index_col=None) 
    # wb = xlrd.open_workbook(filename, encoding_override="utf-8")
    # df = pd.read_excel(wb)
    print(df)
    return df

def write_excel(df, filename, sheetname="Output", replace_sheet=True):
    if replace_sheet:
        with pd.ExcelWriter(filename, mode="a",
                            if_sheet_exists="replace", 
                            engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheetname)


if __name__ == "__main__":
    file_path = "entity_extraction_test.xlsx"
    eval_entity_extraction(file_path)