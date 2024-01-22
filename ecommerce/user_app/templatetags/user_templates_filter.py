from django import template
register = template.Library()

@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    return round((qty) * (unit_price),2)

@register.simple_tag()
def getprogress(value):
    print('value',value)
    return int(((int(value))/4)*100)

@register.simple_tag()
def get_offerprice(price,offer):
    return round(price-(price/offer), 2)