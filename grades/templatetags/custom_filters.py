from django import template

register = template.Library()

# used to get the number of graded and remaining submissions in the profile
@register.filter
def get_value(dictionary, key):
    return dictionary.get(key, 0)