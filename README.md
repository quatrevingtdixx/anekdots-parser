# Anekdots Parser

Парсер анекдотов с сайта shytok.net.

## Установка

```
git clone <repo>
cd anekdots-parser
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск
```
python parse_anekdots.py
```

## GitHub Actions
Workflow автоматически собирает Excel-файл и загружает как артефакт.
