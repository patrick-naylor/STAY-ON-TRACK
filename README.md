<img src="https://github.com/patrick-naylor/STAY-ON-TRACK/blob/main/Images/logo.png?raw=true" alt="drawing" Height="200"/>

Stay On Track is an app that lets you keep track of many aspects of your life.

<img src="https://github.com/patrick-naylor/STAY-ON-TRACK/blob/main/Images/Screenshot%202022-11-04%20at%203.57.56%20PM.png?raw=true" alt="Main data tracking window" Height="500"/>

After you have tracked your life for over 75 days, Stay On Track uses a KMeans clustering model to identify periods similar to the current time period. With Stay On Track you can see when you went a similar time in your life and look at journal entries you made during that period so you can learn from your past!

<img src="https://github.com/patrick-naylor/STAY-ON-TRACK/blob/main/Images/Screenshot%202022-11-04%20at%203.58.30%20PM.jpeg?raw=true" alt="Menu showing similar time periods" Height="200"/>

<img src="https://github.com/patrick-naylor/STAY-ON-TRACK/blob/main/Images/Screenshot%202022-11-04%20at%204.10.39%20PM.jpeg?raw=true" alt="Similar day report" Height="500"/>

Stay On Track uses a sqlite database to store your data which you always have access to. Your data is only saved on your computer, so no information is collected. We do recommend occasionally making backup copies of your data. Your data is stored in personal_data.db.

Give Stay On Track a try by cloning this repository. After downloading the files, run STAY_ON_TRACK.py to initialize your database and log your life. If you would like to see examples of how the app works, you can change the name of file data/sample_data_realistic.db to data/personal_data.db and change setup to be equal to True in util/preferences.py.
