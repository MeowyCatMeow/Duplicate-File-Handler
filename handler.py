import sys
import os
import pathlib
import hashlib


class DuplicateFileHandler:

    def __init__(self):
        self.file_dict = {}
        self._format = ''
        self.option = ''
        self.paths = []
        self.sizes = []
        self.hashes = []
        self.sorted_file_dict = {}  # {path x :{ size: y , hash: z }}
        self.dup_dict = {}  # {size: {'hash': ['path1, 'path2']
        self.for_deleting = {}  # {number : path}

    def get_dict(self):
        if len(sys.argv) < 2:
            print('Directory is not specified')
            sys.exit()
        else:
            for (root, dirs, files) in os.walk(sys.argv[1], topdown=True):
                for name in files:
                    path = os.path.join(root, name)
                    size = os.path.getsize(path)
                    with open(path, 'r') as f:
                        _bytes = f.read()
                        _hash = hashlib.md5(_bytes.encode()).hexdigest()
                        self.paths.append(path)
                        self.sizes.append(size)
                        self.hashes.append(_hash)
            for p, s, h in zip(self.paths, self.sizes, self.hashes):
                self.file_dict[p] = {'size': s, 'hash': h}
            self._format = input('Enter file format:')
            if self._format != '':
                for k in list(self.file_dict):
                    if not k.endswith(self._format):
                        del self.file_dict[k]

    def get_value(self, key):
        return self.file_dict[key]['size']

    def sort_dict(self, _reverse=True):
        sorted_keys = sorted(self.file_dict.keys(), key=self.get_value, reverse=_reverse)
        self.sorted_file_dict = {key: self.file_dict[key] for key in sorted_keys}
        self.check_dup()

    def check_dup(self):
        for key in self.sorted_file_dict:
            path = self.sorted_file_dict[key]
            size = self.sorted_file_dict[key]['size']
            _hash = self.sorted_file_dict[key]['hash']
            if size not in self.dup_dict.keys():
                self.dup_dict[size] = {}
            if _hash not in self.dup_dict[size]:
                self.dup_dict[size][_hash] = []
            self.dup_dict[size][_hash].append(key)
        for s in self.dup_dict:
            print(s, 'bytes')
            for h in self.dup_dict[s]:
                for p in self.dup_dict[s][h]:
                    print(p)
        while True:
            print('Check for duplicates?')
            choice = input().lower()
            if choice in ['yes', 'no']:
                if choice == 'yes':
                    i = 1
                    for _key in self.dup_dict:
                        printed_bytes = False
                        for _hash in self.dup_dict[_key]:
                            duplicates = self.dup_dict[_key][_hash]
                            if len(duplicates) == 1:
                                continue
                            if not printed_bytes:
                                print(_key, 'bytes')
                                printed_bytes = True
                            print('Hash:', _hash)
                            for _path in duplicates:
                                self.for_deleting[i] = _path
                                print(f'{i}.', _path)
                                i += 1
                break
            else:
                print('Wrong option\n')

    def delete(self):
        while True:
            delete = input('Delete files?\n')
            if delete not in ("yes", "no"):
                print("Wrong option\n")
            else:
                break
        while True:
            delete = delete == 'yes'
            if delete:
                try:
                    numbers = input('Enter file numbers to delete:').split()
                    numbers = [int(x) for x in numbers]
                    check = all(item in self.for_deleting.keys() for item in numbers)
                    if not check or len(numbers) == 0:
                        raise ValueError('invalid number')
                except ValueError:
                    print('Wrong format')
                    continue
                try:
                    for k, v in self.for_deleting.items():
                        if k in numbers:
                            print(k, v)
                            print(os.path.getsize(v))
                            os.remove(v)
                except OSError as e:
                    print("Failed with:", e.strerror)
                self.deleted_size(numbers)
            else:
                sys.exit()

    def deleted_size(self, numbers):
        path = []
        for n in numbers:
            path.append(self.for_deleting[n])
        sizes = 0
        for p in path:
            sizes += self.sorted_file_dict[p]['size']
        print(f'\nTotal freed up space: {sizes} bytes')

    def operate(self):
        self.get_dict()
        print('''
Size sorting options:
1. Descending
2. Ascending
                    ''')
        while True:
            print('Enter a sorting option:')
            self.option = input()
            if self.option in ['1', '2']:
                print()
                self.option = int(self.option)
                if self.option == 1:
                    self.sort_dict(_reverse=True)
                elif self.option == 2:
                    self.sort_dict(_reverse=False)
                break
            else:
                print('Wrong option\n')
        self.delete()


handler = DuplicateFileHandler()
handler.operate()
