import csv, datetime,os, sys, math, time
import matplotlib.pyplot as plt
import numpy as np


# Project a vector x into n-1 dimensional space
def project(x):
	cond = 0
	w = np.zeros(len(x))
	print("X: "+str(x))
	for r in x:
		cond += math.pow(r, 2)
	w[0] = math.sqrt(cond)
	w = np.transpose(np.matrix(w))

	v = w - x
	P = (v * np.transpose(v)) / (np.transpose(v) * v)
	return np.identity(len(P)) - 2 * P

# given a 2xn matrix A and a 1xn matrix b, will solve for a root mean
# squares solution using QR factorization. Returns the x matrix.
def householder(A,b):

	# First column = x
	x=A[:,0:1]

	H1 = project(x)
	H1A = H1*A

	# Value for H2 - second column excluding the first value to avoid messing it up
	x = H1A[1:,1:]
	H2_int = project(x)

	# Put in the correct form - first row and column as ID matrix, again to avoid messing up first value.
	H2 = np.matrix(np.zeros(len(np.array(x))))
	H2 = np.concatenate((H2, H2_int))
	id = np.zeros(len(np.array(x))+1)
	id[0] = 1
	H2 = np.concatenate((np.transpose(np.matrix(id)), H2), axis=1)

	R = H2*H1*A

	Q = H1*H2
	R = R[:2, :2]
	d = (np.transpose(Q)*b)
	d = d[:2]

	# Solve Rx = d where R is upper nxn of R, and d is upper n of Q^T*b
	x = np.linalg.inv(R)*d
	return x

'''
Given x, y data use householder reflectors to generate a RMS line
'''
def extrapolate(x,y):
	a1 = [1. for i in range(0, len(y))]
	if len(y) != len(x):
		print("ERROR: x and y arrays must be the same length.")
		return -1
	aT = np.matrix([x, a1])
	a = np.transpose(aT)
	b = np.transpose(np.matrix(y))
	estb = householder(a, b)
	return estb

# Read the given csv file in and return a 2 element tuple containing the times and the highest value for that day.

def read_csv(filename):
	time = []
	high = []
	# Columns of file: Date,open,high,low,close,volume,market cap
	with open(filename) as file:
		reader = csv.reader(file)
		for row in reader:
			time.append(row[0])
			high.append(row[2])

	return (time[1:], high[1:])
'''
Author: Maxine Hartnett
Date: 8/25/2017

If called with no arguments, this program will plot all csv files against each other in folder_name.
If given filenames as arguments upon the call, those will be the only ones plotted.
'''

def main():
	folder_name = "/home/user/Dropbox/personal_projects/crypto/cryptocurrencypricehistory/"
	# The number of elements to use for RMS extrapolation
	to_extr = 5 

	files = os.listdir(folder_name)
	if len(sys.argv) > 1:
		files = sys.argv[1:]

	for file in files:
		print("file: "+file)
		test_data=read_csv(folder_name+file)
		max_data = test_data[1]
		
		#int_day.append(time[4:6])
		datetimes = [datetime.datetime.strptime(t, "%b %d, %Y") for t in test_data[0]]
		last_ind = 0
		today = datetime.datetime.today()
		for dt in datetimes:
			tdelt = today - dt
			
			if tdelt.days > 730:
				last_ind += 1
		#print("Datetimes length: "+str(len(datetimes)))
		datetimes = datetimes[last_ind:]
		#print("Datetimes length post: "+str(len(datetimes)))
		max_data = max_data[last_ind:]
		#print("max data post: "+str(len(max_data)))

		#print(str(datetimes[0].year))
		ending = file.find( "_price.csv")
		label = file[:ending]
		#print(label)
		# Move this check up
		if label != "bitcoin":
			plt.plot(datetimes, max_data, label=label)
		# Add legend
		unix_time = []

		'''
		TODO:
		Fix the time so that it works wrt days not seconds
		'''

		for i in range(len(datetimes)-to_extr, len(datetimes)):
			unix_time.append(float(time.mktime((datetimes[i]).timetuple())))

		max_data = [float(i) for i in max_data]
		print("unix time: "+str(unix_time))
		print("x data: "+str(max_data[len(max_data)-to_extr:]))
		ext=extrapolate(max_data[len(max_data)-to_extr:], unix_time)
		print("Ext: "+str(ext))
		formula = str(np.asscalar(ext[0]))+"*x+"+str(np.asscalar(ext[1]))
		print("Formula: "+formula)


	plt.title("Comparison of Different Cryptocurrencies")
	plt.xlabel("Time")
	plt.ylabel("Highest Price on Given Day")
	plt.legend(loc="upper left")
	plt.show()


if __name__ == "__main__":
 main()