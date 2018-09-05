from errbot import BotPlugin, botcmd, arg_botcmd
from simple_salesforce import Salesforce


class SFDC(BotPlugin):
    
    def activate(self):
        """
        Triggers a plugin activation
        """

        super(SFDC, self).activate()
        self.log.info('booting Salesforce')
    
    def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports
        """
        return {'username': None,
                'password': None,
                'security_token': None
                }

    def get_salesforce(self):
        """
        Get an instance of Salesforce.
        Username, password and security come from self.config
        :return a `Salesforce` instance
        """

        sf = Salesforce(username=self.config['username'],
                        password=self.config['password'], 
                        security_token=self.config['security_token'])
        return sf

    @botcmd  
    def contact(self, msg, args):
        """
        This command retrieves a Salesforce Contact given its Name
        :return Name, Email and Phone number of the Contact
        """

        sfdc_api = self.get_salesforce()

        query = sfdc_api.query("SELECT Id, Email, Phone, Title, Name "
                               "FROM Contact " 
                               "WHERE Name LIKE " + f"'%{args}%'")

        if query['records'] and args:
            for record in query['records']:
                self.send_card(title='Contact',
                               body=f'I found this contact for {args}',
                               link='http://login.salesforce.com/' + record['Id'],
                               fields=(('Name', record['Name']),
                                       ('Email', record['Email']),
                                       ('Phone', record['Phone']),
                                       ('Title', record['Title']),
                                       ('Link', 'http://login.salesforce.com/' + record['Id'])),
                               color='cyan',
                               in_reply_to=msg)
        elif not args:
            return "You should provide an argument to the command"
        else:
            return f"I could not find any record on {args}"

    @botcmd
    def account(self, msg, args):
        """
        This command retrieves a Salesforce Account given its Name
        :return Name
        """
        query = self.get_salesforce().query("SELECT Id, Name, AnnualRevenue, BillingAddress, Website, Phone FROM Account WHERE Name LIKE " + f"'%{args}%'")
        if query['records'] and args:
            for record in query['records']:
                self.send_card(title='Contact',
                               body=f'I found this contact for {args}',
                               link='http://login.salesforce.com/' + record['Id'],
                               fields=(('Name', record['Name']),
                                       ('Annual Revenue', record['AnnualRevenue']),
                                       ('Address', record['BillingAddress']['street']),
                                       ('City', record['BillingAddress']['city']),
                                       ('State', record['BillingAddress']['country']),
                                       ('Website', record['Website']),
                                       ('Phone', record['Phone']),
                                       ('Link', 'http://login.salesforce.com/' + record['Id'])),
                               color='cyan',
                               in_reply_to=msg)
        elif not args:
            return "You should provide an argument to the command"
        else:
            return f"I could not find any record on {args}"

    @arg_botcmd('lastname', type=str)
    @arg_botcmd('-ph', '--phone', dest='phone', type=str)
    @arg_botcmd('-em', '--email', dest='email', type=str)
    def create(self, msg, lastname=None, phone=None, email=None):
        """
        This command create a new Salesforce Contact with a give LastName,
        Phone and Email address
        """

        sfdc_api = self.get_salesforce()

        newcontact = sfdc_api.Contact.create({'LastName': lastname, 
                                              'Phone': phone, 
                                              'Email': email})

        return 'New Contact created Id: {}'.format(newcontact['id'])
