# -*- coding: utf-8 -*-
"""dictexpire
  __init__.py module.
 
  - Author:     
  - License:    
  - Created:    15-11-2018
  - Modified:   15-11-2018
"""
import time
import typing as tp


class TimeCacheValue:

    def __init__(self, value, expire_secs=None):
        self.expire_secs = int(expire_secs or 60)
        self._expire_timestamp = time.time() + self.expire_secs
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return self.__repr__()

    @property
    def is_expired(self):
        has_expired = self.remaining <= 0.0
        return has_expired

    @property
    def remaining(self):
        seconds_left = self._expire_timestamp - time.time()
        return int(seconds_left)


class DictExpire:

    def __init__(self, **kwargs):
        self.data = dict(default_expire_secs=60)
        # self.default_expire_secs = 60
        if 'default_expire_secs' in kwargs:
            self.data['default_expire_secs'] = int(kwargs.pop('default_expire_secs'))
        self.data = {k: TimeCacheValue(v, expire_secs=self.data['default_expire_secs']) for k, v in kwargs.items()}

    def __contains__(self, k):
        """
        Return True or False depending on "k" existence.

        >>> 'b' in DictExpire(a=1, b=2)
        True
        >>> 'z' in DictExpire(a=1, b=2)
        False

        :return bool: True or False depending on "k" existence.
        """
        self._drop_expired()
        return k in self.data

    def __len__(self):
        """
        Get an int type with the number elements currently stored.

        >>> len(DictExpire(a=1, b=2))
        2

        :return int: the number elements currently stored.
        """
        if len(self.data):
            self._drop_expired()
        return len(self.data)

    def __getitem__(self, k):
        """
        Get value stored for "k" key.

        >>> DictExpire(a=1, b=2)['a']
        1

        :param str k:
        :return tp.Any: value stored for "k" key.
        """
        self._drop_expired(k)
        value = None
        try:
            value = self.data[k]
        except KeyError:
            pass
        return value or TimeCacheValue(0, 0)

    def __setitem__(self, k, v):
        """
        Set "v" value to "k" key.

        >>> de = DictExpire(a=1, b=2)
        >>> de['a'] = 10
        >>> de['a']
        10

        :param str k:
        :return tp.Any: value stored for "k" key.
        """
        self._drop_expired(k)
        if not isinstance(v or 0, TimeCacheValue):
            v = TimeCacheValue(v, expire_secs=self.data.get('default_expire_secs', 60))
        self.data.update(**{k: v})

    def __delitem__(self, k):
        """
        Delete "k" item, if k not found no Exception will be raised.

        >>> de = DictExpire(a=1, b=2)
        >>> del de['a']
        >>> de.keys()
        ['b']

        :param str k:
        :return tp.Any: value stored for "k" key.
        """
        try:
            del self.data[k]
        except KeyError:
            pass

    def popitem(self, default=None):
        """
        Get (and remove) the oldest dict item, if DictExpire is empty "default" param value will be returned).
        >>> de = DictExpire(a=1, b=2)
        >>> de.popitem()
        1

        :param tp.Any default: value to be returned if DictExpire is empty.
        :return tp.Any: oldest dict item, if DictExpire is empty "default" param value will be returned).
        """

        if len(self.data):
            k = self.keys()[0]
            v = self.data.get(k)
            if v and v.is_expired:
                del self.data[self.keys()[0]]
                v = default
            return v or default
        else:
            return default

    def pop(self, key, default=None):
        """
        Get (and remove) "key" item from DictExpire and return it's value, if key not exists, default value will be
        returned.

        >>> de = DictExpire(a=1, b=2)
        >>> de.pop('a')
        1

        :param key:
        :param default:
        :return:
        """
        self._drop_expired()
        if value := self.data.get(key or '', default) or default:
            del self.data[key]
            return value
        else:
            return default

    def keys(self):
        """
        Get keys as list.

        >>> de = DictExpire(a=1, b=2)
        >>> keys = de.keys()
        >>> keys[1]
        'b'

        :return list: DictExpire keys as list type.
        """
        if len(self.data):
            self._drop_expired()
        return list(self.data.keys())

    def values(self):
        """
        Get stored values as list.

        >>> de = DictExpire(a=1, b=2)
        >>> values = de.values()
        >>> values[0]
        1

        :return list: DictExpire keys as list type.
        """
        self._drop_expired()
        return [v.value for v in self.data.values()]

    def __iter__(self):
        """
        Return all key-pair items as dict_keyiterator.

        >>> de = DictExpire(a=1, b=2)
        >>> type(iter(de)).__name__
        'dict_keyiterator'

        :return tp.Iterator: all key-pair items as iterator.
        """
        if len(self.data):
            self._drop_expired()
        return self.data.__iter__()

    def set(self, key, value, expire_secs=None):
        """
        Add key-pair item with with specific expire secs, if no expire_secs is supplied, ExpireDict default will be set.
        >>> de = DictExpire()
        >>> de.set('c', 100.0, expire_secs=2)
        >>> de['c']
        100.0
        >>> time.sleep(2)
        >>> 'c' in de
        False
        
        :param str key: key to set or update.
        :param tp.Any value: value to be stored supplied "key"
        :param int expire_secs: specific expire seconds as int.       
        """
        expire_secs = int(expire_secs or self.default_expire_secs)
        value = TimeCacheValue(value, expire_secs=expire_secs)
        self.__setitem__(key, value)

    def items(self):
        """
        Return all items stored in DictExpire "self" instance as a list of tuples [(k1, v1), (k2, v2), ...].

        >>> de = DictExpire(default_expire_secs=2, a=1, b=2)
        >>> de.items()
        [('a', 1), ('b', 2)]

        :return list: a list of key-pair items as tuples.
        """
        self._drop_expired()
        return list(self.data.items())

    def _drop_expired(self, k=None):
        """
        Check and remove expired items.

        >>> de = DictExpire(default_expire_secs=2, a=1, b=2)
        >>> time.sleep(2.1)
        >>> de._drop_expired()
        >>> len(de)
        0

        """

        def del_if_expired(kk):
            value = self.data[kk] if kk in self.data else None
            if value and value.is_expired:
                del self.data[kk]

        if k and k in self.data.keys():
            del_if_expired(k)
        elif k is None:
            for k in dict(self.data):
                del_if_expired(k)

    @staticmethod
    def fromkeys(seq, **kwargs):
        """
        Like "dict" built in method but accepting "default_expire_secs" key with default expiration time value.

        >>> DictExpire.fromkeys(['a', 'b'])
        [DictExpire]({'a': None, 'b': None})

        :param tp.Iterable seq: an iterable type with desired keys for returned DictExpire instance.
        :param kwargs: accepted keys -> "default", "default_expire_secs"
        :return:
        """
        if default := kwargs.get('default'):
            del kwargs['default']
            kwargs.update(dict.fromkeys(seq, default))
        else:
            kwargs.update(dict.fromkeys(seq))

        return DictExpire(**kwargs)

    def __repr__(self):
        """
        DictExpire object representation as str.

        >>> de = DictExpire(default_expire_secs=2, a=1, b=2)
        >>> repr(de)
        "[DictExpire]({'a': 1, 'b': 2})"

        :return str: DictExpire object representation as str
        """
        # self._drop_expired()
        return '[{}]({})'.format(type(self).__name__, self.data)

    def __str__(self):
        """
        DictExpire object representation as str.

        >>> de = DictExpire(default_expire_secs=2, a=1, b=2)
        >>> str(de)
        "{'a': 1, 'b': 2}"

        :return str: DictExpire object representation as str
        """
        # self._drop_expired()
        return str(self.data)

    def __getattr__(self, item):
        """
        Provide items access as attributes.

        >>> de = DictExpire(default_expire_secs=2, a=1, b=2)
        >>> de.b
        2

        :param str n: attribute name. It should match with any existing item at attribute dict "data".
        :return:
        """

        if item != 'data' and item in self.data:
            return self.__dict__['data'][item]
        elif item in self.__dict__:
            return self.__dict__[item]
        elif item in self:
            return self[item]
        else:
            return None

    def __setattr__(self, n, v):
        """
        Provide items access as attributes.

        >>> de = DictExpire(default_expire_secs=2, a=1, b=2)
        >>> de.b = 10
        >>> de.b
        10

        :param str n: attribute name. It should match with any existing item at attribute dict "data".
        :param str v: value to be assigned to.
        """
        if n != 'data':
            # if n in self._dict__['data']:
            self.__dict__['data'].update({n: v})
        else:
            self.__dict__[n] = v


# if __name__ == '__main__':
#     sc = DictExpire(default_expire_secs=5, c=9)
#     print(sc)
#     time.sleep(2)
#     sc.set('a', 11, expire_secs=2)
#     print('c ', sc['c'].remaining, 'seconds to expire')
#     sc['b'] = 300
#     print(sc['b'].expire_secs)
#     print(sc)
#     print(sc.values())
#     print(sc.keys())
#     time.sleep(5)
#     print('c' in sc)
#     print(sc)
