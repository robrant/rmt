import re

x = 'page'
y = re.match('[a-z]', x)
print y.group()