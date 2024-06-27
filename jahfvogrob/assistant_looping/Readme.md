
Description: This asset performs the looping of a step in assistant action and opening of a particular URL in a new tab.

Instructions to use: You can write any query and it will hit the action to print the products and their correspoding links using looping in steps of action. 

Explanation: 
In "Looping" action we have defined three different variables "input_array", "links_array", and "idx".
The loop starts with Step 3 by initialzing "idx" variable to -1.
Step 4 and 5 repeats until the intems of the products array ("input_array") traverses through each element and reaches the end.

The array "links_array" contains links to various products. In Step 5, these links are utilized within anchor tags (<a href="..."></a>).
The "href" attribute specifies the link destination, "target="_blank"" ensures the link opens in a new browser tab, and the "title" attribute provides the text to display as the link.
