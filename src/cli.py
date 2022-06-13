import typer
import uvicorn

app = typer.Typer()


@app.command()
def run():
    uvicorn.run('main:app', host='0.0.0.0', port=3001)


if __name__ == '__main__':
    app()
