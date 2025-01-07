a = Analysis(
    ['gui_app.py'],
    ...
    datas=[
        ('credentials.db', '.'),  
        ('encryption.key', '.'), 
    ],
    ...
)