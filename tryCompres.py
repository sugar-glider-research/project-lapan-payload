import numpy as np

def compress(inputArray):
	height = inputArray.shape[0]
	width = inputArray.shape[1]

	#normalize data
	normArray = np.zeros((height,width), dtype=np.int16)
	for y in range (0,height):
		for x in range (0,width):
			normArray[y,x] = inputArray[y,x] - 128

	#normalize size (divisible by 8)
	subCountY = 0
	subCountX = 0
	subSize = 8
	if height % subSize == 0:
		subCountY = height/subSize
	else:
		subCountY = (height/subSize)+1
	if width % subSize == 0:
		subCountX = width/subSize
	else:
		subCountX = (width/subSize)+1

	sizedArray = np.zeros(((subCountY*subSize),(subCountX*subSize)), dtype=np.int16)
	for y in range (0,height):
		for x in range (0,width):
			sizedArray[y,x] = normArray[y,x]

	#calculate DCT matrix
	DCTArray = np.zeros(((subCountY*subSize),(subCountX*subSize)), dtype=np.float)
	coefInit = 1.0/(np.sqrt(2*subSize))
	coefY = 0.0
	coefX = 0.0
	coefZero = 1.0/(np.sqrt(2))
	coefNonZero = 1.0
	tempCosY = 0.0
	tempCosX = 0.0
	tempSigma = 0.0
	for y in range (0,subCountY):
		for x in range (0,subCountX):
			for v in range (0,subSize):
				for u in range (0,subSize):
					if v == 0:
						coefY = coefZero
					else:
						coefY = coefNonZero
					if u == 0:
						coefX = coefZero
					else:
						coefX = coefNonZero
					for j in range (0,subSize):
						for i in range (0,subSize):
							tempCosY = np.cos((((2.0*j)+1.0)*3.14*v)/(2.0*subSize))
							tempCosX = np.cos((((2.0*i)+1.0)*3.14*u)/(2.0*subSize))
							tempSigma = tempSigma + (sizedArray[((y*subSize)+j),((x*subSize)+i)]*tempCosY*tempCosX)
					DCTArray[((y*subSize)+v),(x*subSize)+u] = tempSigma * coefY * coefX * coefInit
					tempSigma = 0.0

	#quantized an DCT array
	#standard ISO JPEG array
	standardArray = np.array([[16,11,10,16,24,40,51,61],
			       [12,12,14,19,26,58,60,55],
			       [14,13,16,24,40,57,69,56],
			       [14,17,22,29,51,87,80,62],
			       [18,22,37,56,68,109,103,77],
			       [24,35,55,64,81,104,113,92],
			       [49,64,78,87,103,121,120,101],
			       [72,92,95,98,112,100,103,99]], dtype=np.int16)
	quantArray = np.zeros(((subCountY*subSize),(subCountX*subSize)), dtype=np.int16)
	for y in range (0,subCountY):
		for x in range (0,subCountX):
			quantArray[(y*subSize):((y+1)*subSize),(x*subSize):((x+1)*subSize)] = np.round(np.divide(DCTArray[(y*subSize):((y+1)*subSize),(x*subSize):((x+1)*subSize)],standardArray))

	#vectorize array
	vectorArray = np.zeros(((subCountY*subCountX),np.power(subSize,2)), dtype=np.int16)
	outIndex = 0
	for y in range (0,subCountY):
		for x in range (0,subCountX):
			for level in range (0,subSize):
				if level % 2 == 0:
					for elemen in range (0,(level+1)):
						vectorArray[(y*subCountX)+x,outIndex] = quantArray[(y*subSize)+(level-elemen),(x*subSize)+elemen]
						outIndex = outIndex + 1
				elif level % 2 == 1:
					for elemen in range (0,(level+1)):
						vectorArray[(y*subCountX)+x,outIndex] = quantArray[(y*subSize)+elemen,(x*subSize)+(level-elemen)]
						outIndex = outIndex + 1
			for level in range (0,(subSize-1)):
				if level % 2 == 0:
					for elemen in range (0,(subSize-(level+1))):
						vectorArray[(y*subCountX)+x,outIndex] = quantArray[(y*subSize)+(subSize-elemen-1),(x*subSize)+(elemen+1+level)]
						outIndex = outIndex + 1
				elif level % 2 == 1:
					for elemen in range (0,(subSize-(level+1))):
						vectorArray[(y*subCountX)+x,outIndex] = quantArray[(y*subSize)+(elemen+1+level),(x*subSize)+(subSize-elemen-1)]
						outIndex = outIndex + 1
			outIndex = 0

	#RLE on AC component
	#DPCM on DC component
	encodeArray = np.zeros(((subCountY*subCountX),np.power(subSize,2)), dtype=np.int16)
	DCBefore = 0
	for y in range (0,(subCountY*subCountX)):
		countZero = 0
		countState = 0
		index = 1
		encodeArray[y,0] = vectorArray[y,0] - DCBefore
		DCBefore = vectorArray[y,0]
		for x in range (1,(np.power(subSize,2))):
			if countState == 0:
				if vectorArray[y,x] == 0:
					countZero = 1
					countState = 1        
				encodeArray[y,index] = vectorArray[y,x]
				index = index + 1
			elif countState == 1:
				if vectorArray[y,x] == 0:
					countZero = countZero + 1
				else:
					encodeArray[y,index] = countZero
					index = index + 1
					encodeArray[y,index] = vectorArray[y,x]
					index = index + 1
					countState = 0
				if x == (np.power(subSize,2))-1:
					encodeArray[y,index] = countZero
	
	file = open('output.txt', 'w')
       	for y in range (0,height):
                print inputArray[y]
		file.write(str(inputArray[y]))
		file.write(' ')
	file.write('-------------------------')
        print DCTArray[0]
	file.write(str(DCTArray[0]))
	file.close()
