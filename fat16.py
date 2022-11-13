import struct
import pprint

class Fat16():
    # Read image data
    def __init__(self):
        self.data = []
        self.fat = []
        self.root_dir = {}
        self.cluster_area = {}
        try: 
            with open('test.img', 'rb') as image:
                byte = image.read(1)
                self.data.append(byte)
                while byte:
                    byte = image.read(1)
                    self.data.append(byte)
        except IOError:
            print('IO error')
        
        self.read_mbr()
        self.read_fat()
        self.read_root_directory()
        self.read_cluster_area()

    def read_mbr(self):
        self.reserved_sector = struct.unpack('<H', b''.join(self.data[14:16]))[0]
        self.sector_size = struct.unpack('<H', b''.join(self.data[11:13]))[0]
        self.cluster_size_in_sector = struct.unpack('B', self.data[13])[0]
        self.fat_size = struct.unpack('<H', b''.join(self.data[22:24]))[0]
        self.fat_copies = struct.unpack('B', self.data[16])[0]
        self.root_dir_entries = struct.unpack('<H', b''.join(self.data[17:19]))[0]
    
    def get_fat_start(self):
        return self.reserved_sector * self.sector_size

    def get_root_dir_start(self):
        return self.reserved_sector * self.sector_size + self.fat_copies * self.fat_size * self.sector_size
    
    def cluster_area_start(self):
        return self.get_root_dir_start() + self.root_dir_entries * 32

    def read_fat(self):
        for offset in range(self.get_fat_start(), self.get_fat_start() + self.sector_size, 2):
            entry = struct.unpack('<H', b''.join(self.data[offset:offset+2]))[0]
            self.fat.append(hex(entry))

    def read_root_directory(self):
        for i in range(self.get_root_dir_start(), self.get_root_dir_start() + 32 * self.root_dir_entries, 32):
            ascii_tuple = struct.unpack('BBBBBBBBBBB', b''.join(self.data[i:i+11]))
            if (ascii_tuple == (0,0,0,0,0,0,0,0,0,0,0)):
                break

            self.root_dir[hex(i)] = {
                'entry_name': ''.join(chr(ascii) for ascii in ascii_tuple).strip(),
                'attributes': hex(struct.unpack('B', self.data[i+12])[0]),
                'start_cluster': struct.unpack('<H', b''.join(self.data[i+26:i+28]))[0],
                'file_size': struct.unpack('<I', b''.join(self.data[i+28:i+32]))[0]
            }       
    
    def read_cluster_area(self):
        for value in self.root_dir.values():
            if (value['start_cluster'] == 0):
                continue
            cluster_start = self.cluster_area_start() + (value['start_cluster'] - 2) * (self.cluster_size_in_sector * self.sector_size)
            for offset in range(cluster_start, cluster_start + (self.cluster_size_in_sector * self.sector_size), 32):
                name_tuple = struct.unpack('BBBBBBBB', b''.join(self.data[offset:offset+8]))
                if (name_tuple == (0,0,0,0,0,0,0,0)):
                    print('\n')
                    break;
                ext_tuple = struct.unpack('BBB', b''.join(self.data[offset+8:offset+11]))

                self.cluster_area[hex(offset)] = {
                    'file_name': ''.join(chr(ascii) for ascii in name_tuple).strip(),
                    'file_ext': ''.join(chr(ascii) for ascii in ext_tuple),
                    'attributes': hex(struct.unpack('B', self.data[offset+12])[0]),
                    'start_cluster': struct.unpack('<H', b''.join(self.data[offset+26:offset+28]))[0],
                    'file_size': struct.unpack('<I', b''.join(self.data[offset+28:offset+32]))[0]
                }
    
    def print(self):
        print('BOOT SECTOR:')
        print('reserved_sector: ' + str(self.reserved_sector))
        print('sector_size: ' + str(self.sector_size))
        print('cluster_size_in_sector: ' + str(self.cluster_size_in_sector))
        print('fat_size: ' + str(self.fat_size))
        print('fat_copies: ' + str(self.fat_copies))
        print('root_dir_entries: ' + str(self.root_dir_entries))
        print('ROOT DIRECTORY:')
        pprint.pprint(fat16.root_dir, indent = 4, sort_dicts = False)
        print('CLUSTER:')
        pprint.pprint(fat16.cluster_area, indent = 4, sort_dicts = False)

      
fat16 = Fat16()
fat16.print()
