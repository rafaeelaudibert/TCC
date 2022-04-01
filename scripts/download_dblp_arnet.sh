set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
RESET='\033[0m'

TMP_FOLDER="./dblp_arnet_tmp"
DPLP_VERSION="${DBLP_VERSION:-v13}"

case $DBLP_VERSION in
    v4) DBLP_DOWNLOAD_PATH="https://lfs.aminer.cn/lab-datasets/citation/DBLP-citation-Jan8.tar.bz2";;
    v5) DBLP_DOWNLOAD_PATH="https://lfs.aminer.cn/lab-datasets/citation/DBLP-citation-Feb21.tar.bz2";;  
    v6) DBLP_DOWNLOAD_PATH="https://lfs.aminer.cn/lab-datasets/citation/DBLP_citation_Sep_2013.rar";; 
    v7) DBLP_DOWNLOAD_PATH="https://lfs.aminer.cn/lab-datasets/citation/DBLP_citation_2014_May.zip";;  
    v8) DBLP_DOWNLOAD_PATH="https://lfs.aminer.cn/lab-datasets/citation/dblp.v8.tgz";;
    v9) DBLP_DOWNLOAD_PATH="https://lfs.aminer.cn/lab-datasets/citation/dblp.v9.zip";;
    v10) DBLP_DOWNLOAD_PATH="https://lfs.aminer.cn/lab-datasets/citation/dblp.v10.zip";;  
    v11) DBLP_DOWNLOAD_PATH="https://lfs.aminer.cn/misc/dblp.v11.zip";;
    v12) DBLP_DOWNLOAD_PATH="https://originalstatic.aminer.cn/misc/dblp.v12.7z";;  
    v13) DBLP_DOWNLOAD_PATH="https://originalstatic.aminer.cn/misc/dblp.v13.7z";;
    *) echo "${RED}Invalid version! Choose one of {v4..v13}${RESET}" && exit 1
esac

echo "${GREEN}Installing required Python3 libraries...${RESET}"
pip3 install -r requirements.txt

echo "${GREEN}Downloading DBLP ARNET data version ${DBLP_VERSION}...${RESET}"
mkdir -p $TMP_FOLDER
wget -O "$TMP_FOLDER/dblp_raw" $DBLP_DOWNLOAD_PATH

echo "${GREEN}Unzipping it...${RESET}"
dtrx "${TMP_FOLDER}/dblp_raw" --one rename

echo "${GREEN}Renaming file...${RESET}"
mv "./dblp.${DPLP_VERSION}" "./dblp_arnet.${DPLP_VERSION}.json"

# On these versions, we have a broken JSON file with these crazy NumberInt things
if [[ $DBLP_VERSION == "v12" || $DBLP_VERSION == "v13" ]]; then
  echo "${GREEN}Parsing file to a real JSON file...${RESET}"
  sed -i.bak -E 's/NumberInt\(([0-9]+)\)/"\1"/g' "dblp_arnet.${DBLP_VERSION}.json"
fi