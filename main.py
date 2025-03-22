from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd 
from pathlib import Path
from pydantic import BaseModel


app = FastAPI()

# Check if the CSV files exist, if not, create them
tasks_csv = Path("data/tasks.csv")
users_csv = Path("data/users.csv")

# Create the CSV files if they don't exist
if Path(tasks_csv).exists():
    df = pd.DataFrame(columns=['task', 'deadline', 'user'])
    df.to_csv(tasks_csv, index=False)

# Create the CSV files if they don't exist
if Path(users_csv).exists():
    df = pd.DataFrame(columns=['username', 'password'])
    df.to_csv(users_csv, index=False)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # This allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # This allows all headers
)

class User(BaseModel):
    username: str
    password: str 

class Task(BaseModel):
    task: str
    deadline: str 
    user: str
 
@app.post("/login/")
async def user_login(User: User):
    """
    Handles the user login process. The function checks if the user exists in the users CSV file.
    If the username and password match, the user is logged in successfully.

    Args:
        User (User): The username and password provided by the user.

    Returns:
        dict: A response indicating whether the login was successful or not.
              - If successful, the status will be "Logged in".
              - If failed (user not found or incorrect password), appropriate message will be returned.
    """
    df = pd.read_csv(users_csv)
    
    # Check if the username and password match
    username = User.username in df['username']
    password = User.password in df['password']

    # If the username is found but password is incorrect
    if username and not password:
        return {"status": "Failed"}
    
    return {"status": "Logged in"}


@app.post("/create_user/")
async def create_user(User: User):
    """
    Creates a new user by adding their username and password to the users CSV file.

    Args:
        User (User): The username and password for the new user.

    Returns:
        dict: A response indicating whether the user was successfully created.
              - If successful, the status will be "User Created".
              - If user already exists, a relevant message will be returned.
    """
    df = pd.read_csv(users_csv)

    # Check if the user already exists
    if User.username in df['username'].values:
        return {"status": "User already exists"}
    
    # Append the new user to the dataframe
    df.loc[len(df)] = User.dict()
    df.to_csv(users_csv, index=False)
    return {"status": "User Created"}

@app.post("/create_task/")
async def create_task(Task: Task):
    """
    Creates a new task by adding the task description, deadline, and associated user to the tasks CSV file.

    Args:
        Task (Task): The task description, deadline, and associated user.

    Returns:
        dict: A response indicating whether the task was successfully created.
              - If successful, the status will be "Task Created".
    """
    
    df = pd.read_csv(tasks_csv)

    # Append the new task to the dataframe
    df.loc[len(df)] = Task.dict()

    # Save the updated dataframe back to CSV
    df.to_csv(tasks_csv, index=False)

    return {"status": "Task Created"}


@app.get("/get_tasks/")
async def get_tasks(name: str):
    """
    Retrieves the list of tasks associated with a specific user.

    Args:
        name (str): The username for which the tasks need to be fetched.

    Returns:
        dict: A list of tasks (task description, deadline) associated with the given user.
              - If tasks are found, the response will include the task details.
              - If no tasks are found for the user, an empty list will be returned.
    """
    df = pd.read_csv(tasks_csv)

    # Filter tasks for the given user
    user_tasks = df[df["user"] == name]

    # Convert tasks to dictionary format
    return {"tasks": user_tasks.to_dict(orient="records")}


