# myapp/templatetags/custom_filters.py
from django import template
from django import forms


register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})


@register.filter(name='add_class')
def add_class(value, css_class):
    if hasattr(value.field.widget, 'attrs'):
        if not isinstance(value.field.widget, forms.CheckboxInput):
            value.field.widget.attrs['class'] = css_class
    return value

