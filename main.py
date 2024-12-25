from webapp import create_app

app = create_app()
if __name__=='__main__': #only if we run this it runs the web serve not when imported
    app.run(debug=True)