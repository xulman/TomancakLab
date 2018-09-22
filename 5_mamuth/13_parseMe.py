#@String (label="timepoints") timePoints


def parseOutTimes(tps):
	out = []

	while len(tps) > 0:

		# find the next ',' or '-'
		ic = tps.find(',')
		ih = tps.find('-')

		#print "found , @ " + str(ic) + " and - @ " + str(ih)

		# -1 means 'not found'
		if ic == -1:
			# processing for sure the last term
			ic = len(tps)

		# make sure if hyphen is not found to go to the "comma branch"
		if ih == -1:
			ih = ic+1


		# take the one that is closer to the beginning
		if ic < ih:
			# we're parsing out N,
			N = int(tps[0:ic])

			out.append(N)
			tps = tps[ic+1:]

			print "will process single timepoint "+str(N)
		else:
			# we're parsing out N-M,
			N = int(tps[0:ih])
			M = int(tps[ih+1:ic])

			for i in range(N,M+1):
				out.append(i)

			tps = tps[ic+1:]

			print "will process timepoint interval between "+str(N)+" and "+str(M)

	return out


def main():
	try:
		qq = parseOutTimes(timePoints);
		qq.sort()

		# ww = qq.unique()
		ww = []
		for i in range(len(qq)):
			if i == 0 or qq[i-1] != qq[i]:
				ww.append(qq[i])

		print ww
	except ValueError as VE:
		print VE

main()
