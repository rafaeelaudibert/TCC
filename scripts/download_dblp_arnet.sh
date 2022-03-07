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

if [[ $- == *i* ]]
    while true; do
        read -p "Do you wish to remove the tmp folder (${TMP_FOLDER})?" yn
        case $yn in
            [Yy]* ) rm -r $TMP_FOLDER; break;;
            [Nn]* ) break;;
            * ) echo "Please answer yes or no.";;
        esac;
    done
fi

