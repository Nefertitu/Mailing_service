from typing import Any, Iterable

from django import template

register = template.Library()


@register.filter
def model_type(object: Any) -> str:
    """Возвращает имя класса объекта в виде строки"""
    return object.__class__.__name__


@register.filter(name="select_model_type")
def select_model_type(items: Iterable, model_type: str) ->  list:
    """Фильтрует список объектов по типу модели"""
    return [item for item in items if item.__class__.__name__ == model_type]
