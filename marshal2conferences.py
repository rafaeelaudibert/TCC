import sys, marshal
import json
import fire
import re
import pprint
from tqdm import tqdm

PATH_TO_XML = "./dblp.xml"
PATH_TO_MARSHAL = "./dblp.marshal"
DBLP_SIZE = 6_963_277
CATEGORIES = set(
	["article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"]
)
DATA_ITEMS = ["title", "booktitle", "journal", "volume", "year", "ee"]
TDATA_ITEMS = ["key", "tag", "title", "booktitle", "journal", "volume", "year", "ee"]
JDATA_ITEMS = ["key", "title", "journal", "volume", "year", "ee"]
CDATA_ITEMS = ["key", "title", "booktitle", "year", "ee"]

CONFERENCES_FOLDER = './conferences/'
CONFERENCES = [
    {"name": "AAAI", "regex": r"^AAAI$"}, {"name": "IJCAI", "regex": r"^IJCAI( \(\d+\))*$"},
    {"name": "CVPR", "regex": r"^CVPR( \(\d+\))*$"}, {"name": "ECCV", "regex": r"^ECCV( \(\d+\))*$"}, {"name": "ICCV", "regex": r"^ICCV$"},
    {"name": "ICML", "regex": r"^ICML( \(\d+\))*$"}, {"name": "KDD", "regex": r"^KDD$"}, {"name": "NIPS", "regex": r"^((NeurIPS)|(NIPS))$"},
    {"name": "ACL", "regex": r"^ACL( \(\d+\))*$"}, {"name": "EMNL", "regex": r"^EMNLP$"}, {"name": "NAACL", "regex": r"^((HLT\-NAACL)|(NAACL\-HLT))$"},
    {"name": "SIGIR", "regex": r"^SIGIR$"}, {"name": "WWW", "regex": r"^WWW$"},
    {"name": "ASPLOS", "regex": r"^ASPLOS$"}, {"name": "ISCA", "regex": r"^ISCA$"}, {"name": "MICRO", "regex": r"^MICRO$"}, {"name": "HPCA", "regex": r"^HPCA$"},
    {"name": "SIGCOMM", "regex": r"^SIGCOMM$"}, {"name": "NSDI", "regex": r"^NSDI$"},
    {"name": "CCS", "regex": r"^((CCS)|(AsiaCCS))$"}, {"name": "IEEE S&P", "regex": r"^IEEE Symposium on Security and Privacy$"}, {"name": "USINEX Security", "regex": r"^USENIX Security Symposium$"}, {"name": "NDSS", "regex": r"^NDSS$"},
    {"name": "SIGMOD Conference", "regex": r"^SIGMOD Conference$"}, {"name": "VLDB", "regex": r"^VLDB$"}, {"name": "ICDE", "regex": r"^ICDE$"}, {"name": "PODS", "regex": r"^PODS$"},
    {"name": "DAC", "regex": r"^DAC$"}, {"name": "ICCAD", "regex": r"^ICCAD$"},
    {"name": "EMSOFT", "regex": r"^EMSOFT$"}, {"name": "RTAS", "regex": r"^RTAS$"}, {"name": "RTSS", "regex": r"^RTSS$"}, 
    {"name": "HPDC", "regex": r"^HPDC$"}, {"name": "ICS", "regex": r"^ICS$"}, {"name": "SC", "regex": r"^SC$"}, 
    {"name": "MobiCom", "regex": r"^MobiCom$"}, {"name": "MobiSys", "regex": r"^MobiSys$"}, {"name": "SenSys", "regex": r"^SenSys$"}, 
    {"name": "IMC", "regex": r"^((Internet Measurement Conference)|(IMC))$"}, {"name": "SIGMETRICS", "regex": r"^SIGMETRICS$"},
    {"name": "OSDI", "regex": r"^OSDI$"}, {"name": "SOSP", "regex": r"^SOSP$"}, {"name": "EuroSys", "regex": r"^EuroSys$"}, {"name": "FAST", "regex": r"^FAST$"}, {"name": "USENIX ATC", "regex": r"^USENIX Annual Technical Conference$"},
    {"name": "PLDI", "regex": r"^PLDI$"}, {"name": "POPL", "regex": r"^POPL$"}, {"name": "ICFP", "regex": r"^ICFP$"}, {"name": "OOPSLA", "regex": r"^OOPSLA$"},
    {"name": "FSE", "regex": r"^FSE$"}, {"name": "ICSE", "regex": r"^ICSE( \(\d+\))*$"}, {"name": "ASE", "regex": r"^ASE$"}, {"name": "ISSTA", "regex": r"^ISSTA$"},
    {"name": "FOCS", "regex": r"^FOCS$"}, {"name": "SODA", "regex": r"^SODA$"}, {"name": "STOC", "regex": r"^STOC$"},
    {"name": "CRYPTO", "regex": r"^CRYPTO( \(\d+\))*$"}, {"name": "EUROCRYPT", "regex": r"^EUROCRYPT( \(\d+\))*$"},
    {"name": "CAV", "regex": r"^CAV( \(\d+\))*$"}, {"name": "LICS", "regex": r"^LICS$"},
    {"name": "ISMB", "regex": r"^ISMB$"}, {"name": "RECOMB", "regex": r"^((RECOMB)|(RECOMB\-CG))$"},
    {"name": "SIGGRAPH", "regex": r"^SIGGRAPH$"},
    {"name": "EC", "regex": r"^EC$"}, {"name": "WINE", "regex": r"^WINE$"},
    {"name": "CHI", "regex": r"^CHI$"}, {"name": "UbiComp", "regex": r"^UbiComp$"}, {"name": "Pervasive", "regex": r"^Pervasive$"}, {"name": "UIST", "regex": r"^UIST$"},
    {"name": "ICRA", "regex": r"^ICRA( \(\d+\))*$"}, {"name": "IROS", "regex": r"^IROS( \(\d+\))*$"},
    {"name": "VR", "regex": r"^VR$"}
]


def main(min_year=float("-inf"), max_year=float("inf")):
    output = []
    conferences_dict = {conference['name']: {"regex": conference['regex'], 'articles': []} for conference in CONFERENCES}
    pbar_out = tqdm(unit=' entries', unit_scale=True, total=DBLP_SIZE)
    pbar_in = tqdm(unit=' articles', unit_scale=True)
    
    try:
        with open(PATH_TO_MARSHAL, 'rb') as f:
            while True:
                try:
                    info, value = marshal.load(f)

                    # Check if we should insert this
                    if info[1][0] == 'inproceedings' and \
                        float(value['year']) >= min_year and \
                        float(value['year']) <= max_year:

                        # Check, for each author, if it should be added
                        for conference in conferences_dict.keys():
                            if re.compile(conferences_dict[conference]['regex']).search(value['booktitle']):
                                conferences_dict[conference]['articles'].append(value)
                                tqdm.write("[INFO] Added to {}".format(conference))
                        
                        pbar_in.update(1)
                except KeyError as e:
                    pass
                except EOFError as e:
                    break
                pbar_out.update(1)
    finally:
        pbar_out.close()
        pbar_in.close()

    for conference in conferences_dict.keys():
        with open(CONFERENCES_FOLDER + str(conference) + '.json', 'w') as f:
            json.dump(conferences_dict[conference]['articles'], f, indent=2)


# Calling main with fire
if __name__ == "__main__":
    fire.Fire(main)
