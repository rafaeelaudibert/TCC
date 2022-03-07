set -e

GREEN='\033[0;32m'
RESET='\033[0m'

DPLP_VERSION="${DBLP_VERSION:-v13}"

echo "${GREEN}Installing required Python3 libraries...${RESET}"
pip3 install -r requirements.txt

echo "${GREEN}Downloading DBLP ARNET data...${RESET}"
TMP_FOLDER="./dblp_arnet_tmp"
mkdir $TMP_FOLDER
wget "https://originalstatic.aminer.cn/misc/dblp.${DPLP_VERSION}.7z" -P $TMP_FOLDER

echo "${GREEN}Unzipping it...${RESET}"
dtrx "${TMP_FOLDER}/dblp.${DPLP_VERSION}.7z" --one rename

echo "${GREEN}Renaming file...${RESET}"
mv "./dblp.${DPLP_VERSION}" "./dblp_arnet.${DPLP_VERSION}.json"

echo "${GREEN}Parsing file to a real JSON file..."
sed -i.bak -E 's/NumberInt\(([0-9]+)\)/"\1"/g' "dblp_arnet.${DBLP_VERSION}.json"