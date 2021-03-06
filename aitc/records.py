# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import re
import hashlib
import base64

# Regex matching a UUID in uppercase 8-4-4-4-12 hexadecimal format.
VALID_UUID_REGEX = re.compile("^[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-"\
                              "[A-Z0-9]{4}-[A-Z0-9]{12}$")


def origin_to_id(value):
    """Encode an application origin into a fixed-length id."""
    if isinstance(value, unicode):
        value = value.encode("utf8")
    digest = hashlib.sha1(value).digest()
    return base64.urlsafe_b64encode(digest).rstrip("=")


class Record(dict):
    """Base class for dealing with different types of record."""

    FIELDS = set()

    def __init__(self, data=None, ignore_unknown_fields=False):
        super(Record, self).__init__()
        if data is None:
            data = {}

        try:
            data_items = data.items()
        except AttributeError:
            cls_name = self.__class__.__name__
            msg = "%s data must be dict-like, not %s"
            raise ValueError(msg % (cls_name, type(data),))

        for name, value in data_items:
            if name not in self.FIELDS and not ignore_unknown_fields:
                cls_name = self.__class__.__name__
                raise ValueError("Unknown %s field %r" % (cls_name, name,))
            if value is not None:
                self[name] = value

    def get_id(self):
        raise NotImplementedError  # pragma: nocover

    def populate(self, request, old_item=None):
        self["modifiedAt"] = request.server_time

    def abbreviate(self):
        raise NotImplementedError  # pragma: nocover

    def validate(self):
        raise NotImplementedError  # pragma: nocover


class AppRecord(Record):
    """Class for working with App record data."""

    FIELDS = set(("origin", "manifestPath", "installOrigin", "installedAt",
                  "modifiedAt", "name", "hidden", "receipts"))

    def get_id(self):
        return origin_to_id(self["origin"])

    def populate(self, request, old_item=None):
        super(AppRecord, self).populate(request, old_item)
        if old_item is not None:
            self["installedAt"] = old_item["installedAt"]
        else:
            self["installedAt"] = request.server_time

    def abbreviate(self):
        return {
            "origin": self["origin"],
            "modifiedAt": self["modifiedAt"],
        }

    def validate(self):
        # This catches KeyErrors, which indicate missing fields.
        try:
            # Check that paths are URL strings.
            for field in ("origin", "manifestPath", "installOrigin"):
                if not isinstance(self[field], basestring):
                    return False, "%s must be a string" % (field,)

            # Check that the name is a string.
            field = "name"
            if not isinstance(self[field], basestring):
                return False, "name must be a string"

            # Check that timestamps are integers.
            for field in ("installedAt", "modifiedAt"):
                if not isinstance(self[field], (int, long)):
                    return False, "%s must be an integer" % (field,)

            # Check that receipts is a list of strings.
            field = "receipts"
            receipts = self[field]
            if not isinstance(receipts, list):
                return False, "receipts must be a list"
            for receipt in receipts:
                if not isinstance(receipt, basestring):
                    return False, "receipts must be a list of strings"

            # Check that hidden, if present, is boolean true.
            if self.get("hidden") not in (None, True):
                return False, "hidden must be boolean true"
        except KeyError:
            return False, "missing field %r" % (field,)

        return True, None


class DeviceRecord(Record):
    """Class for working with Device record data."""

    FIELDS = set(("uuid", "name", "type", "layout", "addedAt",
                  "modifiedAt", "apps"))

    def get_id(self):
        return self["uuid"]

    def populate(self, request, old_item=None):
        super(DeviceRecord, self).populate(request, old_item)
        if old_item is not None:
            self["addedAt"] = old_item["addedAt"]
        else:
            self["addedAt"] = request.server_time

    def abbreviate(self):
        abrv = self.copy()
        abrv.pop("apps", None)
        return abrv

    def validate(self):
        # This catches KeyErrors, which indicate missing fields.
        try:
            # Check that various fields are strings.
            for field in ("name", "type", "layout"):
                if not isinstance(self[field], basestring):
                    return False, "%s must be a string" % (field,)
                elif not self[field]:
                    return False, "%s must be non-empty" % (field,)

            # Check that timestamps are integers.
            for field in ("addedAt", "modifiedAt"):
                if not isinstance(self[field], (int, long)):
                    return False, "%s must be an integer" % (field,)

            # Check that uuid is valid and in proper format.
            field = "uuid"
            if not VALID_UUID_REGEX.match(self["uuid"]):
                return False, "uuid must be a valid UUID"

            # Check that apps is a dict
            field = "apps"
            if not isinstance(self["apps"], dict):
                return False, "apps must be a dict"
        except KeyError:
            return False, "missing field %r" % (field,)

        return True, None
