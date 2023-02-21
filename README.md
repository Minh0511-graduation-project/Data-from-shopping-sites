# DATA FROM SHOPPING SITES

*This repo is for scraping auto search suggestion data from lazada, tiki and shopee*.

## Pre-requisite

- `python3` version: `3.6.9 or above`
- `pip` version: `21.3.1 or above`

## Usage

__NOTE: These steps below are instructions for Linux environment

- Clone the repository and `cd` inside:
  ``` bash
  git clone https://github.com/Minh0511-graduation-project/Data-from-shopping-sites.git
  cd Data-from-shopping-sites
  ```

- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
  
- Run the .py files
  ```bash
  python3 app/tiki/tiki.py
  ```
  ```bash
  python3 app/shopee/shopee.py
  ```
  ```bash
  python3 app/lazada/lazada.py
  ```
  
- Or just run the main file
  ```bash
  python3 main.py
  ```
  
- The results from search suggestions scraping are stored inside the corresponding json files.
- All 3 files are independent of each other, so they can be run in parallel