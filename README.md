# TCP WMI Dispatcher

A concurrent client-server distributed application for remote query execution and system information gathering, built with Python Sockets and containerized using Docker.

## Application Demo

[![Watch Demo](https://img.youtube.com/vi/sHDLEO8FxSQ/maxresdefault.jpg)](https://www.youtube.com/watch?v=sHDLEO8FxSQ)

Click on the preview to watch the full application demonstration.

## 📌 How It Works

This system simulates a remote system management environment (WMI-like) where a central server coordinates the execution of commands across multiple connected clients.

* **Connection & Registration:** Clients connect with a unique username and their IP address. Upon a successful join or leave, the server automatically broadcasts the updated client list to all active users in real time.
* **Query Dispatching:** Any client acting as an operator can compose a query and target either all active clients or a specific subset (by machine name).
* **Coordinated Execution:** The server orchestrates the command distribution, forwards queries sequentially to the selected targets, and aggregates the responses.
* **Robustness & Timeouts:** If a targeted client fails to respond within a predefined window (5 seconds), the server flags that specific result as a timeout error and securely continues aggregating responses from the remaining clients without blocking.

## 💻 Available Commands
Once connected to the server, use the following query commands directly in the terminal prompt (`>`):

```bash
query all <command>
```
Executes the specified command on all currently connected clients and displays the aggregated results.

Supported commands: os, time, ping.

Example: query all os
```
query <client_name> <command>
```
Executes the specified command strictly on the targeted client.

Example: query TintaA time


⚙️ Prerequisites
Server: Docker installed on your machine.

Client: Python 3.9+ installed locally.

🚀 Run Instructions
1. Start the Server (Docker)
Open your terminal in the project directory where the Dockerfile and server.py are located.

Build the image:

docker build -t tcp-wmi-dispatcher .

Run the container:

docker run -p port:port tcp-wmi-dispatcher

2. Start the Clients
Open a new terminal window or PuTTY session for each client you want to simulate (minimum 3 recommended for a proper test).

Run the client script:

python3 client.py



