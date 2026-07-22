import os
d = '/Users/lijianqiang/Documents/odoo18_tms/addons/wd_tlms'

# 1) __init__.py
fp = os.path.join(d, 'models/__init__.py')
with open(fp) as f:
    c = f.read()
c = c.replace('from . import transport_fee_type\n', '')
with open(fp, 'w') as f:
    f.write(c)
print('OK: __init__.py')

# 2) __manifest__.py
fp = os.path.join(d, '__manifest__.py')
with open(fp) as f:
    c = f.read()
old = "'fleet',\n    ],"
new = "'fleet', 'worlddepot',\n    ],"
c = c.replace(old, new)
with open(fp, 'w') as f:
    f.write(c)
print('OK: __manifest__.py')

# 3) ir.model.access.csv
fp = os.path.join(d, 'security/ir.model.access.csv')
with open(fp) as f:
    lines = f.readlines()
new_lines = [l for l in lines if 'transport_fee_type' not in l]
with open(fp, 'w') as f:
    f.writelines(new_lines)
print('OK: ir.model.access.csv')

# 4) tlmp_menus.xml
fp = os.path.join(d, 'views/tlmp_menus.xml')
with open(fp) as f:
    c = f.read()
c = c.replace('''    <menuitem id=\"menu_tlmp_fee_types\" name=\"Fee Types\" parent=\"menu_tlmp_config\"
              action=\"action_transport_fee_type\" sequence=\"30\"/>
''', '')
with open(fp, 'w') as f:
    f.write(c)
print('OK: tlmp_menus.xml')

print('All registrations updated')
