from flask_dashed.dashboard import DefaultDashboard, DashboardWidget, HelloWorldWidget
"""
USERS - name, email, password, contacts, agencies


CONTACTS - name, email, agencies, location, phone, address


AGENCIES - name, email, contacts, main-contact, phone, alt-phone, zone
"""
def display():
    USERS = {
         'one' : {
            'name': 'kyle',
            'email': 'kyle@level2designs.com',
            'contacts': [
                'tom','hank','grace','linda'
                        ],
                },
        'two' : {
            'name': 'joe',
            'email': 'joe@f.com',
            'contacts': [
                'george','arron','ron'
                        ],
            }
        }





    # coding: utf-8
    keys = USERS.keys()
    userA = USERS[keys[0]]
    userb = USERS[keys[1]]
    template = '<strong>Name</strong>: {name}<br /><strong>Email</strong>: {email}<br /><br /><strong>Related Contacts</strong>: {contacts}<br />'
    rtn = '<br /><p>'
    rtn += template.format(**userA)
    rtn += '</p><br />'
    rtn += template.format(**userb)
    rtn += '</p><br />'
    return rtn





class DisplayContactsWidget(DashboardWidget):
    def render(self):
        return display()


class ContactsDashboard(DefaultDashboard):
    """Default dashboard."""
    widgets = [HelloWorldWidget('Level2CRM Dashboard'),DisplayContactsWidget('Latest Contacts')]





