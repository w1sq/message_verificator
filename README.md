# Message Verificator

This project features a Telegram bot that can send messages to any other user of the same bot, facilitating anonymous message exchanges.

## Prerequisites

-   Docker

## Getting Started

To get a local copy up and running, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/w1sq/message_verificator.git
```

2. Navigate to the project directory:

```bash
cd message_verificator
```

1. Create and complete the [`.env`] file by copying the provided [`.env.example`] file and filling in the necessary values:

```plaintext
TGBOT_API_KEY=<your_telegram_bot_token_here>
HOST=<your_database_host>
PORT=<your_database_port>
LOGIN=<your_database_login>
PASSWORD=<your_database_password>
DATABASE=<your_database_name>
```

-   `TGBOT_API_KEY`: Replace `<your_telegram_bot_token_here>` with your actual Telegram bot token, which you can obtain from the BotFather on Telegram.
-   `HOST`: The hostname or IP address of your database server.
-   `PORT`: The port number your database listens on.
-   `LOGIN`: Your database login username.
-   `PASSWORD`: Your database login password.
-   `DATABASE`: The name of the database you want to connect to.

4. Build the Docker image:

```bash
docker build -t message_verificator .
```

5. Run the Docker container:

```bash
docker run -p 8501:8501 message_verificator
```

After running these commands, the Telegram bot will be up and running.

## Usage

Interact with the Telegram bot by choosing a receiver and sending a message to the bot. The bot will forward your message to recipent, allowing for anonymous message exchanges.

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

## License

Distributed under the [MIT License](LICENSE). See `LICENSE` for more information.

## Contact

Kokorev Artem - <kokorev_artem@vk.com>
