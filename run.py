from main import create_app

app = create_app("configs/config.py")
print(app.config)
app.run()
