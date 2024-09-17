from hypothesis import given, assume, strategies as st
from randomdict import RandomDict
# from indexed_dict import IndexedDict  # Adjust the import path as necessary

# Define a strategy for hashable keys
hashable_keys = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(),
    st.binary(),
    st.tuples(),
    st.tuples(st.none(), st.booleans(), st.integers(), st.text()),
    st.frozensets(st.integers()),
)

# 1. Test that inserting and retrieving a key-value pair works correctly.
@given(k=hashable_keys, v=st.integers())
def test_insertion_retrieval(k, v):
    d = RandomDict()
    d[k] = v
    assert d[k] == v, "Value retrieved does not match the value inserted."

# 2. Test that overwriting a key updates its value.
@given(k=hashable_keys, v1=st.integers(), v2=st.integers())
def test_overwriting(k, v1, v2):
    d = RandomDict({k: v1})
    d[k] = v2
    assert d[k] == v2, "Key overwrite did not update the value."

# 3. Test that deleting a key removes it from the dictionary.
@given(k=hashable_keys, v=st.integers())
def test_deletion(k, v):
    d = RandomDict({k: v})
    del d[k]
    assert k not in d, "Key was not removed after deletion."

# 4. Test that the length of the dictionary is correct.
@given(d=st.dictionaries(hashable_keys, st.integers()))
def test_length(d):
    d = RandomDict(d)
    assert len(d) == len(d.keys()), "Length mismatch between dict and keys."
    assert len(d) == len(d.items()), "Length mismatch between dict and items."
    assert len(d) == len(d.values()), "Length mismatch between dict and values."

# 5. Test iteration over keys, values, and items.
@given(d=st.dictionaries(hashable_keys, st.integers()))
def test_iteration(d):
    d = RandomDict(d)
    keys = list(d.keys())
    values = list(d.values())
    items = list(d.items())
    assert len(keys) == len(d), "Incorrect number of keys iterated."
    assert len(values) == len(d), "Incorrect number of values iterated."
    assert len(items) == len(d), "Incorrect number of items iterated."
    for k, v in items:
        assert d[k] == v, f"Value mismatch for key {k} during iteration."

# 6. Test that accessing a missing key raises KeyError.
@given(d=st.dictionaries(hashable_keys, st.integers()), k=hashable_keys)
def test_missing_key(d, k):
    d = RandomDict(d)
    assume(k not in d)
    try:
        _ = d[k]
        assert False, "Accessing a missing key did not raise KeyError."
    except KeyError:
        pass  # Expected behavior

# 7. Test updating a dictionary with another dictionary.
@given(d1=st.dictionaries(hashable_keys, st.integers()),
       d2=st.dictionaries(hashable_keys, st.integers()))
def test_update(d1, d2):
    d1 = RandomDict(d1)
    d2 = RandomDict(d2)
    d = d1.copy()
    d.update(d2)
    for k in d2:
        assert d[k] == d2[k], f"Key {k} not updated correctly."
    for k in d1:
        if k not in d2:
            assert d[k] == d1[k], f"Key {k} incorrectly modified."

# 8. Test copying a dictionary.
@given(d=st.dictionaries(hashable_keys, st.integers()))
def test_copy(d):
    d = RandomDict(d)
    d_copy = d.copy()
    assert d == d_copy, "Copied dictionary does not match the original."
    assert d is not d_copy, "Copy did not create a new dictionary object."

# 9. Test that clearing a dictionary empties it.
@given(d=st.dictionaries(hashable_keys, st.integers()))
def test_clear(d):
    d = RandomDict(d)
    d.clear()
    assert len(d) == 0, "Dictionary not empty after clear."

# 10. Test the fromkeys class method.
@given(keys=st.lists(hashable_keys, unique=True), v=st.integers())
def test_fromkeys(keys, v):
    d = RandomDict.fromkeys(keys, v)
    for k in keys:
        assert d[k] == v, f"Key {k} does not have the correct value."

# 11. Test that deleting a non-existent key raises KeyError.
@given(d=st.dictionaries(hashable_keys, st.integers()), k=hashable_keys)
def test_delete_missing_key(d, k):
    d = RandomDict(d)
    assume(k not in d)
    try:
        del d[k]
        assert False, "Deleting a missing key did not raise KeyError."
    except KeyError:
        pass  # Expected behavior

# 12. Test dictionary equality and inequality.
@given(d=st.dictionaries(hashable_keys, st.integers()))
def test_equality(d):
    d = RandomDict(d)
    d_copy = d.copy()
    assert d == d_copy, "Copied dictionary should be equal to the original."
    if d:
        k = next(iter(d))
        d_copy[k] += 1  # Modify one value
        assert d != d_copy, "Dictionaries should not be equal after modification."

# 13. Test that dictionaries handle different hashable types as keys.
@given(k1=hashable_keys, v1=st.integers(), k2=hashable_keys, v2=st.integers())
def test_different_keys(k1, v1, k2, v2):
    assume(k1 != k2)
    d = RandomDict({k1: v1, k2: v2})
    assert d[k1] == v1, f"Incorrect value for key {k1}."
    assert d[k2] == v2, f"Incorrect value for key {k2}."

# 14. Test that keys must be hashable (unhashable keys raise TypeError).
@given(k=st.sampled_from([[], {}, set()]), v=st.integers())
def test_unhashable_keys(k, v):
    try:
        d = RandomDict()
        d[k] = v
        assert False, "Assigning unhashable key did not raise TypeError."
    except TypeError:
        pass  # Expected behavior

# 15. Test that the get method returns default when key is missing.
@given(d=st.dictionaries(hashable_keys, st.integers()), k=hashable_keys, default=st.integers())
def test_get_method(d, k, default):
    d = RandomDict(d)
    result = d.get(k, default)
    if k in d:
        assert result == d[k], "Get method did not return the correct value."
    else:
        assert result == default, "Get method did not return the default value."

# 16. Test that the setdefault method works correctly.
@given(d=st.dictionaries(hashable_keys, st.integers()), k=hashable_keys, default=st.integers())
def test_setdefault(d, k, default):
    d = RandomDict(d)
    original = d.copy()
    result = d.setdefault(k, default)
    if k in original:
        assert result == original[k], "Setdefault did not return existing value."
    else:
        assert result == default, "Setdefault did not return default value."
        assert d[k] == default, "Setdefault did not set the default value."

# 17. Test that pop removes and returns the correct value.
@given(d=st.dictionaries(hashable_keys, st.integers()), k=hashable_keys)
def test_pop_method(d, k):
    d = RandomDict(d)
    original = d.copy()
    if k in d:
        result = d.pop(k)
        assert result == original[k], "Pop did not return the correct value."
        assert k not in d, "Key was not removed after pop."
    else:
        try:
            d.pop(k)
            assert False, "Popping a missing key did not raise KeyError."
        except KeyError:
            pass  # Expected behavior

# 18. Test that popitem removes and returns a (key, value) pair.
@given(d=st.dictionaries(hashable_keys, st.integers()))
def test_popitem_method(d):
    d = RandomDict(d)
    original_len = len(d)
    if d:
        k, v = d.popitem()
        assert k not in d, "Key was not removed after popitem."
        assert len(d) == original_len - 1, "Dictionary size did not decrease after popitem."
    else:
        try:
            d.popitem()
            assert False, "Popitem on empty dictionary did not raise KeyError."
        except KeyError:
            pass  # Expected behavior

# 19. Test that the dictionary view objects reflect changes in the dictionary.
@given(d=st.dictionaries(hashable_keys, st.integers()), k=hashable_keys, v=st.integers())
def test_views_reflect_changes(d, k, v):
    d = RandomDict(d)
    keys_view = d.keys()
    values_view = d.values()
    items_view = d.items()
    original_len = len(d)
    k_in_d_before = k in d  # Check if the key exists before modification

    d[k] = v  # Modify the dictionary

    # Check if the length of the keys view has updated correctly
    if not k_in_d_before:
        assert len(keys_view) == original_len + 1, "Keys view did not update after insertion."
    else:
        assert len(keys_view) == original_len, "Keys view size changed unexpectedly."

    # Verify that the new key, value, and item are present in their respective views
    assert k in keys_view, "New key not present in keys view."
    assert v in values_view, "New value not present in values view."
    assert (k, v) in items_view, "New item not present in items view."

# 20. Test that the dictionary correctly handles hash collisions.
class HashCollision:
    def __init__(self, value):
        self.value = value
    def __hash__(self):
        return 42  # Arbitrary constant hash value to force collision
    def __eq__(self, other):
        if isinstance(other, HashCollision):
            return self.value == other.value
        return False

@given(v1=st.integers(), v2=st.integers())
def test_hash_collisions(v1, v2):
    k1 = HashCollision('key1')
    k2 = HashCollision('key2')
    assume(k1 != k2)
    d = RandomDict({k1: v1, k2: v2})
    assert d[k1] == v1, "Incorrect value retrieved for key with hash collision."
    assert d[k2] == v2, "Incorrect value retrieved for key with hash collision."
