import requests
import json
import random
from requests import api


def get_configs(update_flag):
    """
    Description: Load json config file
    Parameters:
        update_flag : force config values update
    """
    config_file_path = "config_files/config.json"
    config_file = open(config_file_path)
    config_json = json.load(config_file)
    config_file.close()
    if config_json["key"] == "" or config_json["token"] == "" or update_flag:
        api_key = input("INGRESE KEY: ")
        token = input("INGRESE TOKEN: ")
        config_json["key"] = api_key
        config_json["token"] = token
        config_string = json.dumps(config_json)
        config_file = open(config_file_path, "w")
        config_file.write(config_string)
        config_file.close()
    else:
        api_key = config_json["key"]
        token = config_json["token"]
    return config_json["api_url"], api_key, token, config_json["labels_list"]


def create_list(URL, api_key, token, board_id, list_name):
    PARAMS = {"key": api_key, "token": token, "name": list_name}
    r = requests.post(url=URL + "/boards/" + board_id + "/lists", params=PARAMS)
    return r.status_code == 200


def get_lists_data(URL, api_key, token, board_id):
    # defining a params dict for the parameters to be sent to the API
    USER_PARAMS = {"key": api_key, "token": token}
    r0 = requests.get(url=URL + "/boards/" + board_id + "/lists", params=USER_PARAMS)
    return r0.json()


def create_label(URL, api_key, token, board_id, label):
    PARAMS = {"key": api_key, "token": token, "name": label, "idBoard": board_id}
    r = requests.post(url=URL + "/labels", params=PARAMS)
    return r.status_code == 200


def get_labels(URL, api_key, token, board_id, labels_list):
    # defining a params dict for the parameters to be sent to the API
    labels_created = False
    while not labels_created:
        label_dict = {}
        labels_created = True
        USER_PARAMS = {"key": api_key, "token": token}
        r0 = requests.get(
            url=URL + "/boards/" + board_id + "/labels", params=USER_PARAMS
        )
        for label in r0.json():
            name = label["name"]
            if name != "":
                label_dict[name] = label["id"]
        for label in labels_list:
            if label not in label_dict.keys():
                create_label(URL, api_key, token, board_id, label)
                labels_created = False
    return label_dict


def get_data(URL, api_key, token):
    """
    Description: get user and boards data from trello API
    """
    # defining a params dict for the parameters to be sent to the API
    USER_PARAMS = {"key": api_key, "token": token}
    BOARDS_PARAMS = {
        "key": api_key,
        "token": token,
        "fields": "name,url,memberships,lists",
    }

    # sending get request and saving the response as response object
    r0 = requests.get(url=URL + "/members/me", params=USER_PARAMS)
    r1 = requests.get(url=URL + "/members/me/boards", params=BOARDS_PARAMS)

    # extracting data in json format
    return r0.json(), r1.json()


def post_card(URL, api_key, token, list_id, task_data, labels_dict):
    PARAMS = {
        "key": api_key,
        "token": token,
        "idList": list_id,
        "name": task_data["Title"],
    }
    if task_data["type"] == "issue":
        PARAMS["desc"] = task_data["Description"]
    elif task_data["type"] == "bug":
        PARAMS["desc"] = task_data["Description"]
        PARAMS["idLabels"] = labels_dict[task_data["Label"]]
        PARAMS["idMembers"] = task_data["idMember"]
    elif task_data["type"] == "task":
        PARAMS["idLabels"] = labels_dict[task_data["Category"]]
    else:
        PARAMS = {**PARAMS, **task_data}
    r = requests.post(url=URL + "/cards", params=PARAMS)
    return r.status_code == 200


def right_user(username):
    """
    Description: Verify if user wants to change access data.
    """
    while True:
        change_user = input(f"Hi {username}! \n Do you want to change user? [y/N]: ")
        if change_user in "Nn":
            return True
        elif change_user in "yY":
            return False
        else:
            print("Unknown option.")


def create_new_task_type(tasks_json):
    """
    Description: Add new task type and update tasks.json
    """
    new_attribute = True
    attribute = ""

    new_task_type = input("Enter new task type name: ")
    tasks_json[new_task_type] = {}
    while new_attribute:
        attribute = input("Enter new attribute name: ")
        if attribute != "":
            tasks_json[new_task_type][attribute] = input(
                "Please enter categories for this attribute. If not needed, press ENTER: "
            )
        else:
            print("Attribute empty.")
            continue
        new_attribute = (
            input('PRESS ENTER to add more attributes or "f" to finish: ') == ""
        )
    tasks_string = json.dumps(tasks_json)
    tasks_file = open("config_files/tasks.json", "w")
    tasks_file.write(tasks_string)
    tasks_file.close()


def create_task():
    """
    Description: Create tasks or set new tasks with new attributes.
    """
    task_index = 0
    index = 0
    task_created = False
    task_type = ""
    categories = ""
    new_task = dict()
    tasks_file = open("config_files/tasks.json")
    tasks_json = json.load(tasks_file)
    tasks_list = list()
    tasks_file.close()

    while not task_created:
        tasks_list = tasks_json.keys()
        task_index = 0
        print(f"Create new task: \n{task_index} - Create new type")
        for type in tasks_list:
            task_index += 1
            print(f"{task_index} - {type}")

        index = int(input(f"Select task flavor [0 - {task_index}]: "))
        while index < 0 or index > task_index:
            index = input("Index out of range. Please enter again: ")
        task_index = index
        if task_index == 0:
            create_new_task_type(tasks_json)
            continue
        else:
            task_type = list(tasks_list)[task_index - 1]
            new_task["type"] = task_type
            for key in tasks_json[task_type].keys():
                categories = tasks_json[task_type][key]
                if categories == "":
                    new_task[key] = input(f"Enter {key}: ")
                else:
                    new_task[key] = input(f"Enter {key} from {categories}: ")
            task_created = True
    return new_task


def load_task(load_file_path):
    """
    Description: load task data from json file
    """
    tasks_file = open("config_files/tasks.json")
    load_file = open(load_file_path)
    tasks_json = json.load(tasks_file)
    load_json = json.load(load_file)
    tasks_file.close()
    load_file.close()
    task_dict = dict()

    task_dict["type"] = load_json["Type"]
    attributes_list = tasks_json[load_json["Type"]].keys()
    for key in attributes_list:
        task_dict[key] = load_json[key]
    return task_dict


def generate_title(description):
    description_list = description.split(" ")
    number = len(description) % 100
    word = description_list[number % len(description_list)]
    return f"bug-{word}-{number}"


def add_bug_data(task_data, memberships):
    task_data["Label"] = "Bug"
    task_data["Title"] = generate_title(task_data["Description"])
    n = random.randint(0, len(memberships) - 1)
    task_data["idMember"] = memberships[n]["idMember"]


def main():

    # Variable declaration
    URL, key, token, labels_list = get_configs(False)
    user_data, boards_data = get_data(URL, key, token)
    boards = []
    board = dict()
    task_data = dict()
    board_name = ""
    board_id = ""
    index = 0
    board_index = 0
    lists_data = []
    list_id = ""
    list_exist = False

    # Verify correct user
    username = user_data["username"]
    while not right_user(username):
        URL, key, token, labels_list = get_configs(True)
        user_data, boards_data = get_data(URL, key, token)

    # Board selection
    print(f"Boards:")
    for board in boards_data:
        board_index += 1
        board_name = board["name"]
        print(f"{board_index} - {board_name}")
    index = input(f"Which board do you want to work with [1 - {board_index}]: ")
    while not index.isdigit() or int(index) < 1 or int(index) > board_index:
        index = input("Index out of range. Please enter again: ")
    board_index = int(index) - 1
    board = boards_data[board_index]
    board_id = board["id"]
    board_name = board["name"]
    print(f"Board name : {board_name}")

    # Task creation
    load_file_path = input(
        "Enter json file name to load task or press ENTER to create one: "
    )
    task_data = create_task() if load_file_path == "" else load_task(load_file_path)
    if task_data["type"] == "bug":
        add_bug_data(task_data, board["memberships"])
    print(task_data)

    # Get lists data
    while not list_exist:
        lists_data = get_lists_data(URL, key, token, board_id)
        for list in lists_data:
            if list["name"] == "To Do":
                list_id = list["id"]
                list_exist = True
                break
        if not list_exist:
            create_list(URL, key, token, board_id, "To Do")

    # Verify labels
    labels_dict = get_labels(URL, key, token, board_id, labels_list)

    # POST task into Board
    if post_card(URL, key, token, list_id, task_data, labels_dict):
        print("TASK created sucessfully!")
    else:
        print("TASK creation FAIL")


if __name__ == "__main__":
    main()
