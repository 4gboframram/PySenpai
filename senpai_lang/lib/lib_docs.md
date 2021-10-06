# Senpai Python Builtin Library
## Intro
To access the builtin library, you can import `%lib%/{file}.py` when using Senpai code.
- If the function is a wrapper for a method of an object, the object should be the last argument of the function and the original object should be the last return value of the function.
  - An exception to this is when the method acts as a finalizer for the object (such as `file_close`).


## `%lib%/file.py`
Contains the module `file`, which
provides a wrapper for Python's `open()` function and methods of the object that can be returned.
If you don't understand the effects of some of these methods, [see Python's io module](https://docs.python.org/3/library/io.html)

- `file_open.call(path)`: Opens a file at `path` in `rb+` mode. Creates a file at `path` and opens it if the file at `path` doesn't exist. Returns a `BufferedRandom` Python object.

- `file_read.call(file) or file_read.call(value, file)`: Calls `file`'s `read()` method with args of `value` if `value` given. Returns a Python `Bytes` object and the `file`. Unfortunately, you can't really do much with a `Bytes` object in Senpai except for writing to a file yet.

- `file_write.call(item, file)`: Writes a string or `Bytes` object to `file`. Returns the `file`.

- `file_seek.call(arg, file)`: Changes the position of the stream to the value of `arg`. If `arg == 'end'`, seeks the end of the stream. Returns the `file` object.

- `file_tell.call(file)`: Tells the stream's current position. Returns an `int` and the file object.

## `%lib%/senpai_os.py`
Contains the `os` module, which for now only contains a wrapper for `os.system()`:

- `os_cmd.call(cmd) or os_cmd.call(cmd, anything)`: Executes `cmd` as a system command and does not have a return value. If a second argument is given, returns the value of `os.system(cmd)`. 

## `%lib%/containers.py`

Contains utilities for working with Python iterables (including strings) and adds a way to initialize iterables.

As of right now, contains 2 modules: `list` and `container`, but will be expanded in the future to contain more iterables.
- The `container` module contains general utilities for working with iterables, such as wrappers for `__set_item__` and `__get_item__`
- The `list` module contains wrappers for the methods of a `SenpaiList` (basically a `collections.deque`).

### `list`
- `list_new.call(*args)`: Returns a new `SenpaiList` (which inherits off of `collections.deque`, so whatever it can take in as arguments).

- `list_insert_back.call(item, list)`: Appends `item` to the end of `list` and returns the updated `list`.

- `list_insert_front.call(item, list)`: Inserts `item` in the front of the `list`. Returns the updated `list`.

### `container`
- `container_get.call(index, container)`: Returns `container.__getitem__(index)` and the `container`

- `container_set.call(obj, index, container)`: Returns `container.__setitem__(index, obj)` and the `container`

- `container_del.call(index, container)`: Calls `container.__delitem__(index)` and returns the `container`

## `%lib%/stack.py`
Contains the module `stack`, which provides utilities to manipulate the stacks of the interpreter in weird ways.

- `stack_cur.call()`: Returns a reference to the current stack. Things can get weird... :)

- `stack_get.call(name)`: Returns a reference to the stack with that name. All changes to that stack will be reflected in the stack returned and vice versa. 

- `stack_switch.call(name)`: Switches the current stack to a stack with that `name`. Creates an empty stack if the name does not exist. Essentially the same thing as the builtin instruction `Let's take it to the {name}!`, but it can take any hashable object as the `name` and allows the creation of stacks with names determined by a variable.

- `stack_del.call(name)`: Deletes a stack with a given `name`. Once again, `name` can be any hashable object. Raises an `IndexError` if a stack named `name` does not exist. Trying to reference a deleted stack will raise an 	`IndexError`.