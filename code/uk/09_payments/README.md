# Платежі

У цьому каталозі знаходяться вихідні файли для розділу https://vadim-khristenko.github.io/aiogram-3-guide/uk/payments/

Для запуску бота (потребує Python 3.11 та вище) скопіюйте файл `settings.example.toml` під ім'ям 
`settings.toml` та заповніть своїми значеннями. Далі можна запустити (з-під venv) командою:

```python
CONFIG_FILE_PATH=/path/to/settings.toml python -m bot
```

Також у репозиторію лежить файл [donatebot.example.service](donatebot.example.service) 
для запуску через Systemd.
