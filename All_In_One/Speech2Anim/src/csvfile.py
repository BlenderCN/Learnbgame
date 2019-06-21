import collections
import csv

class CSVFile:
	def __init__(self, colNames=[]):
		self.setHeader(colNames)

	def setHeader(self, header):
		self.header = header
		self.content = collections.OrderedDict()
		self.nrows = 0
		for colName in header:
			self.content[colName] = []

	def getHeader(self):
		return self.header

	def get_row_count(self):
		return self.nrows

	def getRows(self):
		rows = []
		for i in range(0, self.nrows):
			row = []
			
			for j, col in enumerate(self.header):
				row.append(self.content[col][i])

			rows.append(row)

		return rows

	def addRow(self, values):
		if len(values) != len(self.header):
			print("Incorrect column count ({}, expected {})".format(
					len(values), len(self.header)))
			return False

		for i, col in enumerate(self.header):
			self.content[col].append(values[i]) 

		self.nrows += 1

	def saveAs(self, outputName):
		o = open(outputName+".csv", "w")
		o.write(str(self))

	def from_file(self, file_name):
		with open(file_name) as f:
			csv_file = csv.reader(f, delimiter=';')
			self.setHeader(next(csv_file))
			for row in csv_file:
				self.addRow(row)

	def tidy(self):
		newHeader = []
		for h in self.header:
			newHeader.append(h.strip())
		self.header = newHeader

		newContent = collections.OrderedDict()
		for key, row in self.content.items():
			newkey = key.strip()
			newContent[newkey] = []
			for value in row:
				newContent[newkey].append(str(value).strip())

		self.content = newContent



	def from_dict(self, d):
		self.content = d
		self.nrows = len(d[list(d)[0]])

	def to_dict(self):
		return self.content			

	def __str__(self):
		result = ""
		for key in self.content:
			result += key+";"

		result = result[:-1]
		result += "\n"

		for i in range(0,self.nrows):
			for key, value in self.content.items():
				result += str(value[i]) + ";"
			result = result[:-1]
			result += "\n"

		return result