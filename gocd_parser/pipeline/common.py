class History(object):
	'''Methods common to objects reading from the history_page parser go
	here. This is pipeline history.'''

	def set_scalars(self):
		'''Find all scalars in our data, and set them as object
		attributes.'''

		for key, value in self.data.items():
			if type(value) == type([]):
				continue
			if type(value) == type({}):
				continue

			setattr(self, key, value)
