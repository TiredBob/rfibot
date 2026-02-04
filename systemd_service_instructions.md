I have created the `rfibot.service` file for your bot.

To install and enable this `systemd` service on your Ubuntu system, follow these steps:

1.  **Move the service file**: Copy the `rfibot.service` file to the `systemd` system directory:
    ```bash
    sudo mv rfibot.service /etc/systemd/system/
    ```
2.  **Reload `systemd`**: Inform `systemd` about the new service file:
    ```bash
    sudo systemctl daemon-reload
    ```
3.  **Enable the service**: Configure the service to start automatically on boot:
    ```bash
    sudo systemctl enable rfibot.service
    ```
4.  **Start the service**: Start the bot service immediately:
    ```bash
    sudo systemctl start rfibot.service
    ```
5.  **Check the status**: Verify that the service is running correctly:
    ```bash
    systemctl status rfibot.service
    ```
    To see the bot's output, remember you can attach to its `tmux` session: `tmux attach -t rfibot`.

The `rfibot.service` file has been created locally. I am awaiting your instruction to push this change to the remote `main` branch.