# -*- coding: utf-8 -*-


"""Contacts tests for `whispyr` package"""

import pytest

from whispyr import Contact, ClientError


@pytest.mark.parametrize('contacts', [4], indirect=True)
def test_list_contacts(workspace, cassette, contacts):
    _check_list(workspace, contacts, 4)


@pytest.mark.parametrize('contacts', [55], indirect=True)
def test_list_contacts_paginated(workspace, cassette, contacts):
    _check_list(workspace, contacts, 55)


def test_show_contact(workspace, cassette, contact):
    contact = workspace.contacts.show(contact['id'])
    _check_basic_contact(contact)


def test_show_generic_contact(whispir, cassette, generic_contact):
    contact = whispir.contacts.show(generic_contact['id'])
    _check_basic_contact(contact)


def test_update_contact(workspace, cassette, contact):
    contact_id = contact['id']
    first_name = contact['firstName']
    last_name = contact['lastName']
    new_first_name = '{} updated'.format(first_name)
    new_last_name = '{} updated'.format(last_name)
    workspace.contacts.update(
        contact_id,
        firstName=new_first_name,
        lastName=new_last_name,
        timezone=contact['timezone'],
        workCountry=contact['workCountry']
    )
    updated_contact = workspace.contacts.show(contact_id)
    assert updated_contact['firstName'] == new_first_name
    assert updated_contact['lastName'] == new_last_name


@pytest.mark.parametrize('contact', [False], indirect=True)
def test_delete_contact(workspace, cassette, contact):
    _test_delete(workspace.contacts, contact['id'])


@pytest.mark.parametrize('generic_contact', [False], indirect=True)
def test_delete_generic_contact(whispir, cassette, generic_contact):
    _test_delete(whispir.contacts, generic_contact['id'])


def _test_delete(contacts, contact_id):
    contacts.delete(contact_id)
    with pytest.raises(ClientError) as excinfo:
        contacts.show(contact_id)

    exc = excinfo.value
    assert exc.response.status_code == 404


def _check_list(workspace, contacts, expected_count):
    contacts = workspace.contacts.list()
    contacts = list(contacts)
    assert len(contacts) == len(contacts)
    assert len(contacts) == expected_count
    for contact in contacts:
        _check_basic_contact(contact)


def _check_basic_contact(contact):
    assert isinstance(contact, Contact)
    assert 'id' in contact
    assert 'firstName' in contact
    assert 'lastName' in contact
