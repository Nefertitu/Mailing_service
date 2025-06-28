from django import template

register = template.Library()

@register.filter
def model_type(obj) -> str:
    """Возвращает имя класса объекта в виде строки"""
    return obj.__class__.__name__


@register.filter(name='select_model_type')
def select_model_type(items, model_type) -> list:
    """Фильтрует список объектов по типу модели"""
    return [item for item in items if item.__class__.__name__ == model_type]
