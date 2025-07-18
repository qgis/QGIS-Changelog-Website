# ✨ Contributing to QGIS-Changelog-Website

Thank you for your interest in contributing to the QGIS Changelog Website! We welcome all types of contributions, including bug reports, feature suggestions, code improvements, and documentation updates. Please review the guidelines below to help ensure a smooth and effective contribution process.

![-----------------------------------------------------](./img/green-gradient.png)

## 🧑💻 Development Setup

To get started with development, you can run the application in debug mode using Docker Compose. Several helpful Docker Compose commands are already defined in the `deployment/Makefile`.

## 🏃 Prerequisites

This project requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) for both development and production environments. Please make sure both are installed on your system before proceeding.

![Docker logo](https://www.docker.com/wp-content/uploads/2022/03/Moby-logo.png)

Verify your installation with:
```bash
docker --version
docker-compose --version
```

![-----------------------------------------------------](./img/green-gradient.png)

## 🛒 Cloning the Repository

- Clone the repository:
  ```sh
  git clone https://github.com/qgis/QGIS-Changelog-Website.git
  ```
- Check your current directory:
  ```sh
  pwd
  ```
- The repository path should be `<your current directory>/QGIS-Changelog-Website`
- Navigate to the project directory:
  ```sh
  cd QGIS-Changelog-Website/
  ```

![-----------------------------------------------------](./img/green-gradient.png)

## Pre-commit Hooks

This repository uses [pre-commit](https://pre-commit.com/) to automate code quality checks before each commit. To set it up:

1. Install pre-commit (if not already installed):
    ```sh
    pip install pre-commit
    ```

2. Install the hooks defined in `.pre-commit-config.yaml`:
    ```sh
    pre-commit install
    ```

Now, the configured checks (such as linting and formatting) will run automatically when you commit changes.

![-----------------------------------------------------](./img/green-gradient.png)

### ❄️ Nix Support

If you use Nix or NixOS, you can set up the development environment with:

```sh
nix-shell
./vscode.sh
```
*Note: The Nix shell will soon install all dependencies automatically.*

![-----------------------------------------------------](./img/green-gradient.png)

### ⚡️ Quick Start

- Generate your `.env` file from the example and update it with your email configuration:
  ```sh
  cd deployment
  cp .env.example .env
  nano .env  # Edit as needed
  ```

- Build and start the application:
  ```sh
  make build
  make devweb
  ```

- Run migrations and load initial data:
  ```sh
  make shell c=devweb
  python manage.py migrate
  python manage.py loaddata changes/fixtures/initial_data.json
  # Exit the shell with Ctrl+D
  ```

- Start the development server:
  ```sh
  make devweb-runserver
  ```

Open your browser and visit [http://localhost:62202](http://localhost:62202). The default super admin credentials are `qgisadmin` / `qgisadmin`.

![-----------------------------------------------------](./img/green-gradient.png)

### More Information

For detailed instructions, please refer to the [README-dev](./README-dev.md) and [README-docker](./README-docker.md) files. These documents provide comprehensive information about both development and production environments, similar to the original [Projecta](https://github.com/kartoza/projecta.git) application.

![-----------------------------------------------------](./img/green-gradient.png)