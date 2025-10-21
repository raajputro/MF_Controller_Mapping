1. Create a .venv folder: ```py -m venv .venv```
2. Mount on that .venv folder:
      -  windows: ```.\.venv\Scripts\activate```
      -  macOs/Linux: ```source .\.venv\Scripts\activate```
3. Install all dependencies: ```pip install -r requirements.txt```
4. Execute test: ```pytest -s .\feature_controller_map\test_controller_map.py```
