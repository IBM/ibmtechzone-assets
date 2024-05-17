
object_prompt_start = """Generate JSON output containing the following information extracted from the given combined Selenium script containing multiple classes and functions:

For each method, including those representing web elements:

- {
  "objectClass": "The class of the method or web element (e.g., 'WebEdit', 'WebList', etc.)",
  "objectName": "The name of the method or web element",
  "propertyName": "The property used to locate the web element if applicable (e.g., 'id', 'xpath', 'cssSelector', etc.). If the method doesn't represent a web element, propertyName should be null.",
  "propertyValue": "The value of the property used to locate the web element if applicable. If the method doesn't represent a web element, propertyValue should be null."
  }

Ensure that the objectClass is correctly extracted for each method representing web elements based on the following considerations:
1. For methods directly representing web elements, determine the objectClass based on the method's name or return type and match it with the provided classes ("WebEdit", "WebList", "WebRadioButton", "WebLink", "WebButton", "Page", "WebCheckBox", "Frame").
2. For methods accessing web elements through other methods or classes, analyze the method's usage context and infer the objectClass accordingly.
3. For methods that do not represent web elements, set the objectClass as null.

Consider all declared web elements and those accessed through methods from all classes within the script in the extraction process.

Assume that the properties used to locate web elements can be any locator supported by Selenium (e.g., "id", "xpath", "cssSelector", etc.).

Provide the information in JSON format within a common list.

Input: """




# New Prompt 1

"""Generate JSON output containing the following information extracted from the given combined Selenium script containing multiple classes and functions:

For each method, including those representing web elements:

- {
  "objectClass": "The class of the method or web element (e.g., 'WebEdit', 'WebList', etc.)",
  "objectName": "The name of the method or web element",
  "propertyName": "The property used to locate the web element if applicable (e.g., 'id', 'xpath', 'cssSelector', etc.). If the method doesn't represent a web element, propertyName should be null.",
  "propertyValue": "The value of the property used to locate the web element if applicable. If the method doesn't represent a web element, propertyValue should be null."
  }

Ensure that the objectClass is correctly extracted for each method, considering the following cases:
1. For methods directly representing web elements, the objectClass should be one of the provided classes ("WebEdit", "WebList", "WebRadioButton", "WebLink", "WebButton", "Page", "WebCheckBox", "Frame").
2. For methods accessing web elements through other methods or classes, determine the objectClass based on the return type or usage context.
3. For methods that do not represent web elements, set the objectClass as null.

Consider all declared web elements and those accessed through methods from all classes within the script in the extraction process.

Assume that the properties used to locate web elements can be any locator supported by Selenium (e.g., "id", "xpath", "cssSelector", etc.).

Provide the information in JSON format within a common list.


Input: """




# Old prompt main
"""Generate JSON output containing the following information extracted from the given combined Selenium script containing multiple classes and functions:

For each method, including those representing web elements:

- {
  "objectClass": "The class of the method or web element (e.g., 'WebEdit', 'WebList', etc.)",
  "objectName": "The name of the method or web element",
  "propertyName": "The property used to locate the web element if applicable (e.g., 'id', 'xpath', etc.). If the method doesn't represent a web element, propertyName should be null.",
  "propertyValue": "The value of the property used to locate the web element if applicable. If the method doesn't represent a web element, propertyValue should be null."
  }

Ensure that the objectClass is correctly extracted for each method, limited to the provided classes ("WebEdit", "WebList", "WebRadioButton", "WebLink", "WebButton", "Page", "WebCheckBox", "Frame").

Note:
- Each method representing a web element interacts with these web elements.
- Include all declared web elements and those accessed through methods from all classes within the script in the extraction process.
- Assume that the properties used to locate web elements are limited to "id", "xpath", and "linkText".
- Provide the information in JSON format within a common list.

Input: """

testcase_prompt_start = """Extract TestCases and their corresponding functions from the provided Selenium scripts and provide the results in JSON format. Each TestCase may contain one or more functions.

For each TestCase:

Identify the name of the TestCase.
List all the functions within the TestCase.

For each function within a TestCase:

Determine the name of the function.

Ensure that the extraction process accurately captures TestCases and functions regardless of their placement within the script. Provide the extracted information in JSON format for further analysis.

The JSON structure should be as follows:
[
 {
 "TestCaseName": "Name of the TestCase",
 "Functions": ["Name of the function", "Name of another function"]
 },
 {
 "TestCaseName": "Name of another TestCase",
 "Functions": [ "Name of function in another TestCase"]
 }
]

Input:
"""

mapping_testcase_and_object_prompt_start="""Given a list of object names and a JSON file containing test cases and functions, along with Selenium scripts as inputs, learn to map the object names to the functions and actions in the test cases by analyzing the provided Selenium scripts. Provide the output in JSON format.

The input JSON file contains the following structure:
[
 {
 "TestCaseName": "Name of the TestCase",
 "Functions": ["Name of the function", "Name of another function"]
 },
 {
 "TestCaseName": "Name of another TestCase",
 "Functions": [ "Name of function in another TestCase"]
 }
]

The object names list contains the names of objects (web elements) used in the Selenium scripts and has the following structure:
[objectName1, objectName2, objectName3]

Your task is to learn the mapping between object names and functions and actions in the test cases based on their occurrences in the Selenium scripts. The output should be a JSON object representing the mapping, structured as follows:
{
  "TestCases": [
    {
      "TestCaseName": "Name of the TestCase",
      "Functions": [
        {
          "FunctionName": "Name of the function",
          "ObjectActions": {
            "Object1": ["Action1", "Action2"],
            "Object2": ["Action3"],
            "Object3": ["Action4"]
          }
        },
        {
          "FunctionName": "Name of another function",
          "ObjectActions": {
            "Object4": ["Action5"]
          }
        }
      ]
    },
    {
      "TestCaseName": "Name of another TestCase",
      "Functions": [
        {
          "FunctionName": "Name of function in another TestCase",
          "ObjectActions": {
            "Object5": ["Action6", "Action7"],
            "Object6": ["Action8"]
          }
        }
      ]
    }
  ]
}

Input:
"""

object_prompt_end = """
Output:"""