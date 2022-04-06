## Plotly Dash Exercise With Box Office Data 2017-2019

This is an example plotly dash app I created to explore and play around. The data is from [this kaggle exercise](https://www.kaggle.com/datasets/yjeong5126/box-office-data-20172019). 
The main goal is to practice dashboard making. I also wanted to see if a particular genre was more "lucrative" than another, and how do movie studios compare in terms of revenue/profit. 



## Instructions

To get started, first clone this repo:


```
git clone https://github.com/DolanCoder/exercise_box_office_dashboard.git
cd exercise_box_office_dashboard
```


Create and activate a conda env:
```
conda create -n exercise_box_office_dashboard python=3.8
conda activate exercise_box_office_dashboard
```

Or a venv (make sure your `python3` is 3.8+):
```
python3 -m venv venv
source venv/bin/activate  # for Windows, use venv\Scripts\activate.bat
```

Install all the requirements:

```
pip install -r requirements.txt
```

You can now run the app:
```
python index.py
```

and visit http://127.0.0.1:8050/.

OR You can check out the demo site on heroku (https://boxofficedashboard.herokuapp.com) 
