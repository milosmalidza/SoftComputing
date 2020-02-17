import cv2
from utility import Utility
from tracking_frame import TrackingFrame
import math

def getAbsoluteFirstFrame():
    cap = cv2.VideoCapture(Utility.directory + 'video1.mp4')
    cap.set(1, Utility.absolute_first_frame_index)
    ret, img = cap.read()
    cap.release()
    return ret, img

def getFilesWithResults():
    lines = None
    with open(Utility.directory + 'res.txt') as f:
        lines = f.readlines()

    results = {}
    for i, line in enumerate(lines):
        if i == 0: continue
        token = line.split(',')
        results[token[0]] = int(token[1].rstrip())

    return results

def main():
    sqx, sqy, sqw, sqh = Utility.square_rect
    ret, absoluteFirstFrame = getAbsoluteFirstFrame()
    realResults = getFilesWithResults()
    predictedResults = {}
    for key, value in realResults.items():
        cap = cv2.VideoCapture(Utility.directory + key)

        ret, firstFrame = cap.read()
        ret, secondFrame = cap.read()

        acquired = []
        potential = []

        visited = []
        predictedPeople = 0
        while cap.isOpened():
            frame = None
            try:
                frame = cv2.absdiff(absoluteFirstFrame, secondFrame)
                fr = cv2.absdiff(firstFrame, secondFrame)
                frame = cv2.addWeighted(frame, 0.3, fr, 2.9, -5)
            except:
                break

            thresh = Utility.adaptiveTreshold(frame)
            thresh = cv2.dilate(thresh, Utility.getVerticalKernel(), iterations=3)

            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            filtered_contours = []
            filtered_positions = []

            for c in contours:
                x, y, w, h = cv2.boundingRect(c)

                if not Utility.contoursMeetsParameters(w, h):
                    continue

                #cv2.rectangle(firstFrame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                filtered_contours.append((x, y, w, h))
                filtered_positions.append((x, y))

            for acq in acquired[:]:
                position = acq.determineClosestPosition(filtered_positions, acquired)
                if position is not None:
                    x, y, w, h = Utility.getContourAtPosition(filtered_contours, position)
                    acq.updateStats(position, w, h)
                    acq.incrementLostTrackTick()

                    if not acq.counted and Utility.checkRectCollision(
                            (acq.position[0], acq.position[1], acq.width, acq.height), (sqx, sqy, sqx + sqw, sqy + sqh))\
                            and acq.lostTrackTick > 14:
                        acq.counted = True
                        visited.append(acq)
                        predictedPeople += Utility.getPredictedPeople(acq.width, acq.height)

                else:
                    acq.updatePosition()
                    acq.decrementLostTrackTick()
                    if acq.lostTrackTick == 0:
                        acquired.remove(acq)

                cv2.rectangle(firstFrame, (int(acq.position[0]), int(acq.position[1])),
                              (int(acq.position[0]) + int(acq.width), int(acq.position[1]) + int(acq.height)),
                              (0, 0, 255), 1)

            for pot in potential[:]:
                position = pot.determineClosestPosition(filtered_positions)
                if position is not None:
                    x, y, w, h = Utility.getContourAtPosition(filtered_contours, position)
                    pot.updateStats(position, w, h)
                    pot.decrementPotential()
                    if Utility.checkIfPotentialIsAcquired(pot, acquired):
                        potential.remove(pot)
                        continue

                    if pot.potentialTick == 0:
                        acquired.append(pot)
                        potential.remove(pot)
                else:
                    pot.updatePosition()
                    pot.decrementPotentialNot()
                    if pot.potentialNotTick == 0:
                        potential.remove(pot)

                #cv2.rectangle(firstFrame, (int(pot.position[0]), int(pot.position[1])), (int(pot.position[0]) + int(pot.width), int(pot.position[1]) + int(pot.height)), (255, 255, 0), 1)

            for fc in filtered_contours:
                x, y, w, h = fc
                if Utility.checkIfContourIsFree(fc, potential, acquired):
                    potential.append(TrackingFrame((x, y), w, h))

            cv2.putText(firstFrame, "Acquired: " + str(len(acquired)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1)
            cv2.putText(firstFrame, "Potential: " + str(len(potential)), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1)
            cv2.putText(firstFrame, "Filtered Cs: " + str(len(filtered_contours)), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1)
            cv2.putText(firstFrame, "Contours: " + str(len(contours)), (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1)
            cv2.putText(firstFrame, "Counted: " + str(predictedPeople), (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 200, 0), 1)
            cv2.rectangle(firstFrame, (sqx, sqy), (sqw, sqh), (255, 255, 0), 2)
            # cv2.rectangle(firstFrame, (0, 0), (30, 40), (255, 255, 255), 1)
            cv2.imshow('frame', firstFrame)
            cv2.imshow('thresh', thresh)

            firstFrame = secondFrame
            ret, secondFrame = cap.read()

            if cv2.waitKey(Utility.video_speed) & 0xFF == ord('q'):
                break

        cap.release()
        predictedResults[key] = predictedPeople
        print(key + ": " + str(predictedPeople))

    cv2.destroyAllWindows()

    sum = 0
    for key, value in predictedResults.items():
        sum += abs(predictedResults[key] - realResults[key])

    print("MAE: " + str(sum / float(len(predictedResults))))

    print("Finished")


if __name__ == '__main__':
    main()




