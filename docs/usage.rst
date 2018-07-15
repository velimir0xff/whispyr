=====
Usage
=====

Initialisation
--------------

To use whispyr in a project you need to have valid whispir.io credentials (username, password and API key)::

  from whispyr import Whispir

  TEST_USERNAME = 'U53RN4M3'
  TEST_PASSWORD = 'P4ZZW0RD'
  TEST_API_KEY = 'V4L1D4P1K3Y'

  whispir = Whispir(TEST_USERNAME, TEST_PASSWORD, TEST_API_KEY)


Available resources
-------------------

Instance of class ``Whispir`` contains all available resources (workspaces, messages, templates, response rules and etc, you can find more on official whispir API documentaion page https://whispir.github.io/api) as its members::

  >>> whispir.workspaces
  <whispyr.whispyr.Workspaces object at 0x10f1c2eb8>
  >>> whispir.messages
  <whispyr.whispyr.Messages object at 0x10f1c2e80>
  ...

Resources in plural form are collections which provide an access to containers. For example ``workspaces`` is a workspace resource and it provides CRUD functionality for workspaces.


Collections actions
-------------------

Each collection has ``create``, ``show``, ``list``, ``update`` and ``delete`` functions to work with objects.
All passed arguments passed as is to json encoder. Library doesn't perform any checks or validations, which means that you need to know required parameters and their format before you can call any of mentioned actions.

create
~~~~~~

``create`` makes a ``POST`` request for a given resource::

  name = 'whispyr tests'
  new_workspace = whispir.workspaces.create(projectName=name, status='A')

returned object is a container for a created resource. For this example it's an instance of ``whispyr.Workspace``::

  from whispyr import Workspace
  assert isinstance(workspace, Workspace)


All containers are dictionary like objects which wraps response from whispir.io API and provides an access to other resources available under some particular instance of an entity.

show
~~~~

``show`` makes a ``GET`` request for a given resource with a provided ID::

  workspace = whispir.workspaces.show(new_workspace['id'])
  assert isinstance(workspace, Workspace)
  assert 'id' in workspace
  assert 'projectName' in workspace


list
~~~~

``list`` makes a ``GET`` request for a given resource to return all available objects (library takes care about pagination)::

  for workspace in whispir.workspaces.list():
      assert isinstance(workspace, Workspace)
      assert 'id' in workspace
      assert 'projectName' in workspace


update
~~~~~~
``update`` makes a ``PUT`` request for a given resource with a provided ID to update/edit a resource with specified parameters::

  whispir.contacts.update(
      contact_id,
      firstName='John',
      lastName='Wick',
      timezone='Australia/Melbourne',
      workCountry='Australia'
  )


delete
~~~~~~

``delete`` makes a ``DELETE`` request for a given resource with a provided ID::

  whispir.contacts.delete(contact['id'])


Container resources
-------------------

Some containers (such as ``whispyr.Workspace`` and ``whispyr.Message``) might provide an access to some collections.

Workspace
~~~~~~~~~

You might find it useful to limit the work to some workspace (sandbox in test env for instance) and do not put all objects in a global space::

  project_name = 'whispyr tests'
  workspace = next(ws for ws in whispir.workspaces.list()
                   if ws['projectName'] == 'sandbox')
  for contact in workspace.contacts.list():
      print(contact['firstName'])

Alternatively, if you know workspace ID::

  workspace = whispir.workspaces.Workspace(id='C3A1B60DEED39BB3')


Message
~~~~~~~~

Message container provides an access to all message's resources such as message statuses and responses::

  message = workspace.messages.send(to=contact['mri'],
                                    subject='whispyr test',
                                    body='test message, please disregard')
  for status in message.statuses.list():
      for category in status['categories']:
          print('{}: {}'.format(category['name'], category['recipientCount']))
