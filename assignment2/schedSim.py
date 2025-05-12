#!/usr/bin/env python3
import re
import argparse

def parse_arg():
	parser = argparse.ArgumentParser(description="Simulate a Scheduler")
	parser.add_argument("job_file", help="Path to the .txt file with the 'jobs'")
	parser.add_argument("-p", "--policy", choices=["FIFO", "SRTN", "RR"], required=True, help="Scheduling Policy")
	parser.add_argument("-q", "--quantum", help="Time for Round Robin ONLY (In this program)")

	return parser.parse_args()

def output_results(avg_turn, avg_wait, p_info, gantt_chart, policy, quantum=None):
	p_info.sort(key= lambda p: (p["process"]))
	gantt_chart = "".join(gantt_chart)
	len_gantt = len(re.findall(r'\[(P\d+|--)\]', gantt_chart))

	if quantum == None:
		print(policy)	
	else:
		print(f"{policy} Q={quantum}")

	print(f"{"Process":<10}{"Arrival":<10}{"Burst":<10}")
	for p in p_info:
		print(f"{"P"+ str(p["process"]):<10}{"T=" + (str(p["arrival"])):<10}{(str(p["burst"])) + "T":<10}")

	print(2 * "\n")

	print(f"{"Process":<10}{"Wait":<10}{"Turn-around":<10}")
	for p in p_info:
		print(f"{"P"+ str(p["process"]):<10}{(str(p["wait"])) + "T":<10}{(str(p["turn-around"])) + "T":<10}")

	print(2 * "\n")

	print(f"average wait:{avg_wait}")
	print(f"average turn around:{avg_turn}")

	print(2 * "\n")

	print("ELABORATION")
	print(gantt_chart)

	# Generate aligned time labels
	labels = ""
	for t in range(0, len_gantt + 1, 4):
		if t % 4 == 0:
			position = t * 4
			labels += " " * (position - len(labels)) + f"T={t}"	
	print(labels)

def read_job(file_path):
	jobs = []
	with open(file_path, 'r') as file:
		for index, line in enumerate(file):	
			# strip: removes leading/trailing whitespaces including \t and \n
			# split: split strings into word tokens. Default with " ". rt list
			job = line.strip().split()	
			if len(job) != 2:	
				continue # Ignore malformed list. Can change handling later...or not
			burst, arrival = map(int, job) # unpacking jobs and casting it to int
			jobs.append({						
				"id": index,
				"arrival": arrival,
				"burst": burst,
				"remaining": burst
			})
	return jobs

def avg_wait_time(jobs):
	num_jobs = 0
	total_wait = 0
	for job in jobs:
		total_wait += job['wait']	
		num_jobs += 1

	return total_wait / num_jobs

def avg_turn_around_time(jobs):
	num_jobs = 0
	total_wait = 0
	for job in jobs:
		total_wait += job['turn-around']	
		num_jobs += 1

	return total_wait / num_jobs

def simulated_fcfs(jobs, args):
	if args.quantum != None:
		print(f"Policy:{args.policy} does not require quantum")
		exit(1)

	time = 0
	fn_jobs = []
	gantt_chart = []

	for job in jobs:			
		start = max(time, job['arrival'])
		end = start + job['burst']

		# Error handling
		if job["burst"] <= 0:
			print("Error: Job needs to have at min. 1 burst")
			exit(1)

		if (job['arrival'] - time) > 0:
			gantt_chart.append((job['arrival'] - time) * "[--]")

		fn_jobs.append({
			"process": job['id'],
			"arrival": job['arrival'],
			"burst": job['burst'],
			"wait": start - job['arrival'],
			"end": end,
			"turn-around": end - job['arrival']
		})
		time = end

		gantt_chart.append((end-start) * f"[P{job['id']}]")	

	# Output
	avg_wait = avg_wait_time(fn_jobs)
	avg_turn = avg_turn_around_time(fn_jobs)
	output_results(avg_turn, avg_wait, fn_jobs, gantt_chart, args.policy)


def simulated_srtn(jobs, args):	
	if args.quantum != None:
		print(f"Policy:{args.policy} does not require Quantum")
		exit(1)

	time = 0
	completed = 0
	total_jobs = len(jobs)
	queue = []
	fn_jobs = []
	gantt_chart = []

	while completed < total_jobs:
		# Split jobs from arrived and not...arrived
		arriving_jobs = [job for job in jobs if job['arrival'] == time]
		queue.extend(arriving_jobs) # Want to keep mutating the list
		jobs = [job for job in jobs if job not in queue]

		if queue:	
			queue.sort(key=lambda job: (job['remaining'], job['id']))
			cur_job = queue[0] # ptr

			# Error handling
			if cur_job["burst"] <= 0:
				print("Error: Job needs to have at min. 1 burst")
				exit(1)

			exist_job = next((fn_job for fn_job in fn_jobs if fn_job['process'] == cur_job['id']), None)
			if exist_job == None:
				fn_jobs.append({
						"process": cur_job['id'],
						"arrival": cur_job['arrival'],
						"burst": cur_job['burst'],
						"wait": 0,
						"end": 0,
						"turn-around": 0
				})	
				exist_job = fn_jobs[-1]
			else:
				pass

			cur_job['remaining'] -= 1
			time += 1

			if cur_job['remaining'] == 0:
				if exist_job != None:
					queue.remove(cur_job)
					completed += 1

					# Final update of the current job		
					exist_job["end"] = time
					exist_job["turn-around"] = exist_job["end"] - exist_job["arrival"]
					exist_job["wait"] = exist_job["turn-around"] - exist_job["burst"]
				else:
					print("Job complete but does not exist in the fn_job?")
					exit(1)	
			gantt_chart.append(f"[P{cur_job["id"]}]")
		else:
			time += 1
			gantt_chart.append("[--]")
	
	# Output
	avg_wait = avg_wait_time(fn_jobs)
	avg_turn = avg_turn_around_time(fn_jobs)
	output_results(avg_turn, avg_wait, fn_jobs, gantt_chart, args.policy)

		
def simulated_rr(jobs, args):
	# Validate quantum
	if args.quantum == None:
		print(f"Quantum missing for {args.policy}")
		exit(1)
	
	quantum = int(args.quantum)
	time = 0
	completed = 0
	total_jobs = len(jobs)
	queue = []
	fn_jobs = []
	gantt_chart = []

	while completed < total_jobs:
		# Split jobs from arrived and not...arrived
		arriving_jobs = [job for job in jobs if job['arrival'] == time]
		arriving_jobs.sort(key= lambda job: (job["remaining"], job['id']))

		queue.extend(arriving_jobs) # Want to keep mutating the list
		jobs = [job for job in jobs if job not in queue]

		if queue:	
			cur_job = queue.pop(0) # grab the first job
			slice_time = min(quantum, cur_job["remaining"])

			# Error handling
			if cur_job["burst"] <= 0:
				print("Error: Job needs to have at min. 1 burst")
				exit(1)

			# Log the first job
			exist_job = next((fn_job for fn_job in fn_jobs if fn_job['process'] == cur_job['id']), None)
			if exist_job == None:
				fn_jobs.append({
						"process": cur_job['id'],
						"arrival": cur_job['arrival'],
						"burst": cur_job['burst'],
						"wait": 0,
						"end": 0,
						"turn-around": 0
				})	
				exist_job = fn_jobs[-1]
			else:
				pass

			for _ in range(quantum):
				time += 1
				cur_job["remaining"] -= 1

				# Spin for new arrives
				arriving_jobs = [job for job in jobs if job['arrival'] == time]
				queue.extend(arriving_jobs)
				jobs = [job for job in jobs if job not in queue]

				gantt_chart.append(f"[P{cur_job["id"]}]")

				if cur_job["remaining"] == 0:
					break	

			if cur_job["remaining"] == 0:
				completed += 1
				# Find the finish job
				exist_job = next((fn_job for fn_job in fn_jobs if fn_job['process'] == cur_job['id']), None)
				exist_job["end"] = time
				exist_job["turn-around"] = exist_job["end"] - exist_job["arrival"]
				exist_job["wait"] = exist_job["turn-around"] - exist_job["burst"]
			else:
				# Not finished
				queue.append(cur_job)
		else:
			time += 1
			gantt_chart.append("[--]")	

	# Output
	avg_wait = avg_wait_time(fn_jobs)
	avg_turn = avg_turn_around_time(fn_jobs)
	output_results(avg_turn, avg_wait, fn_jobs, gantt_chart, args.policy, args.quantum)


# Driver Code
def main():
	args = parse_arg() # Create object to get the stored args from ttys

	jobs = read_job(args.job_file)
	jobs.sort(key=lambda job: (job['arrival'], job['id']))
	if jobs == None:
		print("Error: empty jobs")
		exit(1)

	# Funciton dispatch table
	dispatch = {
		"FIFO": simulated_fcfs,
		"SRTN": simulated_srtn,
		"RR": simulated_rr
	}
	dispatch[args.policy](jobs, args)	


# Is this file being run as main?
if __name__ == "__main__":
	main()

