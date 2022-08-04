import uvicorn

# Run it with unicorn
if __name__ == '__main__':
    uviconn = uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
