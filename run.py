from bighak.bighak import Dashboard

dashboard = Dashboard()

try:
    dashboard.start()
except:
    dashboard.shut_down()
