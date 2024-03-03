## FoodFriend (demo)
*A pantry list and recipe maker app.*

Developed during HackTheBurghX as a solution to solve everyday problems.

A local llama2-based food list and recipe app. Made during HackTheBurghX as a team of two.

### Functionality
The app allows you to scan your grocery receipts and uses image processing and Google's OCR (optical character recognition) to translate them to text. Then, a local llama2 LLM (large language model) is used to select food entries, figure out if they should go to the fridge, and parse the receipt text into simple English.

Both the pantry and fridge lists show how many days you've had an item, making it easier to cook with food you've had for longer. To make this process even easier, you can select any combination of ingredients and the LLM will create recipes for you on the go!

![image](https://github.com/jakub-maly/FoodFriend/assets/50239149/1f44254e-60ac-4c1b-8393-f9e0c15e0602)

![image](https://github.com/jakub-maly/FoodFriend/assets/50239149/6099665e-fc79-421d-9061-d907effbec67)

### Requirements
To run the program, Ollama's `LLAMA2` model and the Tesseract model need to be installed locally.
