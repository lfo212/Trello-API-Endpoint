# Trello API Endpoint

Script to create tasks in Trello.

## Steps

    0- [Optional] Add key and token to config_files/config.json
    1- Execute script: 
        ```
        python3 trello_endpoint.py
        ```
    2- Enter required information
    3- [Optional] After selecting board, enter json file name to create the task.

## Load task from json file

Before executing step 1 complete template.json with required attributes:

    {
        "Type": "",
        "Title": "",
        "Description": "",
        "Category": ""
    }

then save and in step 3 enter: "template.json"
