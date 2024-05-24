...in progress

### Clone Repository
```sh
git clone git@github.com:sabi-h/qpyr.git
```

### Install Dependencies
```sh
poetry install
```

### Publish new Package version
1. Increase the version in `pyproject.toml` file
2. Run in terminal: 
    ```sh
        poetry build; poetry publish
    ```