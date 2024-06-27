
Description: This asset facilitates the dynamic creation of buttons that open in new tabs, neatly spaced within the same line.

Usage Instructions:
You can input any query, which triggers an action ("Dynamic Buttons") to display buttons for clicking. Each button opens a corresponding product's documentation in a new tab.

Explanation: 
The "Dynamic Buttons" action utilizes three key variables: "product_links", "template", and "links".
Step 3 involves assigning "product_links" to a list of dictionaries, each containing a product name and its respective URL. One can utilize this variable to change the number of buttons.
"template" is set using an expression that generates a clickable button with the product name as text, linked to its documentation.
The variable "links" consolidates all these buttons, ensuring they are displayed in a single line with appropriate spacing.