# Wireless Measurements Project 521168S-3003

Welcome to the repository for the Wireless Measurements course project - a Smart Campus Sensor Measurement Device. The objective of this project is to create a device that monitors the CO2 levels in a work cubicle and alerts the user when it gets too high, ensuring a safe and healthy work environment.

In this repository, you will find all the code and resources necessary to replicate the project and build your own smart campus sensor measurement device. The code includes the firmware for the microcontroller, the communication protocol for transmitting data wirelessly, and the software for displaying the data on a user interface.

We have also included detailed documentation and instructions to guide you through the project, including the hardware and software setup, and how to customize the alert settings.

We hope that this project will serve as a valuable resource for anyone interested in wireless measurements and smart campus sensor technology. Please feel free to contribute to the project or reach out to us if you have any questions or suggestions.

<br />

Smart campus : https://smartcampus.fi/oulu/

Smart campus sensor map : https://smartcampus.oulu.fi/manage/map

Smart campus API page : https://smartcampus.oulu.fi/manage/

<br />

## Conda virtual enviroment 

To install libraries using Conda, follow these steps:

1. Open your terminal or Anaconda Prompt.

2. Activate your Conda environment using the command conda activate your_env_name. If you don't have an environment set up, you can create one using the command 'conda create --name your_env_name'.

3. Use the 'conda install' command to install the desired library. For example, to install NumPy, use the command conda install numpy.

4. Repeat step 3 for any additional libraries you need.

5. To check which libraries are installed in your environment, you can use the command 'conda list'.

6. When you are finished working with your environment, you can deactivate it using the command 'conda deactivate'.

Note: Conda can also be used to install libraries from non-default channels or to install specific versions of libraries. You can refer to the Conda documentation for more information on these advanced options.


# Good practices

## Code Formatting
Follow PEP 8 guidelines for code formatting. This includes naming conventions, code structure, and documentation.
Use an automated tool like 'black' or 'autopep8' to format your code before submitting a pull request.

## Documentation
Use docstrings to document classes, functions, and modules.
Write clear and concise comments to explain complex code logic.
Provide examples in documentation to help users understand how to use your code.

## Testing
Write unit tests to ensure that your code is working as expected.
Use a testing framework such as 'pytest' or 'unittest'.
Ensure that your tests cover edge cases and handle unexpected inputs.

## Pull Requests
Create a separate branch for your changes and make sure it is up to date with the main branch before submitting a pull request.
Provide a clear and concise description of your changes in the pull request.
Include relevant documentation and tests with your code changes.

By following these best practices, we can maintain a high-quality codebase that is easy to understand, maintain, and contribute to. Thank you for your contributions!