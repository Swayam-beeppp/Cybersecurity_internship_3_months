import cv2
import numpy as np

# Load the images
img1 = cv2.imread('image1.jpg', cv2.IMREAD_GRAYSCALE)  # queryImage
img2 = cv2.imread('image2.jpg', cv2.IMREAD_GRAYSCALE)  # trainImage

# Initiate ORB detector
orb = cv2.ORB_create(nfeatures=2000)

# Find keypoints and descriptors with ORB
kp1, des1 = orb.detectAndCompute(img1, None)
kp2, des2 = orb.detectAndCompute(img2, None)

# Create BFMatcher object
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Match descriptors
matches = bf.match(des1, des2)

# Sort them by distance
matches = sorted(matches, key=lambda x: x.distance)

# Draw top N matches
good_matches = matches[:50]

# Extract location of good matches
src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

# Compute homography
M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

# Warp image1 to image2’s perspective
h, w = img1.shape
pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
dst = cv2.perspectiveTransform(pts, M)

img2_color = cv2.imread('image2.jpg')
result = cv2.polylines(img2_color, [np.int32(dst)], True, (0,255,0), 3, cv2.LINE_AA)

# Show result
cv2.imshow('Homography Detection', result)
cv2.waitKey(0)
cv2.destroyAllWindows()
