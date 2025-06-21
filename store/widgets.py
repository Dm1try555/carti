import json
from django import forms

class SimpleListWidget(forms.TextInput):
    """Віджет, який перетворює звичайний текст у JSON список"""

    def format_value(self, value):
        if isinstance(value, list):
            # Якщо вже список, конвертуємо у рядок через кому
            return ', '.join(str(v) for v in value)
        if isinstance(value, str):
            # Якщо це рядок — спробуємо його розпарсити як JSON
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return ', '.join(str(v) for v in parsed)
            except (json.JSONDecodeError, TypeError):
                pass
            # Якщо не JSON, повертаємо як є (можливо вже у форматі 'red, blue')
            return value
        return super().format_value(value)

    def value_from_datadict(self, data, files, name):
        raw_value = data.get(name, '')
        if raw_value:
            # Розбиваємо рядок по комах та обрізаємо пробіли
            return [item.strip() for item in raw_value.split(',') if item.strip()]
        return []
