AP_15_variant

# How to Run

1. Open Terminal in project folder

2. Type  
```
$ cd src
```

3. Change local python version to 3.8.0  
```
$ pyenv local 3.8.0
```

4. Change version of python in poetry environment 
```
$ poetry env use python3
```

5. Add Waitress to poetry 
```
$ poetry add waitress 
```

6. Run App 
```
$ poetry run python waitress_server.py
```
