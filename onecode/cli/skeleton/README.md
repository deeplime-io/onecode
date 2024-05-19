## OneCode Project Instructions

### Getting started with your code
1. Don't touch the `main.py` (feel free to look at it though ;-))
2. The application entry point is the `run()` function of the Python file of each Flow:
    * Don't change the Python flow filename nor the function name `run()`
    * Add your code to the `run()` function
    * Feel free to organize your code inside multiple files and sub-folders


### Running your application
To run you script with the default parameters
```bash
python main.py
```

To run you script with the another parameter set:
1. First extract your parameters as JSON and edit the parameter values as needed
2. Run your application providing the JSON file
```bash
# Extract and edit the generated file
onecode-extract my_parameters.json

# Run your application with the file
python main.py my_parameters.json
```

To run a specific flow
```bash
python main.py --flow flow_name
```
