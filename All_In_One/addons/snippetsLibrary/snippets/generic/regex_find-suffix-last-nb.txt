rx = re.compile(r'(.*)(.\d{3})$')
# ex: on 'theName.001'
# \1 = 'theName'
# \2 = '.001'
rx.match(ob.name)
rx.sub(r'\1', ob.name)

#direct
re.match(r'.*(.\d{3})$', ob.name)
re.sub(r'(.*)(.\d{3})$', r'\1', ob.name)