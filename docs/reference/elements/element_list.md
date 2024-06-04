There are 2 kinds of Elements in OneCode:

* [Input Elements](#input-elements): use them to expose your input parameters.
* [Output Elements](#output-elements): use them to expose your output data.


# Input Elements

On OneCode Cloud, the interface (UI) is automatically created from these elements.
All Input Elements have at least the following attributes:

* `key`: pick a name that is unique across your App.
* `value`: the default value (typically used when running your local code without parameter file).
* `label`: the label displayed in the interface (if not provided, the `key` will be used instead).
* `optional`: whether `None` is possible value.

Available input elements for OneCode projects:

* [checkbox](#checkbox)
* [csv_reader](#csv_reader)
* [dropdown](#dropdown)
* [file_input](#file_input)
* [number_input](#number_input)
* [radio_button](#radio_button)
* [slider](#slider)
* [text_input](#text_input)


Below are some examples on how to call these elements.
The full API is available [here](input_elements_api.md).

---

## checkbox
```python
do_something = checkbox(
    key="do_something",
    value=True,
    label="Do Something?"
)

if do_something:
    # do something here

```


## csv_reader
```python
df = csv_reader(
    key="my_csv",
    value="model/data.csv",
    label="Choose a CSV file"
)

# df is a pd.DataFrame!
print(df.describe())

```


## dropdown
```python
# single choice
my_choice = dropdown(
    key="my_choice",
    value="cat",
    label="Choose an animal",
    options=["dog", "cat", "fish"]
)

print(f"my choice is: {my_choice}")


# multiple choice
my_multi_choice = dropdown(
    key="my_multi_choice",
    value=["cat"],
    label="Choose several animals",
    options=["dog", "cat", "fish"],
    multiple=True
)

print(f"my multiple choices are: {my_multi_choice}")

```


## file_input
```python
# single file
image = file_input(
    key="my_file",
    value="images/my_image.png",
    label="Select an image",
    types=[FileFilter.IMAGE]
)

img = PIL.Image.open(image)


# multiple files
multifiles = file_input(
    key="my_file",
    value=["model/test.csv", "model/test.json"],
    label="Select several files",
    types=[("Data", ".csv .tsv"), ("Config", ".json .yaml .yml")],
    multiple=True
)

for file in multifiles:
    with open(file) as f:
        # ...

```


## number_input
```python
magic_number = number_input(
    key="magic_number",
    value=42,
    label="Choose a magic number",
    min=0,
    max=None,
    step=2
)

print(f"Your magic number is {magic_number}")

```


## radio_button
```python
animal = radio_button(
    key="my_choice",
    value="fish",
    label="Choose an animal",
    options=["dog", "cat", "fish"],
    horizontal=False
)

print(f"Your animal of choice is {animal}")

```


## slider
```python
magic_number = slider(
    key="magic_number",
    value=42,
    label="Choose a magic number",
    min=0,
    max=50,
    step=0.5
)

print(f"Your magic number is {magic_number}")

```


## text_input
```python
name = text_input(
    key="your_name",
    value="OneCoder",
    label="What is your name?",
    max_chars=30,
    placeholder="Type your name here!"
)

print(f"Your name is {name}")

```


# Output Elements

On OneCode Cloud, only file explicitly flagged as output are push back to the storage.
All Output Elements have at least the following attributes:

* `key`: pick a meaningful name - it doesn't have to be unique across your App.
* `value`: the default value (typically used when running your local code without parameter file).

Available output elements for OneCode projects:

* [file_output](#file_output)

Below is an example on how to call this element.
The full API is available [here](output_elements_api.md).


## file_output
```python
image = file_output(
    key="output_image",
    value="model/my_image.png",
    make_path=True  # will create the model folder if doesn't exist
)

plt.savefig(image)

```
