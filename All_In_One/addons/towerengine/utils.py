

def bound_box_minmax(bound_box):
	min_v = [bound_box[0][0], bound_box[0][1], bound_box[0][2]]
	max_v = [bound_box[0][0], bound_box[0][1], bound_box[0][2]]

	for v in bound_box[:]:
		for i in range(0, 3):
			min_v[i] = min([min_v[i], v[i]])
			max_v[i] = max([max_v[i], v[i]])

	return [min_v, max_v]

