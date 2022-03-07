set -e

GREEN='\033[0;32m'
RESET='\033[0m'

echo "${GREEN}Installing required Python3 libraries...${RESET}"
pip3 install -r requirements.txt

echo "${GREEN}Downloading DBLP data...${RESET}"
TMP_FOLDER="./dblp_tmp"
mkdir $TMP_FOLDER
wget https://dblp.uni-trier.de/xml/dblp.xml.gz -P $TMP_FOLDER

echo "${GREEN}Unzipping it...${RESET}"
gunzip -c "${TMP_FOLDER}/dblp.xml.gz" > "${TMP_FOLDER}/dblp.xml"

echo "${GREEN}Converting downloaded XML to JSON...${RESET}"
python3 scripts/xml2json.py "${TMP_FOLDER}/dblp.xml.gz" "${TMP_FOLDER}/dblp.json"
mv "${TMP_FOLDER}/dblp.json" ./dblp.json