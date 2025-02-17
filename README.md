# Home Loan App

## Create an environment using venv

1. Open a terminal and navigate to your project folder.
```sh
cd myproject
```


2. In your terminal, type:
```sh
python -m venv .venv
```


3. A folder named ".venv" will appear in your project. This directory is where your virtual environment and its dependencies are installed.


## Activate your environment

4. In your terminal, activate your environment with one of the following commands, depending on your operating system.
   
   ```sh
    # Windows command prompt
    .venv\Scripts\activate.bat

    # Windows PowerShell
    .venv\Scripts\Activate.ps1

    # macOS and Linux
    source .venv/bin/activate
    ```

5. Once activated, you will see your environment name in parentheses before your prompt. "(.venv)"

## Install Streamlit in your environment

6. In the terminal with your environment activated, type:

```sh
pip install streamlit
```


7. Test that the installation worked by launching the Streamlit Hello example app:

```sh
streamlit hello
```


    If this doesn't work, use the long-form command:
    
```sh
python -m streamlit hello
```

8. Streamlit's Hello app should appear in a new tab in your web browser!