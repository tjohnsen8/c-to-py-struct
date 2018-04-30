'''
will read in a .h file, and create a namedtuple based on the 
types and names of the variables for binary parsing
'''

from struct import unpack
from collections import namedtuple

'''
have to create type strings for the struct library 
to unpack binary data from a data stream (file, socket, etc)
'''

# all types will need to be defined here
ctype_to_struct = {
	'uint16_t': 'H',
	'uint8_t': 'B', 
	'int16_t': 'h', 
	'int8_t': 'b', 
	'int32_t': 'l',
	'uint32_t': 'L'
	}


def get_type_from_line(line):
	type_str = ''
	tuple_label = ''
	words = line.split()
	if len(words) >= 2:
		if words[0] in ctype_to_struct:
			# add the type to the type_str
			c_type = ctype_to_struct[words[0]]
			type_str += c_type
			if '[' in line:
				# get the number in between
				num = int(line[line.find("[")+1:line.find("]")])
				# don't include the [] in the label
				label_base = words[1][:words[1].find('[')]
				tuple_label = '{}0'.format(label_base)
				# add to the type_str, starting at 1 since we already added one
				for i in range(1, num):
					type_str += c_type
					tuple_label += ' {}{}'.format(label_base, i)
			else:
				tuple_label = words[1].replace(';', '')
		else:
			print('{} not defined, please add'.format(words[0]))
	return type_str, tuple_label


def get_struct_name(line):
	words = line.split()
	if len(words) > 1:
		return words[1].replace(';', '')


def read_header_file(filename):
	struct_list = []
	with open(filename, 'r') as f:
		lines = f.readlines()
		struct_started = False
		comment_started = False
		type_str = ''
		labels = ''
		for line in lines:
			# look for the start of the def
			if len(line.split()) < 2:
				pass
			elif '//' in line.split()[0]:
				pass
			elif not comment_started and '/*' in line:
				comment_started = True
				pass
			elif '*/' in line:
				comment_started = False
				pass
			elif not struct_started:
				if 'struct' in line:
					struct_started = True
			elif '}' in line:
				struct_started = False
				struct_name = get_struct_name(line)
				py_struct = PyStruct(struct_name, type_str, labels)
				struct_list.append(py_struct)
				type_str = ''
				labels = ''
			else:
				# line in the struct
				line_type, line_label = get_type_from_line(line)
				type_str += line_type
				if line_label != '':
					labels += ' {}'.format(line_label)
	return struct_list


class PyStruct:
	def __init__(self, name, types, labels):
		# create the tuple, accessible by self.'<whatever is in name>'
		self.tuple = namedtuple(name, labels)
		self.types = types
		self.name = name
		self.label_list = labels.split()

if __name__ == '__main__':
	struct_list = (read_header_file('test.h'))
	for py_struct in struct_list:
		print(py_struct.label_list)
