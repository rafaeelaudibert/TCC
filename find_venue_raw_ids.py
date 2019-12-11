import json, sys, tqdm


s_venue = "international conference on learning representations"
iclr = set()
 
fw = open("dblp_arnet/iclr_list.txt", "w")

with open("dblp_arnet/dblp_papers_v11.txt", "r") as fp:
	for line in tqdm.tqdm(fp, total=4107340):
		p = json.loads(line)
		pid = p["id"]
		#print(pid)
		try:
			if s_venue in p["venue"]["raw"].lower():
				fw.write(pid+"\n")
				iclr.add(int(pid))
				fw.flush()
			#end if
		except KeyError:
			pass
			#print("No venue found: ", pid)
fw.close()

s_venue = "arxiv"
arxiv = set()


fw = open("dblp_arnet/"+s_venue+"_list.txt", "w")
nvf = 0

with open("dblp_arnet/dblp_papers_v11.txt", "r") as fp:
	for line in tqdm.tqdm(fp, total=4107340):
		p = json.loads(line)
		pid = p["id"]
		#print(pid)
		try:
			if s_venue in p["venue"]["raw"].lower() and pid not in iclr:
				fw.write(pid+"\n")
				arxiv.add(int(pid))
				fw.flush()
			#end if
		except KeyError:
			nvf += 1
			#print("No venue found: ", pid)
fw.close()




fw = open("dblp_arnet/journal_list.txt", "w")

with open("dblp_arnet/dblp_papers_v11.txt", "r") as fp:
	for line in tqdm.tqdm(fp, total=4107340):
		p = json.loads(line)
		pid = p["id"]
		#print(pid)
		try:
			if "journal" in p["doc_type"].lower() and pid not in arxiv and pid not in iclr:
				fw.write(pid+"\n")
				fw.flush()
			#end if
		except KeyError:
			pass
			#print("No venue found: ", pid)
fw.close()

print(nvf)