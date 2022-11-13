import struct

class Fat16():
    # Read image data
    def __init__(self):
        self.data = []
        self.root_dir = {}
        try: 
            with open('test.img', 'rb') as image:
                byte = image.read(1)
                self.data.append(byte)
                while byte:
                    byte = image.read(1)
                    self.data.append(byte)
        except IOError:
            print('IO error')

    def read_mbr(self):
        self.reserved_sector = struct.unpack('<H', b''.join(self.data[14:16]))[0]
        self.sector_size = struct.unpack('<H', b''.join(self.data[11:13]))[0]
        self.cluster_size_in_sector = struct.unpack('B', self.data[13])[0]
        self.fat_size = struct.unpack('<H', b''.join(self.data[22:24]))[0]
        self.fat_copies = struct.unpack('B', self.data[16])[0]
        self.root_dir_entries = struct.unpack('<H', b''.join(self.data[17:19]))[0]
        
        print('reserved_sector: ' + str(self.reserved_sector))
        print('sector_size: ' + str(self.sector_size))
        print('cluster_size_in_sector: ' + str(self.cluster_size_in_sector))
        print('fat_size: ' + str(self.fat_size))
        print('fat_copies: ' + str(self.fat_copies))
        print('root_dir_entries: ' + str(self.root_dir_entries))

    def get_root_dir_start(self):
        return self.reserved_sector * self.sector_size + self.fat_copies * self.fat_size * self.sector_size
    
    def cluster_area_start(self):
        return self.get_root_dir_start() + self.root_dir_entries * 32

    def read_root_directory(self):
        for i in range(self.get_root_dir_start(), self.get_root_dir_start() + 32 * 4, 32): # todo: 4 should be self.root_dir_entries
            ascii_array = struct.unpack('BBBBBBBBBBB', b''.join(self.data[i:i+11]))
            entry_name = ''.join(chr(ascii) for ascii in ascii_array)
            if (entry_name != ''):
                self.root_dir[hex(i)] = {
                    'entry_name': entry_name,
                    'attributes': struct.unpack('B', self.data[i+12])[0],
                    'start_cluster': struct.unpack('<H', b''.join(self.data[i+26:i+28]))[0],
                    'file_size': struct.unpack('<I', b''.join(self.data[i+28:i+32]))[0]
                }
    
    def read_cluster_area(self):
        for value in self.root_dir.values():
            cluster_start = self.cluster_area_start() + value['start_cluster'] * (self.cluster_size_in_sector * self.sector_size)
            for offset in range(cluster_start, cluster_start + (self.cluster_size_in_sector * self.sector_size), 32):
                ascii_tuple = struct.unpack('BBBBBBBBBBB', b''.join(self.data[offset:offset+11]))
                if (ascii_tuple == (0,0,0,0,0,0,0,0,0,0,0)):
                    print('\n')
                    break;
                file_name = ''.join(chr(ascii) for ascii in ascii_tuple)
                print('entry: {} -> {} '.format(value['entry_name'], file_name))

      
fat16 = Fat16()
fat16.read_mbr()
fat16.read_root_directory()
fat16.read_cluster_area()