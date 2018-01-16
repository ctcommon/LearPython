import threading

def print_work(cunt):
	for i in range(cunt):
		print 'new thread print:', i

def main():
	t = threading.Thread(target=print_work,args=(10,))
	t.start()
	sum=0
	for i in range(100):
		sum += i
	print 'sum=%s' %sum

if __name__ == "__main__":
	main()
	
