# This file have just define 1 class:Database and 1 helper function for this class.

# Helper function to split line content into a list
def split_ctn(ctn: str):
    return ctn.rstrip('\r\n').split(', ')

class Database:
    def __init__(self, path) -> None:
        self.path = path
        # Read file and initialize header and sequence number
        with open(self.path, 'rb') as file_db:
            self.header = split_ctn(file_db.readline().decode())  # Get header
            file_db.seek(-3, 2)                                   # Move to the third last character (sequence number)
            self.seq = int(file_db.read(3))                       # Read current sequence number

    # Search function, match rows based on given keywords
    def search(self, count = 1, **search_args):
        search_result = []              # Store matching results
        conditions = []                 # Store matching indices and values
        for key, value in search_args.items():
            i = self.header.index(key)  # Get index of the keyword in the header
            conditions.append((i, value))

        with open(self.path, 'rt') as txt:
            txt.readline()  # Skip header
            while count != 0:
                content = txt.readline()                       # Read file line by line
                if content == '' or content[0] == 's':         # Check if end of file or sequence line
                    break
                value_list = split_ctn(content)                # Parse line data
                for i, val in conditions:
                    if value_list[i] != val:
                        break
                else:
                    count -= 1
                    search_result.append(dict(zip(self.header, value_list)))
        return search_result                                   # Return matching rows

    # Search based on detector function
    def search_if(self, detect_fn: object, count = 1, *args, **kwargs):
        search_result = []

        with open(self.path, 'rt') as txt:
            txt.readline()  # Skip header
            while count != 0:
                content = txt.readline()                         # Read file line by line
                if content == '' or content[0] == 's':           # Check if end of file or sequence line
                    break
                value_list = split_ctn(content)
                value_comp = dict(zip(self.header, value_list))  # Create line data dictionary
                if detect_fn(value_comp, *args, **kwargs):       # Match using detector function
                    count -= 1
                    search_result.append(value_comp)
        return search_result                                     # Return matching rows

    # Insert new row
    def insert(self, **insert_args):
        self.seq += 1
        new_seq = str(self.seq).zfill(3)                                # Update sequence number
        value_list = [insert_args.get(key, '') for key in self.header]  # Create row data list
        value_list[0] = new_seq                                         # Set sequence number
        insert_ctn = ', '.join(value_list) + '\ns' + new_seq            # Concatenate row data and sequence number

        with open(self.path, 'r+b') as txt:
            txt.seek(-4, 2)                 # Move to the end of the file
            txt.truncate()                  # Truncate last sequence number
            txt.write(insert_ctn.encode())  # Write new data
        return new_seq

    # Update function, allows editing or deleting a row
    def update(self, modify_dict: dict = {}, count = 1, **search_args):
        if count == 0:
            return
        conditions = []                 # Store matching indices and values
        for key, value in search_args.items():
            i = self.header.index(key)  # Get index of the keyword in the header
            conditions.append((i, value))

        with open(self.path, 'r') as txt:
            data_list = txt.readlines()  # Read all lines

        for idx, content in enumerate(data_list):
            if content == '' or content[0] == 's':  # Skip empty or sequence lines
                continue
            value_list = split_ctn(content)         # Parse row data
            for i, val in conditions:
                if value_list[i] != val:
                    break
            else:
                count -= 1
                if modify_dict is None:             # If None is passed, delete the row
                    data_list[idx] = ''
                else:  # Modify matching row
                    for key, value in modify_dict.items():
                        i = self.header.index(key)  # Get index of the keyword in the header
                        value_list[i] = value
                    data_list[idx] = ', '.join(value_list) + '\n'
                if count == 0:
                    break

        with open(self.path, 'w') as txt:
            txt.write(''.join(data_list))  # Write modified data back to the file

    # Update based on modification function
    def update_if(self, modify_fn: object, count = 1, *args, **kwargs):
        if count == 0:
            return
        with open(self.path, 'r') as txt:
            data_list = txt.readlines()  # Read all lines

        for idx, content in enumerate(data_list):
            if content == '' or content[0] == 's':                 # Skip empty or sequence lines
                continue
            value_list = split_ctn(content)                        # Parse row data
            value_comp = dict(zip(self.header, value_list))        # Convert to dictionary
            updated_comp = modify_fn(value_comp, *args, **kwargs)  # Call modification function
            if updated_comp is False:                              # If no match, continue
                continue
            count -= 1
            # If None is returned, delete the row; otherwise update the row content
            data_list[idx] = '' if (updated_comp is None) else (', '.join(updated_comp.values()) + '\n')
            if count == 0:
                break

        with open(self.path, 'w') as txt:
            txt.write(''.join(data_list))  # Write modified data back to the file

if 0:
    v = 'undefineded'
    # Sample test code
    file = Database('./test.txt')

    # Custom detector function for matching name and password
    def custom_detect(value_comp:dict, d_name, d_passw):
        return (value_comp['name'] == d_name and value_comp['password'] == d_passw)

    # Test search functionality
    file.search(name='Kuek', password='2882')
    file.search_if(custom_detect, 1, 'Kuek', '2882')

    # Insert new row
    file.insert(name='Rachael', password='0802')

    # Custom modification function to update the name field
    def custom_modify(value_comp: dict, old_name, new_name):
        if value_comp['name'] != old_name:
            return False
        value_comp['name'] = new_name  # Update name
        return value_comp

    # Test update functionality
    file.update({'name':'KuekZY'}, name='Kuek')  # Delete matching row
    file.update_if(custom_modify, 1, 'Kuek', 'KuekZY')  # Update name field
    print(v)
