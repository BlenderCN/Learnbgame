from geometry import Point2D
from enum import Enum
import config
class BodyPartType(Enum):
	NOSE = 0
	NECK = 1
	RSHOULDER = 2
	RELBOW = 3
	RWRIST = 4
	LSHOULDER = 5
	LELBOW = 6
	LWRIST = 7
	RHIP = 8
	RKNEE = 9
	RANKLE = 10
	LHIP = 11
	LKNEE = 12
	LANKLE = 13
	REYE = 14
	LEYE = 15
	REAR = 16
	LEAR = 17
	BKG = 18

class BodyPart:
	""" The position of a body part with a confidence score """
	def __init__(self, bodyPart, pos, score):
		self.bodyPart = bodyPart
		self.pos = pos
		self.score = score

	def __str__(self):
		return "{} {} score:{}".format(self.bodyPart, self.pos, self.score)

class Pose:
	""" A group of BodyParts """
	def __init__(self):
		self.parts = {}
		for part in BodyPartType:
			self.parts[part] = BodyPart(part, Point2D(0,0), 0)

	def fromData(self, personData):
		pc = 0
		for i in range(0, len(personData["pose_keypoints"]), 3):
			part = BodyPartType(pc)
			pc += 1
			pos = Point2D(	personData["pose_keypoints"][i], 
							personData["pose_keypoints"][i+1])
			score = personData["pose_keypoints"][i+2]
			self.parts[part] = BodyPart(part, pos, score)

	def getPart(self, part):
		return self.parts[part]

	def __str__(self):
		result = ""
		for part in self.parts:
			result += "{}\n".format(self.parts[part])
		return result

class PoseKeypoint:
	""" A keyframe with its pose """
	def __init__(self, frame, pose):
		self.frame = frame
		self.pose = pose
	def __str__(self):
		return "(PoseKeypoint Frame: {}\n{})".format(self.frame, self.pose) 

def getPersonArea(personData):
	#Did we find a keyframe with a score > SCORE_THRESHOLD
	validKeypointFound = False
	for i in range(0, len(personData["pose_keypoints"]), 3):
		currX = personData["pose_keypoints"][i]
		currY = personData["pose_keypoints"][i+1]
		score = personData["pose_keypoints"][i+2]

		if score < config.SCORE_THRESHOLD:
			continue

		if validKeypointFound:
			minX = min(currX, minX)
			maxX = max(currX, maxX)
			minY = min(currY, minY)
			maxY = max(currY, maxY)
		else:
			validKeypointFound = True
			minX = currX
			maxX = minX
			minY = currY
			maxY = minY

	if not validKeypointFound:
		return 0
	else:
		return (maxY-minY) * (maxX-minX)

def getBiggestPersonIndex(keypointData):
	index = 0
	biggestArea = getPersonArea(keypointData["people"][0])
	for i, person in enumerate(keypointData["people"]):
		personArea = getPersonArea(person)
		if personArea > biggestArea:
			index = i
			biggestArea = personArea

	return index