import math

class TrackingFrame:

    maxDistance = 25

    def __init__(self, position=(0, 0), width=5, height=10):
        self.position = position
        self.lastPosition = position
        self.velocity = (0, 0)  # (x, y) velocity vector2d
        self.previousVelocities = []
        self.width = width
        self.height = height
        self.counted = False
        self.countId = 0
        self.potentialTick = 16
        self.potentialNotTick = 4
        self.lostTrackTick = 16

    def decrementPotential(self):
        if self.potentialTick > 0:
            self.potentialTick -= 1

    def decrementPotentialNot(self):
        if self.potentialNotTick > 0:
            self.potentialNotTick -= 1

    def decrementLostTrackTick(self):
        if self.lostTrackTick > 0:
            self.lostTrackTick -= 1

    def incrementLostTrackTick(self):
        if self.lostTrackTick < 16:
            self.lostTrackTick += 1

    def setPosition(self, position):
        self.lastPosition = self.position
        self.position = position
        self.velocity = (self.position[0] - self.lastPosition[0], self.position[1] - self.lastPosition[1])
        self.previousVelocities.append(self.velocity)
        if len(self.previousVelocities) > 20:
            self.previousVelocities.pop(0)

    def getAvgVelocity(self):
        x, y = (0, 0)
        for vel in self.previousVelocities:
            x += vel[0]
            y += vel[1]

        if len(self.previousVelocities) == 0:
            return 0, 0

        return x / len(self.previousVelocities), y / len(self.previousVelocities)

    def updateStats(self, position, width, height):
        self.setPosition(position)
        self.width += (width - self.width) / 5
        self.height += (height - self.height) / 5

    def determineClosestPosition(self, positions, acquired=None):
        position = None
        closest_distance = 999999

        if acquired is None:
            for pos in positions:
                distance = math.sqrt(math.pow(self.position[0] - pos[0], 2) + math.pow(self.position[1] - pos[1], 2))
                if distance > TrackingFrame.maxDistance:
                    continue
                if distance < closest_distance:
                    closest_distance = distance
                    position = pos

        else:
            for pos in positions:
                distance = math.sqrt(math.pow(self.position[0] - pos[0], 2) + math.pow(self.position[1] - pos[1], 2))
                if distance > TrackingFrame.maxDistance:
                    continue
                if distance < closest_distance:
                    if self.checkIfAcquired(pos, acquired):
                        continue

                    closest_distance = distance
                    position = pos

        return position

    def checkIfAcquired(self, position, acquired):
        for acq in acquired:
            if acq.position[0] == position[0] and acq.position[1] == position[1]:
                return True

        return False

    def updatePosition(self):
        x, y = self.position
        avg = self.getAvgVelocity()
        x += avg[0] * 0.7 + self.velocity[0] * 0.3
        y += avg[1] * 0.7 + self.velocity[1] * 0.3

        self.position = (x, y)


