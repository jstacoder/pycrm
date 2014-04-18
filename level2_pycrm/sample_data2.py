# coding: utf-8
keys = USERS.keys()
userA = USERS[keys[0]]
userb = USERS[keys[1]]
template = 'Name: {name}\nEmail: {email}\n\nRelated Agencies: {agencies}\n\nRelated Contacts: {contacts}\n'
print template.format(**userA)
print template.format(**userb)