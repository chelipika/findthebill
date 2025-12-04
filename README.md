# Aiogram Bot Template

This repository provides a robust and scalable template for building Telegram bots using `aiogram`, a modern and asynchronous framework for Telegram Bot API. It includes features like subscription checks, broadcasting messages to users and groups, and handling channel posts.

## Features

*   **Asynchronous Operations**: Built on `asyncio` for high performance and responsiveness.
*   **Subscription Check**: Ensures users are subscribed to a specified channel before accessing bot features.
*   **Broadcast Messaging**: Send messages, photos, and audio with inline buttons to all users or all connected groups.
*   **Channel Post Forwarding**: Automatically forwards posts from a designated channel to all bot users.
*   **Group Chat Management**: Detects new group chats and saves their IDs for broadcast capabilities.
*   **FSM (Finite State Machine)**: Utilizes `aiogram`'s FSM for managing multi-step user interactions (e.g., creating broadcast messages).
*   **Database Integration**: Designed to work with a database for storing user and group IDs (via `database.requests`).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.8+
*   `pip` package manager

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/chelipika/tg_template_aiogram.git
    cd tg_template_aiogram
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (You'll need to create a `requirements.txt` file based on the imports in the provided code, e.g., `aiogram`, `schedule`).

4.  **Configuration:**
    Create a `config.py` file in the root directory with the following content:
    ```python
    # config.py
    TOKEN = "YOUR_BOT_TOKEN"
    CHANNEL_ID = -1001234567890 # Your channel's ID (must be a supergroup/channel)
    CHANNEL_LINK = "https://t.me/your_channel_link"
    ```
    *   **`TOKEN`**: Your Telegram Bot API token, obtained from BotFather.
    *   **`CHANNEL_ID`**: The ID of the public or private channel you want users to subscribe to. Make sure your bot is an administrator in this channel. For private channels, use the numerical ID (e.g., `-1001234567890`).
    *   **`CHANNEL_LINK`**: The invite link to your channel.

5.  **Database Setup:**
    The template assumes a `database` directory with a `requests.py` module for handling database interactions (e.g., `set_user`, `get_all_user_ids`, `set_group`, `get_all_groups_ids`). You will need to implement this part based on your chosen database (e.g., SQLite, PostgreSQL, MongoDB).

    Example `database/requests.py` (using a simple placeholder for demonstration):
    ```python
    # database/requests.py
    import asyncio

    # In a real application, replace these with actual database operations
    _users = set()
    _groups = set()

    async def set_user(tg_id: int):
        _users.add(tg_id)
        print(f"User {tg_id} added.")

    async def get_all_user_ids():
        return list(_users)

    async def set_group(chat_id: int):
        _groups.add(chat_id)
        print(f"Group {chat_id} added.")

    async def get_all_groups_ids():
        return list(_groups)
    ```

6.  **Keyboards Setup:**
    The template uses `logic/keyboards.py`. You'll need to implement the `create_markap_kb` and `subscribe_channel` functions there.

    Example `logic/keyboards.py`:
    ```python
    # logic/keyboards.py
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    subscribe_channel = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Subscribe", url="YOUR_CHANNEL_LINK_FROM_CONFIG")]
    ])

    def create_markap_kb(name: str, url: str) -> InlineKeyboardMarkup | None:
        if name and url:
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=name, url=url)]
            ])
        return None
    ```
    *Remember to replace `"YOUR_CHANNEL_LINK_FROM_CONFIG"` with the actual link.*

### Running the Bot

```bash
python main.py # Or whatever your main bot file is named
```

## Bot Commands and Functionality

Here's an overview of the commands and their usage:

### User Commands

*   `/start`: Initiates the bot, checks subscription status, and welcomes the user. If not subscribed, it provides a channel link.

### Admin/Private Commands

*(These commands are typically for bot administrators and should be protected accordingly in a production environment, e.g., by checking `message.from_user.id` against a list of admin IDs.)*

*   `/narrator <text>`: Sends the provided `<text>` argument to all users who have interacted with the bot.
    *   **Example**: `/narrator Hello everyone! Check out our new update.`

*   `/send_to_all_users`: Starts a multi-step process to create and send a rich message (image/audio + text + inline button) to all users.
    *   **Steps**:
        1.  Send image 🖼️
        2.  Send text 🗄️
        3.  Send inline link name 📛
        4.  Send inline link URL 🔗

*   `/send_to_all_groups`: Similar to `/send_to_all_users`, but broadcasts the rich message to all groups where the bot is a member.
    *   **Steps**:
        1.  Send image 🖼️
        2.  Send text 🗄️
        3.  Send inline link name 📛
        4.  Send inline link URL 🔗

### Automatic Handlers

*   **Channel Post Forwarding**: Any message posted in the `CHANNEL_ID` defined in `config.py` will be automatically forwarded to all bot users.
*   **Group Join Requests**: Handles `chat_join_request` updates.
*   **New Group Chat**: When the bot is added to a new group, it records the `chat_id`.
*   **Subscription Check Callback**: The `subchek` callback query re-checks the user's subscription status.

## Extending the Bot

*   **Add more commands**: Define new `@router.message(Command("your_command"))` handlers in `main.py`.
*   **Implement actual database**: Replace the placeholder `database/requests.py` with a real database solution (e.g., `SQLAlchemy`, `PonyORM`, `motor` for MongoDB).
*   **Error Handling**: Enhance error handling for network issues, API limits, and invalid user input.
*   **Admin Panel**: Consider building an in-bot admin panel for easier management of broadcasts and settings.
*   **Logging**: Implement proper logging for debugging and monitoring.
*   **Rich Media Support**: Extend `send_to_all_users` and `send_to_all_groups` to support videos, documents, and other media types.

## Contributing

Feel free to fork this repository, open issues, and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).
